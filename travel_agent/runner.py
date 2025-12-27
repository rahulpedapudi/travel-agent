"""
RUNNER - APPLICATION ENTRY POINT
=================================
WHY A RUNNER:
- ADK agents need a "runner" to actually execute them
- The Runner handles: session management, message routing, event streaming
- This is where you start the application (python -m travel_agent.runner)

KEY CONCEPTS:
1. Runner - Executes the agent and manages the conversation loop
2. SessionService - Stores conversation state (in-memory for now, can upgrade to DB)
3. Session - A single conversation instance with a user

FLOW:
User Input → Runner → Agent → Tool Calls → Response Events → User Output
"""

import asyncio
import os
from pathlib import Path

# Load environment variables from .env file
# This is needed when running directly with python -m (adk run does this automatically)
from dotenv import load_dotenv

# Find the .env file in the travel_agent directory
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import the root agent (supervisor)
from .agents.root_agent import root_agent

# Import state initialization
from .state.session import initialize_session_state


async def run_travel_agent():
    """
    Main async function that runs the travel planning agent.
    
    WHY ASYNC:
    - ADK uses async for non-blocking I/O (agent calls, tool execution)
    - Allows handling multiple users concurrently in production
    - Required by ADK's Runner.run_async() method
    """
    
    # ========================================================
    # 1. CREATE SESSION SERVICE
    # ========================================================
    # InMemorySessionService stores sessions in RAM.
    # Good for: Development, testing, single-server deployments
    # 
    # For production, you'd swap this with:
    # - DatabaseSessionService (PostgreSQL, Firestore)
    # - RedisSessionService (for distributed systems)
    session_service = InMemorySessionService()
    
    # ========================================================
    # 2. CREATE THE RUNNER
    # ========================================================
    # The Runner is the "engine" that executes your agent.
    # It handles:
    # - Routing messages to the right agent
    # - Managing tool execution
    # - Streaming responses back
    runner = Runner(
        agent=root_agent,
        app_name="travel_planner",      # Unique name for your app
        session_service=session_service
    )
    
    # ========================================================
    # 3. CREATE A SESSION
    # ========================================================
    # A session represents one conversation with one user.
    # Each session has:
    # - Unique ID (for tracking)
    # - User ID (for multi-user apps)
    # - State dictionary (persisted across turns)
    session = await session_service.create_session(
        app_name="travel_planner",
        user_id="demo_user"  # In production, use actual user IDs
    )
    
    # Initialize session state with default values
    # This ensures all agents can read/write state without KeyError
    initialize_session_state(session.state)
    
    print("=" * 60)
    print("🌍 TRAVEL PLANNER AGENT")
    print("=" * 60)
    print("I'll help you plan your perfect trip!")
    print("Type 'quit' to exit.\n")
    
    # ========================================================
    # 4. INTERACTIVE CONVERSATION LOOP
    # ========================================================
    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except EOFError:
            # Handle Ctrl+D gracefully
            break
            
        if not user_input:
            continue
            
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye! Safe travels! ✈️")
            break
        
        # ====================================================
        # 5. SEND MESSAGE TO AGENT
        # ====================================================
        # Wrap user input in ADK's Content format.
        # The agent expects messages with a "role" (user/model) 
        # and "parts" (the actual content).
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )
        
        print("\nAgent: ", end="", flush=True)
        
        # ====================================================
        # 6. STREAM AGENT RESPONSE
        # ====================================================
        # run_async yields events as the agent processes.
        # Events include: thinking, tool calls, and final responses.
        # We filter for content events and print the text.
        try:
            async for event in runner.run_async(
                session_id=session.id,
                user_id="demo_user",
                new_message=content
            ):
                # Check if this event has content to display
                if hasattr(event, "content") and event.content:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            print(part.text, end="", flush=True)
            
            print("\n")  # New line after response
            
        except Exception as e:
            # ================================================
            # 7. ERROR HANDLING
            # ================================================
            # Catch any errors during agent execution.
            # In production, you'd log this and potentially retry.
            print(f"\n❌ Error occurred: {str(e)}")
            print("Let me try again. Please repeat your request.\n")


def main():
    """
    Synchronous entry point.
    
    WHY THIS WRAPPER:
    - asyncio.run() is the standard way to run async code in Python
    - Makes the module runnable via: python -m travel_agent.runner
    """
    asyncio.run(run_travel_agent())


# Standard Python idiom for "run this when executed directly"
if __name__ == "__main__":
    main()
