from google.adk.agents import Agent
from google.adk.tools import google_search

researcher_agent = Agent(
    name="researcher_agent",
    model="gemini-2.5-flash",
    tools=[google_search],  # Gives it access to live web data
    instruction="""
    You are a Travel Researcher Agent.
    Your goal is to gather options for the trip based on the state.
    The state contains: Destination, Budget, Dates.
    You should:
    1. Search for flights (prices, airlines) if not known.
    2. Search for hotel options or find places nearby.
    3. Find top attractions suitable for the budget.
    4. Check weather.
    Use the available tools.
    When you have gathered sufficient raw options (at least 3 hotels, 3 attractions, flight info), output a summary in JSON format inside the text, and say "RESEARCH_COMPLETE".
    The JSON should be a list of dicts, e.g. [{"category": "hotel", "name": "...", "price": "..."}, ...].
    """
)