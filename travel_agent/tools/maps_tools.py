"""
MAPS TOOLS - Google Maps Routes API
====================================
Route optimization and validation tools for the Builder Agent.

USED BY: Itinerary Builder Agent

KEY TOOL: compute_route_matrix
- Takes N places and returns travel times between ALL pairs
- Essential for sorting activities efficiently (nearest-neighbor)

NOTE: Using synchronous requests for Google AI API compatibility.
"""

from google.adk.tools import FunctionTool
from typing import List
import os

# Use requests (sync) for compatibility
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def compute_route_matrix(
    locations: List[str],
    travel_mode: str = "DRIVE"
) -> dict:
    """
    Calculate travel times between ALL pairs of locations.
    Essential for optimizing itinerary order.
    
    Args:
        locations: List of place names (e.g., ["Tokyo Tower", "Senso-ji Temple"])
        travel_mode: Mode of transport - "DRIVE", "WALK", "TRANSIT"
    
    Returns:
        Matrix with travel duration between each location pair
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        # Return estimated times as fallback
        return {
            "error": "GOOGLE_MAPS_API_KEY not set",
            "locations": locations,
            "suggestion": "Estimate 15-30 min between nearby attractions, 45-60 min across city"
        }
    
    if not HAS_REQUESTS:
        return {
            "error": "requests library not installed",
            "locations": locations,
            "suggestion": "Estimate 20 min between locations in same area"
        }
    
    if len(locations) < 2:
        return {
            "error": "Need at least 2 locations",
            "locations": locations
        }
    
    url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
    waypoints = [{"waypoint": {"address": loc}} for loc in locations]
    
    try:
        response = requests.post(
            url,
            headers={
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters"
            },
            json={
                "origins": waypoints,
                "destinations": waypoints,
                "travelMode": travel_mode.upper()
            },
            timeout=20
        )
        
        if response.status_code != 200:
            return {
                "error": f"API error: {response.status_code}",
                "locations": locations,
                "suggestion": "Estimate 20 min between nearby locations"
            }
        
        data = response.json()
        if not isinstance(data, list):
            data = [data]
            
    except Exception as e:
        return {
            "error": str(e)[:100],
            "locations": locations,
            "suggestion": "Estimate 20 min between nearby locations"
        }
    
    # Build readable matrix
    matrix = []
    for route in data:
        duration = route.get("duration", "0s")
        if isinstance(duration, str) and duration.endswith("s"):
            seconds = int(duration[:-1])
            minutes = seconds // 60
            duration_str = f"{minutes} min"
        else:
            duration_str = str(duration)
        
        matrix.append({
            "from": locations[route.get("originIndex", 0)],
            "to": locations[route.get("destinationIndex", 0)],
            "duration": duration_str,
            "distance_km": round(route.get("distanceMeters", 0) / 1000, 1)
        })
    
    return {
        "locations": locations,
        "travel_mode": travel_mode,
        "matrix": matrix
    }


def validate_open_hours(
    place_name: str,
    proposed_time: str,
    day_of_week: str
) -> dict:
    """
    Check if a place is likely open at the proposed time.
    
    Args:
        place_name: Name or type (e.g., "Tokyo Museum", "restaurant")
        proposed_time: Time in HH:MM format (e.g., "14:00")
        day_of_week: Day name (e.g., "Monday", "Saturday")
    
    Returns:
        Whether the place is likely open
    """
    # Typical hours by place type
    typical_hours = {
        "museum": {"open": "09:00", "close": "17:00", "closed": ["Monday"]},
        "temple": {"open": "06:00", "close": "17:00", "closed": []},
        "restaurant": {"open": "11:00", "close": "22:00", "closed": []},
        "cafe": {"open": "08:00", "close": "20:00", "closed": []},
        "bar": {"open": "18:00", "close": "02:00", "closed": []},
        "mall": {"open": "10:00", "close": "21:00", "closed": []},
        "market": {"open": "05:00", "close": "14:00", "closed": ["Sunday"]},
    }
    
    # Detect place type
    place_lower = place_name.lower()
    detected_type = None
    for ptype in typical_hours:
        if ptype in place_lower:
            detected_type = ptype
            break
    
    if not detected_type:
        return {
            "place": place_name,
            "time": proposed_time,
            "is_open": True,
            "confidence": "low",
            "note": "Could not determine type. Verify hours."
        }
    
    hours = typical_hours[detected_type]
    
    # Check closed days
    if day_of_week in hours["closed"]:
        return {
            "place": place_name,
            "time": proposed_time,
            "is_open": False,
            "reason": f"{detected_type}s often closed on {day_of_week}"
        }
    
    # Check time
    is_open = hours["open"] <= proposed_time <= hours["close"]
    
    return {
        "place": place_name,
        "time": proposed_time,
        "is_open": is_open,
        "hours": f"{hours['open']} - {hours['close']}",
        "confidence": "medium"
    }


# Export as FunctionTools
compute_route_matrix_tool = FunctionTool(compute_route_matrix)
validate_open_hours_tool = FunctionTool(validate_open_hours)
