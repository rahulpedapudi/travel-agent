"""
TRAVEL AGENT API
=================
Production-ready FastAPI backend with Server-Driven UI.

Endpoints:
- POST /chat - Send message, get response with optional UI component
- POST /chat/stream - Stream response via Server-Sent Events (SSE)
- GET /health - Health check
- DELETE /session/{id} - Clear session
- GET /ui-schema - Get all UI component schemas

Run locally:
  uvicorn travel_agent.api:app --reload
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .context import session_context
from typing import Optional
import uuid
import logging
import json

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agents import root_agent
from .config import get_settings, Settings
from .schemas import (
    ChatResponse,
    UIComponent,
    UIType,
    BudgetSliderProps,
    DateRangePickerProps,
    PreferenceChipsProps,
    CompanionSelectorProps,
    ItineraryCardProps,
    RatingFeedbackProps,
    RatingFeedbackProps,
    QuickActionsProps,
)
from .workflow_schemas import WorkflowPlan, WorkflowTask, TaskStatus, WorkflowPlan
from .firebase_auth import init_firebase, get_current_user

# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

limiter = Limiter(key_func=get_remote_address)

# Structured Logging
from .logging import get_logger, RequestLogger
logger = get_logger("api")

# --- MONKEY PATCH FOR ADK LIBRARY BUGS ---
# 1. Fixes TypeError: 'NoneType' object is not iterable in agent_tool.py
# 2. Handles Gemini 503 "model overloaded" errors with retry
import asyncio

try:
    from google.adk.tools import agent_tool
    from google.genai import errors as genai_errors
    original_run_async = agent_tool.AgentTool.run_async

    async def patched_run_async(self, *args, **kwargs):
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries + 1):
            try:
                return await original_run_async(self, *args, **kwargs)
            except TypeError as e:
                if "'NoneType' object is not iterable" in str(e):
                    logger.warning(f"Caught ADK library bug in AgentTool ({self.name}): {e}. Returning empty success.")
                    return {"output": "Agent completed but returned no content."}
                raise e
            except genai_errors.ServerError as e:
                # Handle Gemini 503 "model overloaded" errors
                if "503" in str(e) or "overloaded" in str(e).lower():
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                        logger.warning(f"Gemini API overloaded (attempt {attempt + 1}/{max_retries + 1}). Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.error(f"Gemini API overloaded after {max_retries + 1} attempts. Giving up.")
                        return {"output": "The AI service is currently busy. Please try again in a moment.", "error": True}
                raise e
            except Exception as e:
                # Log unexpected errors but don't retry them
                logger.error(f"Unexpected error in AgentTool ({self.name}): {e}")
                raise e

    agent_tool.AgentTool.run_async = patched_run_async
    logger.info("Applied AgentTool monkey patch for stability and retry logic")
except ImportError:
    logger.warning("Could not apply AgentTool monkey patch - library not found")
# ----------------------------------------


# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(
    title="Travel Agent API",
    description="AI-powered travel planning assistant with Server-Driven UI",
    version="2.0.0"
)

# Rate Limiting setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS for React frontend
settings = get_settings()
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage
session_service = InMemorySessionService()

# Redis state service for session ownership tracking
from .redis_state import state_service as redis_state

# Simple in-memory storage for chat titles (session_id -> title)
# In production, this should be in Redis or database
SESSION_TITLES = {}

# ADK Runner
runner = Runner(
    agent=root_agent,
    app_name="travel_agent",
    session_service=session_service
)

# Initialize Firebase (optional - only if FIREBASE_SERVICE_ACCOUNT_KEY is set)
try:
    init_firebase()
    logger.info("Firebase Authentication initialized")
except Exception as e:
    logger.warning(f"Firebase not initialized (auth disabled): {e}")

# Log the LLM model being used
from .config import LLM_MODEL
logger.info(f"LLM Model: {LLM_MODEL}")


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):
    """Chat request from frontend."""
    message: str
    session_id: Optional[str] = None


# ============================================================
# AUTH MIDDLEWARE
# ============================================================

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key if configured."""
    settings = get_settings()
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


# ============================================================
# ENDPOINTS
# ============================================================

def extract_ui_from_tool_response(text: str) -> Optional[dict]:
    """
    Extract UI component from render_ui tool response.
    The tool returns JSON with ui_component key.
    """
    try:
        if text and "ui_component" in text:
            data = json.loads(text)
            if "ui_component" in data:
                return data["ui_component"]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def extract_chat_title(text: str) -> Optional[str]:
    """
    Extract chat title from set_chat_title tool response.
    """
    try:
        if text and "chat_title" in text:
            data = json.loads(text)
            return data.get("chat_title")
    except (json.JSONDecodeError, KeyError):
        pass
    return None

@app.get("/health")
async def health_check():
    """Health check for Cloud Run."""
    return {"status": "healthy", "agent": "travel_agent", "version": "2.0.0"}


@app.get("/ui-schema")
async def get_ui_schema():
    """
    Get all available UI component types and their props.
    Useful for frontend development and documentation.
    """
    return {
        "components": {
            "budget_slider": BudgetSliderProps.model_json_schema(),
            "date_range_picker": DateRangePickerProps.model_json_schema(),
            "preference_chips": PreferenceChipsProps.model_json_schema(),
            "companion_selector": CompanionSelectorProps.model_json_schema(),
            "itinerary_card": ItineraryCardProps.model_json_schema(),
            "rating_feedback": RatingFeedbackProps.model_json_schema(),
            "quick_actions": QuickActionsProps.model_json_schema(),
        },
        "types": [t.value for t in UIType]
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user: dict = Depends(get_current_user)):
    """
    Process a chat message and return agent response with optional UI.
    
    Response includes:
    - response: Text from the agent
    - session_id: For maintaining conversation
    - ui: Optional UI component to render (slider, picker, etc.)
    """
    try:
        # Use Firebase user ID for session (ensures each user has their own conversation)
        user_id = user["uid"]
        session_id = request.session_id or user_id
        
        # Get or create session
        session = await session_service.get_session(
            app_name="travel_agent",
            user_id=user_id,
            session_id=session_id
        )
        
        if not session:
            session = await session_service.create_session(
                app_name="travel_agent",
                user_id=user_id,
                session_id=session_id
            )
            logger.info(f"Created new session for user {user_id}: {session_id}")
        
        # Set context for state tools (CRITICAL for preference persistence)
        session_context.set(session_id)
        
        # Convert message to ADK format
        content = types.Content(
            role="user",
            parts=[types.Part(text=request.message)]
        )
        
        # Run agent and collect response + UI from tool calls
        response_text = ""
        ui_data = None
        
        async for event in runner.run_async(
            session_id=session.id,
            user_id=session_id,
            new_message=content
        ):
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    # Collect text response
                    if hasattr(part, "text") and part.text:
                        response_text += part.text
                    # Check for render_ui tool response
                    if hasattr(part, "function_response") and part.function_response:
                        fn_resp = part.function_response
                        if hasattr(fn_resp, "name") and fn_resp.name == "render_ui":
                            ui_data = extract_ui_from_tool_response(
                                fn_resp.response.get("result", "") if fn_resp.response else ""
                            )
        
        if not response_text:
            response_text = "I'm having trouble processing that. Could you try rephrasing?"
        
        # Build UI component from tool call data
        ui_component = None
        if ui_data:
            ui_component = UIComponent(
                type=UIType(ui_data["type"]),
                props=ui_data.get("props", {}),
                required=ui_data.get("required", True)
            )
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            ui=ui_component
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")


@app.post("/session")
async def create_session(user: dict = Depends(get_current_user)):
    """
    Create a new chat session for the authenticated user.
    Returns the new session_id to use for /chat requests.
    """
    user_id = user["uid"]
    session_id = str(uuid.uuid4())
    
    await session_service.create_session(
        app_name="travel_agent",
        user_id=user_id,
        session_id=session_id
    )
    logger.info(f"Created new session for user {user_id}: {session_id}")
    
    return {
        "session_id": session_id,
        "message": "New chat created"
    }


@app.delete("/session/{session_id}")
async def delete_session(session_id: str, user: dict = Depends(get_current_user)):
    """Clear a session (delete conversation history)."""
    try:
        user_id = user["uid"]
        await session_service.delete_session(
            app_name="travel_agent",
            user_id=user_id,
            session_id=session_id
        )
        return {"message": "Session deleted"}
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        return {"message": "Session may not exist"}

@app.get("/session/{session_id}")
async def get_session_history(
    session_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get session history and current state.
    Used for restoring chat context on page load.
    """
    try:
        user_id = user["uid"]
        
        # SECURITY: Verify session ownership
        owner = redis_state.get_owner(session_id)
        if owner and owner != user_id:
            raise HTTPException(status_code=403, detail="Access denied: You don't own this session")
        
        # Set context
        session_context.set(session_id)
        
        # Get session from ADK (InMemory)
        session = await session_service.get_session(
            app_name="travel_agent",
            user_id=user_id,
            session_id=session_id
        )
        
        # Get structured trip state
        from .tools.state_tools import _get_state
        state = _get_state(session_id)
        
        # Serialize history
        history = []
        if hasattr(session, "history"):
            for msg in session.history:
                # Basic serialization for ADK messages
                role = getattr(msg, "role", "unknown")
                content = ""
                
                # ADK messages often have 'parts'
                if hasattr(msg, "parts"):
                    # Extract text from parts
                    texts = []
                    for part in msg.parts:
                        if hasattr(part, "text"):
                            texts.append(part.text)
                        else:
                            texts.append(str(part))
                    content = "\n".join(texts)
                elif hasattr(msg, "content"):
                    content = str(msg.content)
                
                # Filter out system messages or tool calls if desired
                # For now, include everything that has text
                if content:
                    history.append({
                        "role": role,
                        "content": content,
                        # Add timestamp if available? ADK usually doesn't track it on msg object
                    })
        
        return {
            "session_id": session_id,
            "messages": history,
            "trip_state": state
        }
        
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/chat/stream")
@limiter.limit("30/minute")  # Rate limit: 30 requests per minute per IP
async def chat_stream(request: Request, body: ChatRequest, user: dict = Depends(get_current_user)):
    """
    Stream chat response using Server-Sent Events (SSE).
    
    Event types:
    - plan: Initial task plan
    - task_start: Sub-agent started
    - task_complete: Sub-agent finished
    - thinking: Current detailed action
    - token: Partial text chunk
    - done: Final event with session_id and UI component
    - error: Error message
    """

    async def generate():
        # Use Firebase user ID for session (ensures each user has their own conversation)
        user_id = user["uid"]
        # Generate unique session_id if not provided (for new chats)
        session_id = body.session_id or str(uuid.uuid4())
        
        # Initialize request logger
        req_log = RequestLogger(
            session_id=session_id,
            user_id=user_id,
            endpoint="/chat/stream"
        )
        
        try:
            req_log.log.info(
                "request_started",
                session_id=session_id,
                user_id=user_id,
                message_length=len(body.message),
            )
            import time
            start_time = time.time()
            
            # Set context for state tools
            session_context.set(session_id)
            
            # Get or create session
            session = await session_service.get_session(
                app_name="travel_agent",
                user_id=user_id,
                session_id=session_id
            )
            
            if not session:
                session = await session_service.create_session(
                    app_name="travel_agent",
                    user_id=user_id,
                    session_id=session_id
                )
                # Record session ownership for security
                redis_state.set_owner(session_id, user_id)
                logger.info("session_created", user_id=user_id, session_id=session_id)
            
            
            # Convert message to ADK format
            content = types.Content(
                role="user",
                parts=[types.Part(text=body.message)]
            )
            
            # Stream tokens and capture UI from tool calls
            full_response = ""
            ui_data = None
            chat_title = None  # Will be set by LLM via set_chat_title tool
            
            # Agent to Task mapping
            AGENT_TO_TASK = {
                "clarifier_agent": ("clarify", "Gathering trip preferences"),
                "researcher_agent": ("research", "Researching destinations"),
                "activity_agent": ("activities", "Finding activities"),
                "builder_agent": ("build", "Building itinerary"),
                "refinement_agent": ("refine", "Refining plan"),
            }
            
            # Plan is sent only when real work begins (not during clarification)
            plan_sent = False
            EXECUTION_AGENTS = ["researcher_agent", "activity_agent", "builder_agent", "refinement_agent"]
            
            active_task_id = None
            
            async for event in runner.run_async(
                session_id=session.id,
                user_id=user_id,
                new_message=content
            ):
                if hasattr(event, "content") and event.content and event.content.parts:
                    for part in event.content.parts:
                        # Stream text chunks
                        if hasattr(part, "text") and part.text:
                            full_response += part.text
                            yield f"data: {json.dumps({'type': 'token', 'text': part.text})}\n\n"
                        
                        # Emit thinking/task events when agent calls a tool
                        if hasattr(part, "function_call") and part.function_call:
                            fn_call = part.function_call
                            tool_name = getattr(fn_call, "name", "processing")
                            
                            # EMIT: Plan (only once, when real work begins)
                            # Send plan when first execution agent is called (not clarifier)
                            if not plan_sent and tool_name in EXECUTION_AGENTS:
                                plan_sent = True
                                tasks = [
                                    WorkflowTask(id="research", label="Researching destinations", status=TaskStatus.PENDING, agent="researcher_agent"),
                                    WorkflowTask(id="activities", label="Finding activities", status=TaskStatus.PENDING, agent="activity_agent"),
                                    WorkflowTask(id="build", label="Building itinerary", status=TaskStatus.PENDING, agent="builder_agent"),
                                ]
                                yield f"data: {json.dumps({'type': 'plan', 'tasks': [t.model_dump() for t in tasks]})}\n\n"
                            
                            # EMIT: Task Start
                            # Check if this tool is a sub-agent
                            if tool_name in AGENT_TO_TASK:
                                task_id, label = AGENT_TO_TASK[tool_name]
                                active_task_id = task_id
                                yield f"data: {json.dumps({'type': 'task_start', 'taskId': task_id, 'label': label})}\n\n"
                            
                            # Map tool names to user-friendly messages
                            thinking_messages = {
                                "clarifier_agent": "Understanding your preferences...",
                                "researcher_agent": "Researching destinations...",
                                "activity_agent": "Finding activities...",
                                "builder_agent": "Building your itinerary...",
                                "refinement_agent": "Refining the plan...",
                                "render_ui": "Preparing input...",
                                "find_places_nearby": "Searching for places...",
                                "compute_route_matrix": "Calculating routes...",
                                "search_travel_info": "Searching travel info...",
                            }
                            message = thinking_messages.get(tool_name, f"Working on it...")
                            yield f"data: {json.dumps({'type': 'thinking', 'message': message, 'tool': tool_name})}\n\n"
                            
                            # Log tool call
                            req_log.log_tool_call(tool_name)
                        
                        # 3. EMIT: Task Complete
                        # When we get a function response from a sub-agent
                        if hasattr(part, "function_response") and part.function_response:
                            fn_resp = part.function_response
                            if active_task_id and hasattr(fn_resp, "name") and fn_resp.name in AGENT_TO_TASK:
                                yield f"data: {json.dumps({'type': 'task_complete', 'taskId': active_task_id})}\n\n"
                                active_task_id = None

                            # Capture render_ui tool response for UI component
                            if hasattr(fn_resp, "name") and fn_resp.name == "render_ui":
                                ui_data = extract_ui_from_tool_response(
                                    fn_resp.response.get("result", "") if fn_resp.response else ""
                                )
                            
                            # Capture set_chat_title tool response
                            if hasattr(fn_resp, "name") and fn_resp.name == "set_chat_title":
                                title = extract_chat_title(
                                    fn_resp.response.get("result", "") if fn_resp.response else ""
                                )
                                if title:
                                    chat_title = title
                                    # Persist title
                                    SESSION_TITLES[session_id] = title
            
            # Build UI component from tool call data
            ui_component = None
            if ui_data:
                ui_component = {
                    "type": ui_data["type"],
                    "props": ui_data.get("props", {}),
                    "required": ui_data.get("required", True)
                }
            
            # FALLBACK: If no UI was captured but state has itinerary, create one
            if not ui_component:
                try:
                    from .tools.state_tools import get_itinerary
                    itinerary_data = get_itinerary()
                    if itinerary_data and itinerary_data.get("itinerary") and isinstance(itinerary_data["itinerary"], list) and len(itinerary_data["itinerary"]) > 0:
                        ui_component = {
                            "type": "itinerary_card",
                            "props": {"days": itinerary_data["itinerary"]},
                            "required": True
                        }
                        logger.info(f"Created itinerary UI from state: {len(itinerary_data['itinerary'])} days")
                except Exception as e:
                    logger.warning(f"Failed to load itinerary from state: {e}")
            
            # Retrieve persisted title if not set in this turn
            if not chat_title and session_id in SESSION_TITLES:
                chat_title = SESSION_TITLES[session_id]
            
            done_data = {
                "type": "done",
                "session_id": session_id,
                "chat_title": chat_title,
                "ui": ui_component
            }
            yield f"data: {json.dumps(done_data)}\n\n"
            
            # Log request completion
            duration_ms = (time.time() - start_time) * 1000
            req_log.log.info(
                "request_completed",
                session_id=session_id,
                duration_ms=round(duration_ms, 2),
                tool_calls=req_log.tool_calls,
                tool_count=len(req_log.tool_calls),
                response_length=len(full_response),
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            req_log.log.error(
                "request_failed",
                session_id=session_id if 'session_id' in locals() else "unknown",
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__,
                error_message=str(e),
                tool_calls=req_log.tool_calls if 'req_log' in locals() else [],
            )
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "travel_agent.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )
