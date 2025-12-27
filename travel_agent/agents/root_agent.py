"""
ROOT AGENT (SUPERVISOR)
=======================
WHY A SUPERVISOR PATTERN:
- Single point of control for the entire workflow
- Can handle errors from any sub-agent centrally
- Makes it easy to add logging, metrics, and debugging

ERROR HANDLING STRATEGY:
- Wrap sub-agent calls conceptually (ADK handles actual execution)
- Use output_key to capture sub-agent results in session state
- Include fallback instructions in the system prompt
"""

from google.adk.agents import Agent
from google.adk.tools import AgentTool

# Import specialized agents (relative imports within package)
from .clarifier import clarifier_agent
from .researcher import researcher_agent  
from .builder import builder_agent


# ============================================================
# WRAP AGENTS AS TOOLS
# ============================================================
# WHY AgentTool:
# - Allows the supervisor to "call" sub-agents like functions
# - ADK handles the context passing and response collection
# - Each tool gets a clear description for the LLM to understand

clarifier_tool = AgentTool(agent=clarifier_agent)
researcher_tool = AgentTool(agent=researcher_agent)
builder_tool = AgentTool(agent=builder_agent)


# ============================================================
# SUPERVISOR AGENT
# ============================================================
root_agent = Agent(
    name="supervisor",
    model="gemini-2.5-flash",
    tools=[clarifier_tool, researcher_tool, builder_tool],
    
    # output_key saves the supervisor's final response to session state
    # This is useful for debugging and for building conversation history
    output_key="app:supervisor_response",
    
    instruction="""
    You are the Supervisor of a Travel Agency. You manage a team of specialized agents.
    
    YOUR ROLE: Orchestrate the workflow, delegate tasks, handle errors gracefully.
    
    AVAILABLE AGENTS:
    1. clarifier_agent - Gathers destination, budget, and travel dates from user
    2. researcher_agent - Searches for flights, hotels, attractions using web search
    3. itinerary_builder - Creates a day-by-day travel plan from research
    
    WORKFLOW PROTOCOL:
    
    STEP 1 - CLARIFICATION:
    - Start by calling `clarifier_agent` with the user's message
    - If the user hasn't provided destination, budget, OR dates: 
      → Pass clarifier's questions back to the user
    - If clarifier confirms all 3 requirements are gathered:
      → Proceed to STEP 2
    
    STEP 2 - RESEARCH:
    - Call `researcher_agent` with the confirmed requirements
    - Wait for it to return hotel options, attractions, and flight info
    - If research is successful:
      → Proceed to STEP 3
    - If research fails (timeout, no results):
      → Tell user: "I'm having trouble finding options. Let me try again."
      → Retry once, then ask user if they want to adjust requirements
    
    STEP 3 - ITINERARY BUILDING:
    - Call `itinerary_builder` with the research summary
    - Present the final day-by-day plan to the user
    
    ERROR HANDLING:
    - If any agent returns an error, acknowledge it to the user
    - Offer to retry or ask for adjusted requirements
    - Never leave the user hanging without a response
    
    IMPORTANT:
    - Always check each agent's output before proceeding
    - You must DELEGATE - do not try to research or build itineraries yourself
    - Be friendly and professional in all communications
    """
)