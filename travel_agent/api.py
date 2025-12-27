"""
TRAVEL AGENT API
=================
Production-ready FastAPI backend for the travel agent.

Endpoints:
- POST /chat - Send message, get response
- GET /health - Health check

Run locally:
  uvicorn travel_agent.api:app --reload

Deploy to Cloud Run:
  gcloud run deploy travel-agent --source .
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

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(
    title="Travel Agent API",
    description="AI-powered travel planning assistant",
    version="1.0.0"
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

# Session storage (in-memory for now, Redis for production scale)
session_service = InMemorySessionService()

# ADK Runner
runner = Runner(
    agent=root_agent,
    app_name="travel_agent",
    session_service=session_service
)


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class ChatRequest(BaseModel):
    """Chat request from frontend."""
    message: str
    session_id: Optional[str] = None  # Auto-generated if not provided


class ChatResponse(BaseModel):
    """Chat response to frontend."""
    response: str
    session_id: str


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
    return {"status": "healthy", "agent": "travel_agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, _: bool = Depends(verify_api_key)):
    """
    Process a chat message and return agent response.
    
    - Creates a new session if session_id not provided
    - Maintains conversation history within session
    """
    try:
        # Generate or use provided session ID
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
        
        return ChatResponse(response=response_text, session_id=session_id)
        
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
