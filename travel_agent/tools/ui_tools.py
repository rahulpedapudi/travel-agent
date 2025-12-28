"""
UI TOOLS - Render dynamic UI components.
"""

from typing import Optional, List
import json


def render_ui(
    component_type: str,
    props: Optional[dict] = None,
    required: bool = True
) -> str:
    """
    Render a UI component for the user.
    
    Args:
        component_type: One of:
            - "budget_slider": Budget selection (always INR)
            - "date_range_picker": Travel dates
            - "preference_chips": Interests selection
            - "companion_selector": Who's traveling
            - "itinerary_card": Day itinerary with activities
            - "text_input": Single line text input
        
        props: Component-specific properties.
        required: Whether user must interact (default: True)
    
    Returns:
        JSON string with UI component data.
    
    ITINERARY_CARD SCHEMA (Single or Multi-day):
    
    // Multi-day (PREFERRED)
    render_ui("itinerary_card", {
        "days": [
            {
                "day_number": 1,
                "date": "2025-01-15",
                "theme": "Arrival",
                "activities": [...]
            },
            {
                "day_number": 2,
                "date": "2025-01-16",
                "activities": [...]
            }
        ]
    })
    
    // Single-day (Legacy)
    render_ui("itinerary_card", {
        "day_number": 1,
        "date": "2025-01-15",
        "activities": [...]
    })
    """
    if props is None:
        props = {}
    
    # Enforce INR currency for budget_slider
    if component_type == "budget_slider":
        props["currency"] = "INR"

    # Hydrate itinerary from state if requested
    if component_type == "itinerary_card" and props.get("load_from_state"):
        from .state_tools import get_itinerary
        state_data = get_itinerary()
        if state_data and "itinerary" in state_data:
            props["days"] = state_data["itinerary"]
    
    return json.dumps({
        "ui_component": {
            "type": component_type,
            "props": props,
            "required": required
        }
    })


def render_itinerary_card(
    day_number: int,
    date: str,
    activities: List[dict],
    theme: Optional[str] = None
) -> str:
    """
    Render an itinerary card for one day.
    
    Args:
        day_number: Day number (1, 2, 3...)
        date: Date in YYYY-MM-DD format
        activities: List of activity objects with:
            - start_time: "09:00" (24h format, required)
            - duration: "2h" (required)
            - title: "Place name" (required)
            - location: "Address" (required)
            - type: "attraction"|"food"|"transport"|"hotel"|"shopping"|"nature" (required)
            - end_time: "11:00" (optional)
            - description: "Brief description" (optional)
            - notes: ["Tip 1", "Tip 2"] (optional)
            - travel_duration: "20m" (optional)
            - travel_method: "Metro"|"Walk"|"Taxi"|"Bus"|"Train" (optional)
            - travel_note: "Specific directions" (optional)
        theme: Optional day theme like "Cultural Tokyo"
    
    Returns:
        JSON string with itinerary_card UI component.
    
    Example:
        render_itinerary_card(
            day_number=1,
            date="2025-01-15",
            theme="Cultural Tokyo",
            activities=[
                {
                    "start_time": "09:00",
                    "duration": "2h",
                    "title": "Senso-ji Temple",
                    "location": "Asakusa, Tokyo",
                    "type": "attraction",
                    "notes": ["Arrive early to avoid crowds"]
                },
                {
                    "start_time": "12:00",
                    "duration": "1h",
                    "title": "Lunch at Sushi Dai",
                    "location": "Tsukiji Market",
                    "type": "food",
                    "travel_duration": "25m",
                    "travel_method": "Metro"
                }
            ]
        )
    """
    props = {
        "day_number": day_number,
        "date": date,
        "activities": activities
    }
    
    if theme:
        props["theme"] = theme
    
    return json.dumps({
        "ui_component": {
            "type": "itinerary_card",
            "props": props,
            "required": False
        }
    })


def set_chat_title(title: str) -> str:
    """
    Set the title for this chat conversation.
    Call this once you understand what the user wants.
    
    Args:
        title: A short, descriptive title for this chat.
               Examples:
               - "Tokyo Adventure - January 2025"
               - "Weekend in Paris"
               - "Family Beach Vacation"
               - "Budget Backpacking Europe"
    
    Returns:
        Confirmation that the title was set.
    
    Tips for good titles:
    - Include the destination
    - Include the time period if known
    - Keep it under 40 characters
    - Make it descriptive but concise
    """
    return json.dumps({
        "chat_title": title
    })

