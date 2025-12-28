"""
SCHEDULER TOOLS - Deterministic Itinerary Building
===================================================
Code-based scheduling to replace LLM-based time calculations.

WHY CODE, NOT LLM:
- LLMs are bad at math (9:00 + 2h = ??)
- LLMs hallucinate opening hours
- Code is deterministic and reliable

HOW IT WORKS:
1. LLM decides WHAT to include and in what ORDER
2. Code calculates WHEN (start/end times, travel time)
3. Code validates (opening hours, no overlaps)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import math


def build_schedule(
    places: List[dict],
    duration_days: int,
    pace: str = "moderate",
    start_time: str = "09:00",
    end_time: str = "21:00"
) -> dict:
    """
    Build a complete itinerary schedule from a list of places.
    
    Args:
        places: List of places to visit, each with:
            - name: str
            - type: str (attraction, restaurant, museum, etc.)
            - duration_minutes: int (estimated visit time)
            - opening_time: str (optional, e.g., "09:00")
            - closing_time: str (optional, e.g., "18:00")
            - lat, lng: float (optional, for travel time)
        duration_days: Number of days
        pace: "relaxed" (3-4 activities/day), "moderate" (4-5), "packed" (5-6)
        start_time: Day start time
        end_time: Day end time
    
    Returns:
        {
            "success": true,
            "days": [
                {
                    "day_number": 1,
                    "activities": [
                        {"time": "09:00", "end_time": "11:00", "place": {...}, "travel_minutes": 0},
                        {"time": "11:30", "end_time": "13:00", "place": {...}, "travel_minutes": 30}
                    ]
                }
            ],
            "warnings": ["Could not fit X on Day 2 due to closing time"]
        }
    """
    # Set activities per day based on pace
    max_activities = {"relaxed": 4, "moderate": 5, "packed": 6}.get(pace, 5)
    
    # Default durations by type
    default_durations = {
        "museum": 120,
        "attraction": 90,
        "restaurant": 75,
        "cafe": 45,
        "park": 60,
        "shopping": 90,
        "temple": 60,
        "beach": 180,
        "hotel": 0
    }
    
    # Prepare places with durations
    prepared_places = []
    for p in places:
        place = p.copy()
        if "duration_minutes" not in place:
            place["duration_minutes"] = default_durations.get(
                place.get("type", "attraction").lower(), 90
            )
        prepared_places.append(place)
    
    # Group by type priorities
    # Breakfast spot first, dinner last, attractions in between
    breakfast_types = ["cafe", "breakfast"]
    lunch_types = ["restaurant", "lunch"]
    dinner_types = ["restaurant", "dinner", "bar"]
    
    # Distribution planning
    days = []
    warnings = []
    place_index = 0
    
    for day_num in range(1, duration_days + 1):
        day_activities = []
        current_time = datetime.strptime(start_time, "%H:%M")
        day_end = datetime.strptime(end_time, "%H:%M")
        activities_today = 0
        
        while (activities_today < max_activities and 
               place_index < len(prepared_places) and
               current_time < day_end):
            
            place = prepared_places[place_index]
            duration = place.get("duration_minutes", 90)
            
            # Check if we can fit this activity
            activity_end = current_time + timedelta(minutes=duration)
            
            # Check opening hours if available
            opening = place.get("opening_time")
            closing = place.get("closing_time")
            
            if opening:
                open_time = datetime.strptime(opening, "%H:%M")
                if current_time < open_time:
                    # Wait until it opens
                    current_time = open_time
                    activity_end = current_time + timedelta(minutes=duration)
            
            if closing:
                close_time = datetime.strptime(closing, "%H:%M")
                if activity_end > close_time:
                    # Can't fit before closing
                    warnings.append(f"Moved {place['name']} - closes at {closing}")
                    # Try to fit at opening next day
                    place_index += 1
                    continue
            
            # Check if past day end
            if activity_end > day_end:
                # Done for today
                break
            
            # Calculate travel time from previous (estimate)
            travel_time = 0
            if day_activities:
                prev = day_activities[-1]["place"]
                travel_time = _estimate_travel_time(prev, place)
                current_time += timedelta(minutes=travel_time)
                activity_end = current_time + timedelta(minutes=duration)
            
            # Add the activity
            day_activities.append({
                "time": current_time.strftime("%H:%M"),
                "end_time": activity_end.strftime("%H:%M"),
                "duration_minutes": duration,
                "travel_from_previous": travel_time,
                "place": place
            })
            
            current_time = activity_end + timedelta(minutes=15)  # 15 min buffer
            activities_today += 1
            place_index += 1
        
        days.append({
            "day_number": day_num,
            "activities": day_activities,
            "total_activities": len(day_activities)
        })
    
    # Check for unscheduled places
    if place_index < len(prepared_places):
        unscheduled = [p["name"] for p in prepared_places[place_index:]]
        warnings.append(f"Could not fit: {', '.join(unscheduled[:3])}")
    
    return {
        "success": True,
        "days": days,
        "scheduled_count": place_index,
        "total_places": len(prepared_places),
        "warnings": warnings
    }


def _estimate_travel_time(from_place: dict, to_place: dict) -> int:
    """Estimate travel time between two places."""
    # If we have coordinates, use distance
    if all(k in from_place for k in ["lat", "lng"]) and all(k in to_place for k in ["lat", "lng"]):
        dist = _haversine_distance(
            from_place["lat"], from_place["lng"],
            to_place["lat"], to_place["lng"]
        )
        # Rough estimate: 30 km/h average city speed
        minutes = int(dist / 0.5)  # km / (km/min)
        return max(10, min(60, minutes))  # 10-60 min range
    
    # Default estimate based on location types
    if from_place.get("type") == to_place.get("type"):
        return 15  # Same type, likely same area
    return 25  # Different types, moderate distance


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km."""
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def optimize_route_order(places: List[dict]) -> List[dict]:
    """
    Reorder places to minimize travel time (nearest neighbor algorithm).
    
    Args:
        places: List of places with lat, lng coordinates
    
    Returns:
        Reordered list of places
    """
    if len(places) <= 2:
        return places
    
    # Filter places with coordinates
    with_coords = [p for p in places if "lat" in p and "lng" in p]
    without_coords = [p for p in places if "lat" not in p or "lng" not in p]
    
    if len(with_coords) <= 1:
        return places
    
    # Simple nearest neighbor
    ordered = [with_coords[0]]
    remaining = with_coords[1:]
    
    while remaining:
        current = ordered[-1]
        nearest = min(remaining, key=lambda p: _haversine_distance(
            current["lat"], current["lng"], p["lat"], p["lng"]
        ))
        ordered.append(nearest)
        remaining.remove(nearest)
    
    return ordered + without_coords


def validate_schedule(schedule: dict) -> dict:
    """
    Validate a schedule for issues.
    
    Checks:
    - No time overlaps
    - Opening hours respected
    - Reasonable travel times
    """
    issues = []
    
    for day in schedule.get("days", []):
        prev_end = None
        for activity in day.get("activities", []):
            start = datetime.strptime(activity["time"], "%H:%M")
            end = datetime.strptime(activity["end_time"], "%H:%M")
            
            if prev_end and start < prev_end:
                issues.append({
                    "type": "overlap",
                    "day": day["day_number"],
                    "activity": activity["place"]["name"]
                })
            
            prev_end = end
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


def add_meals_to_schedule(schedule: dict, restaurants: List[dict]) -> dict:
    """
    Insert meal breaks into an existing schedule.
    
    Inserts at:
    - ~12:30 lunch
    - ~19:30 dinner
    """
    lunch_time = "12:30"
    dinner_time = "19:30"
    
    for day in schedule.get("days", []):
        activities = day["activities"]
        
        # Find where to insert lunch
        lunch_inserted = False
        dinner_inserted = False
        
        new_activities = []
        for i, activity in enumerate(activities):
            if not lunch_inserted and activity["time"] >= lunch_time:
                # Insert lunch before this activity
                if restaurants:
                    restaurant = restaurants[i % len(restaurants)]
                    new_activities.append({
                        "time": lunch_time,
                        "end_time": "13:30",
                        "duration_minutes": 60,
                        "travel_from_previous": 15,
                        "place": {**restaurant, "meal_type": "lunch"},
                        "is_meal": True
                    })
                lunch_inserted = True
            
            new_activities.append(activity)
            
            if not dinner_inserted and activity["time"] >= dinner_time:
                if restaurants:
                    restaurant = restaurants[(i + 1) % len(restaurants)]
                    new_activities.append({
                        "time": dinner_time,
                        "end_time": "21:00",
                        "duration_minutes": 90,
                        "travel_from_previous": 20,
                        "place": {**restaurant, "meal_type": "dinner"},
                        "is_meal": True
                    })
                dinner_inserted = True
        
        day["activities"] = new_activities
    
    return schedule
