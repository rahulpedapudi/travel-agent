"""
REFINEMENT AGENT
=================
Handles mid-plan changes and adaptive refinements.

EXAMPLES:
- "Swap the beach day for shopping"
- "Add kid-friendly spots"
- "Make it more budget-friendly"
- "Remove the museum, add more food tours"

KEY CAPABILITY:
Only re-runs affected parts of the itinerary, not the entire plan.
"""

from google.adk.agents import Agent
from ..tools import find_places_nearby, get_calendar_dates


def apply_refinement(
    current_itinerary: dict,
    change_type: str,
    change_details: str
) -> dict:
    """
    Apply a refinement to the existing itinerary.
    
    Args:
        current_itinerary: The current day-by-day plan
        change_type: Type of change - "swap", "add", "remove", "adjust"
        change_details: What to change (e.g., "beach -> shopping", "add kid-friendly")
    
    Returns:
        Instructions for which parts need to be regenerated
    """
    change_type_lower = change_type.lower()
    
    if "swap" in change_type_lower:
        # Parse "X for Y" or "X with Y"
        parts = change_details.lower().replace(" for ", "|").replace(" with ", "|").split("|")
        if len(parts) == 2:
            return {
                "action": "swap",
                "remove": parts[0].strip(),
                "add": parts[1].strip(),
                "affected_days": "detect_from_itinerary",
                "regenerate": True
            }
    
    elif "add" in change_type_lower:
        return {
            "action": "add",
            "filter": change_details,  # e.g., "kid-friendly spots"
            "affected_days": "all",
            "regenerate": False  # Just append activities
        }
    
    elif "remove" in change_type_lower:
        return {
            "action": "remove",
            "target": change_details,
            "affected_days": "detect_from_itinerary",
            "regenerate": False
        }
    
    elif "adjust" in change_type_lower:
        return {
            "action": "adjust",
            "adjustment": change_details,
            "affected_days": "all",
            "regenerate": True
        }
    
    return {
        "action": "unknown",
        "original_request": f"{change_type}: {change_details}",
        "suggestion": "Please clarify: do you want to swap, add, remove, or adjust something?"
    }


refinement_agent = Agent(
    name="refinement_agent",
    model="gemini-2.5-flash",
    tools=[find_places_nearby, apply_refinement],
    
    instruction="""
    You are a Plan Refinement Agent.
    Your job is to modify existing itineraries based on user feedback.
    
    AVAILABLE TOOLS:
    - find_places_nearby: Find new activities/places
    - apply_refinement: Determine what parts of the plan to change
    
    TYPES OF REFINEMENTS:
    
    1. SWAP: Replace one thing with another
       User: "Swap the beach day for shopping"
       Action: Find shopping activities, replace beach activities
    
    2. ADD: Insert new activities
       User: "Add kid-friendly spots"
       Action: Find kid-friendly places, insert into existing days
    
    3. REMOVE: Take something out
       User: "Remove the museum visits"
       Action: Remove museum from itinerary, adjust schedule
    
    4. ADJUST: Modify the style/theme
       User: "Make it more budget-friendly"
       Action: Replace expensive options with cheaper alternatives
    
    YOUR PROCESS:
    
    1. Parse the user's refinement request
    2. Call apply_refinement to understand what action to take
    3. If needed, call find_places_nearby to get replacement activities
    4. Provide updated itinerary with only the changed parts highlighted
    
    OUTPUT FORMAT:
    ```
    REFINEMENT APPLIED:
    - Changed: [what was changed]
    - Reason: [why/how it matches user request]
    
    Updated Day X:
    - [new activities]
    ```
    
    IMPORTANT:
    - Only modify what the user asked for
    - Keep the rest of the itinerary intact
    - Highlight what changed so user can see the difference
    - If unsure what to change, ask for clarification
    """
)
