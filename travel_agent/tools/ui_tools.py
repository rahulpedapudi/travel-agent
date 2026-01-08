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


def render_map(
    markers: List[dict],
    center: Optional[dict] = None,
    zoom: int = 13,
    title: Optional[str] = None
) -> str:
    """
    Render an interactive map with markers for places.
    Call this to show researched locations on a map.
    
    Args:
        markers: List of marker objects, each with:
            - lat: float (required) - Latitude
            - lng: float (required) - Longitude
            - title: str (required) - Place name
            - type: str - "hotel", "attraction", "restaurant", "activity"
            - description: str (optional) - Brief description
            - day: int (optional) - Day number for color coding
        
        center: Map center point {"lat": float, "lng": float}
                If not provided, auto-centers on first marker.
        
        zoom: Map zoom level (1-20, default 13)
        
        title: Optional title for the map
    
    Returns:
        JSON with map_view UI component.
    
    Example:
        render_map([
            {"lat": 35.6586, "lng": 139.7454, "title": "Tokyo Tower", "type": "attraction"},
            {"lat": 35.6762, "lng": 139.6503, "title": "Park Hyatt Tokyo", "type": "hotel"},
            {"lat": 35.7101, "lng": 139.8107, "title": "Senso-ji Temple", "type": "attraction"}
        ], title="Tokyo Trip Locations")
    """
    # Auto-center on first marker if no center provided
    if not center and markers:
        center = {"lat": markers[0]["lat"], "lng": markers[0]["lng"]}
    elif not center:
        center = {"lat": 0, "lng": 0}
    
    return json.dumps({
        "ui_component": {
            "type": "map_view",
            "props": {
                "center": center,
                "zoom": zoom,
                "markers": markers,
                "title": title
            },
            "required": False
        }
    })


def render_route(
    origin: dict,
    destination: dict,
    waypoints: Optional[List[dict]] = None,
    travel_mode: str = "TRANSIT",
    day_number: Optional[int] = None
) -> str:
    """
    Render a map with a route/path between locations.
    Call this to show the day's journey with directions.
    
    Args:
        origin: Start point {"lat": float, "lng": float, "title": str}
        
        destination: End point {"lat": float, "lng": float, "title": str}
        
        waypoints: List of intermediate stops, each with:
            - lat: float (required)
            - lng: float (required)
            - title: str (required)
            - order: int (required) - Stop order (1, 2, 3...)
            - arrival_time: str (optional) - e.g., "10:30"
        
        travel_mode: One of "DRIVING", "WALKING", "TRANSIT", "BICYCLING"
                     Default is "TRANSIT"
        
        day_number: Day number for labeling (optional)
    
    Returns:
        JSON with route_view UI component.
    
    Example:
        render_route(
            origin={"lat": 35.6762, "lng": 139.6503, "title": "Hotel"},
            destination={"lat": 35.7101, "lng": 139.8107, "title": "Senso-ji Temple"},
            waypoints=[
                {"lat": 35.6895, "lng": 139.6917, "title": "Harajuku", "order": 1, "arrival_time": "10:00"},
                {"lat": 35.6586, "lng": 139.7454, "title": "Tokyo Tower", "order": 2, "arrival_time": "12:00"}
            ],
            travel_mode="TRANSIT",
            day_number=1
        )
    """
    return json.dumps({
        "ui_component": {
            "type": "route_view",
            "props": {
                "origin": origin,
                "destination": destination,
                "waypoints": waypoints or [],
                "travel_mode": travel_mode,
                "day_number": day_number,
                "show_traffic": False
            },
            "required": False
        }
    })
