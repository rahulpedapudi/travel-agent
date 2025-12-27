"""
REFINEMENT AGENT
=================
Handles mid-plan changes like swapping activities.
"""

from google.adk.agents import Agent
from ..tools import find_places_nearby, get_calendar_dates


def apply_refinement(
    current_itinerary: dict,
    change_type: str,
    change_details: str
) -> dict:
    """Determine what changes to make to the itinerary."""
    change_type_lower = change_type.lower()
    
    if "swap" in change_type_lower:
        parts = change_details.lower().replace(" for ", "|").replace(" with ", "|").split("|")
        if len(parts) == 2:
            return {"action": "swap", "remove": parts[0].strip(), "add": parts[1].strip()}
    elif "add" in change_type_lower:
        return {"action": "add", "filter": change_details}
    elif "remove" in change_type_lower:
        return {"action": "remove", "target": change_details}
    
    return {"action": "clarify", "request": change_details}


refinement_agent = Agent(
    name="refinement_agent",
    model="gemini-2.5-flash",
    tools=[find_places_nearby, apply_refinement],
    
    instruction="""
    You modify existing itineraries based on user requests.
    
    LANGUAGE RULES - VERY IMPORTANT:
    - NEVER mention "refinement", "tools", "processing"
    - NEVER say "applying your changes" or "modification complete"
    - Just make the change and show the result naturally
    
    ❌ DON'T SAY: "I've applied the refinement to your itinerary"
    ✅ SAY: "Done! I swapped out the museum for some shopping time"
    
    ❌ DON'T SAY: "Processing your request to add kid-friendly activities"
    ✅ SAY: "Added some fun spots the kids will love!"
    
    CHANGES YOU HANDLE:
    - "Swap X for Y" → Replace one activity with another
    - "Add more X" → Find and add activities of that type
    - "Remove X" → Take it out of the plan
    - "Make it more budget-friendly" → Suggest cheaper alternatives
    
    OUTPUT:
    Briefly confirm what you changed, then show the updated part of the itinerary.
    
    Example:
    "Got it! I swapped the art museum for some street food exploring. Here's your updated Day 2:
    
    - 2:00 PM - Street Food Tour in [Area]
    - 4:00 PM - [Next activity]
    ..."
    
    Keep it casual and friendly!
    """
)
