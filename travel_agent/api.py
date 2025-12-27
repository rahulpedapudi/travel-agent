"""
TRAVEL AGENT API
=================
Production-ready FastAPI backend with Server-Driven UI.

Endpoints:
- POST /chat - Send message, get response with optional UI component
- GET /health - Health check
- DELETE /session/{id} - Clear session
- GET /ui-schema - Get all UI component schemas

Run locally:
  uvicorn travel_agent.api:app --reload
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import logging

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agents import root_agent
from .config import get_settings, Settings
from .schemas import (
    ChatResponse,
    UIComponent,
    UIType,
    detect_ui_component,
    BudgetSliderProps,
    DateRangePickerProps,
    PreferenceChipsProps,
    CompanionSelectorProps,
    ItineraryCardProps,
    RatingFeedbackProps,
    QuickActionsProps,
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(
    title="Travel Agent API",
    description="AI-powered travel planning assistant with Server-Driven UI",
    version="2.0.0"
)

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

# ADK Runner
runner = Runner(
    agent=root_agent,
    app_name="travel_agent",
    session_service=session_service
)


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
async def chat(request: ChatRequest, _: bool = Depends(verify_api_key)):
    """
    Process a chat message and return agent response with optional UI.
    
    Response includes:
    - response: Text from the agent
    - session_id: For maintaining conversation
    - ui: Optional UI component to render (slider, picker, etc.)
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get or create session
        session = await session_service.get_session(
            app_name="travel_agent",
            user_id=session_id,
            session_id=session_id
        )
        
        if not session:
            session = await session_service.create_session(
                app_name="travel_agent",
                user_id=session_id,
                session_id=session_id
            )
            logger.info(f"Created new session: {session_id}")
        
        # Convert message to ADK format
        content = types.Content(
            role="user",
            parts=[types.Part(text=request.message)]
        )
        
        # Run agent and collect response
        response_text = ""
        async for event in runner.run_async(
            session_id=session.id,
            user_id=session_id,
            new_message=content
        ):
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_text += part.text
        
        if not response_text:
            response_text = "I'm having trouble processing that. Could you try rephrasing?"
        
        # Detect UI component based on response text
        ui_component = detect_ui_component(response_text)
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            ui=ui_component
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")


@app.delete("/session/{session_id}")
async def delete_session(session_id: str, _: bool = Depends(verify_api_key)):
    """Clear a session (start fresh conversation)."""
    try:
        await session_service.delete_session(
            app_name="travel_agent",
            user_id=session_id,
            session_id=session_id
        )
        return {"message": "Session cleared"}
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        return {"message": "Session may not exist"}


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
