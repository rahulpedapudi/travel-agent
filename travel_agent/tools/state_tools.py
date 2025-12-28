"""
STATE TOOLS - Session State Management
=======================================
Tools for persisting structured data to session state.

USED BY: All agents

FLOW:
1. Clarifier → set_preferences() → stores TripPreferences
2. Researcher → add_places() → stores hotels, restaurants, attractions
3. Activity → set_recommended_activities() → stores filtered activities
4. Builder → set_itinerary() → stores final itinerary

All agents READ via get_trip_state() - single source of truth.
"""

from typing import Optional, List
import json


from ..context import session_context
from ..redis_state import state_service

# Legacy in-memory store (kept for backwards compat, but redis_state is primary)
_trip_states = {}


def _get_state(session_id: Optional[str] = None) -> dict:
    """Get or create state for session using Redis (with fallback)."""
    if session_id is None:
        session_id = session_context.get()
    
    # Use Redis-backed service
    state = state_service.get_state(session_id)
    
    # Also maintain local cache for fast repeated access within same request
    _trip_states[session_id] = state
    return state


def _save_state(session_id: Optional[str] = None) -> None:
    """Persist state to Redis."""
    if session_id is None:
        session_id = session_context.get()
    
    if session_id in _trip_states:
        state_service.set_state(session_id, _trip_states[session_id])


# ============================================================
# PREFERENCE TOOLS (Used by Clarifier)
# ============================================================

def set_preferences(
    destination: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    duration_days: Optional[int] = None,
    budget_amount: Optional[int] = None,
    budget_level: Optional[str] = None,
    companions: Optional[str] = None,
    interests: Optional[List[str]] = None,
    pace: Optional[str] = None,
    hotel_style: Optional[str] = None,
    must_haves: Optional[List[str]] = None,
    avoids: Optional[List[str]] = None,
    mode: str = "guided"
) -> dict:
    """
    Save user's trip preferences to state.
    Called by Clarifier after gathering info.
    
    Args:
        destination: Where they're going (e.g., "Tokyo, Japan")
        start_date: Start date YYYY-MM-DD
        end_date: End date YYYY-MM-DD
        duration_days: Number of days
        budget_amount: Amount in INR
        budget_level: budget, mid_range, luxury
        companions: solo, couple, family_with_kids, friends
        interests: List like ["food", "museums", "nightlife"]
        pace: relaxed, moderate, packed
        hotel_style: luxury, boutique, mid-range, budget
        must_haves: Required features
        avoids: Things to avoid
        mode: guided or surprise_me
    
    Returns:
        Confirmation of saved preferences
    """
    state = _get_state()
    prefs = state["preferences"]
    
    if destination:
        prefs["destination"] = destination
    if start_date:
        prefs["start_date"] = start_date
    if end_date:
        prefs["end_date"] = end_date
    if duration_days:
        prefs["duration_days"] = duration_days
    if budget_amount:
        prefs["budget_amount"] = budget_amount
    if budget_level:
        prefs["budget_level"] = budget_level
    if companions:
        prefs["companions"] = companions
    if interests:
        prefs["interests"] = interests
    if pace:
        prefs["pace"] = pace
    if hotel_style:
        prefs["hotel_style"] = hotel_style
    if must_haves:
        prefs["must_haves"] = must_haves
    if avoids:
        prefs["avoids"] = avoids
    if mode:
        prefs["mode"] = mode
    
    # Persist to Redis
    _save_state()
    
    return {
        "status": "saved",
        "preferences": prefs,
        "message": "Preferences saved to state"
    }


def get_preferences() -> dict:
    """
    Get current trip preferences.
    Used by all agents to read user requirements.
    """
    state = _get_state()
    return {
        "preferences": state["preferences"],
        "is_complete": all([
            state["preferences"].get("destination"),
            state["preferences"].get("duration_days") or state["preferences"].get("start_date"),
            state["preferences"].get("budget_amount") or state["preferences"].get("budget_level")
        ])
    }


# ============================================================
# PLACE TOOLS (Used by Researcher)
# ============================================================

def add_places(
    places: List[dict],
    place_type: str
) -> dict:
    """
    Add places to state.
    Called by Researcher after finding hotels/restaurants/attractions.
    
    Args:
        places: List of place dicts with name, rating, address, etc.
        place_type: "hotel", "restaurant", "attraction"
    
    Returns:
        Confirmation with count
    """
    state = _get_state()
    
    type_key = {
        "hotel": "hotels",
        "lodging": "hotels",
        "restaurant": "restaurants",
        "cafe": "restaurants",
        "attraction": "attractions",
        "museum": "attractions",
        "park": "attractions"
    }.get(place_type.lower(), "attractions")
    
    # Add unique ID to each place
    for i, place in enumerate(places):
        if "id" not in place:
            place["id"] = f"{place_type[:3]}_{i+1}"
        place["type"] = place_type
    
    state[type_key].extend(places)
    
    # Persist to Redis
    _save_state()
    
    return {
        "status": "saved",
        "type": type_key,
        "count": len(places),
        "total": len(state[type_key])
    }


def get_places(place_type: Optional[str] = None) -> dict:
    """
    Get places from state.
    
    Args:
        place_type: Optional filter - "hotel", "restaurant", "attraction"
    
    Returns:
        Dictionary of places
    """
    state = _get_state()
    
    if place_type:
        type_key = {
            "hotel": "hotels",
            "restaurant": "restaurants",
            "attraction": "attractions"
        }.get(place_type.lower(), "attractions")
        return {"places": state.get(type_key, [])}
    
    return {
        "hotels": state["hotels"],
        "restaurants": state["restaurants"],
        "attractions": state["attractions"]
    }


# ============================================================
# ACTIVITY TOOLS (Used by Activity Agent)
# ============================================================

def set_recommended_activities(activities: List[dict]) -> dict:
    """
    Save filtered/recommended activities.
    Called by Activity Agent after filtering based on interests.
    """
    state = _get_state()
    state["recommended_activities"] = activities
    
    # Persist to Redis
    _save_state()
    
    return {
        "status": "saved",
        "count": len(activities)
    }


# ============================================================
# ITINERARY TOOLS (Used by Builder)
# ============================================================

def set_itinerary(days: List[dict]) -> dict:
    """
    Save the final itinerary.
    Called by Builder after creating the schedule.
    
    Args:
        days: List of day plans, each with activities
    """
    state = _get_state()
    state["itinerary"] = days
    state["phase"] = "complete"
    
    # Persist to Redis
    _save_state()
    
    return {
        "status": "saved",
        "days": len(days),
        "phase": "complete"
    }


def get_itinerary() -> dict:
    """Get the current itinerary."""
    state = _get_state()
    return {
        "itinerary": state["itinerary"],
        "phase": state["phase"]
    }


# ============================================================
# FULL STATE ACCESS
# ============================================================

def get_trip_state() -> dict:
    """
    Get complete trip state.
    This is the single source of truth for all agents.
    """
    return _get_state()


def set_phase(phase: str) -> dict:
    """Update workflow phase."""
    state = _get_state()
    state["phase"] = phase
    return {"phase": phase}


def add_warning(message: str) -> dict:
    """Add a warning/note to state."""
    state = _get_state()
    state["warnings"].append(message)
    return {"warning_added": message}


def clear_state(session_id: str = "default") -> dict:
    """Clear state for a session."""
    if session_id in _trip_states:
        del _trip_states[session_id]
    return {"status": "cleared"}


# Legacy compatibility
def update_trip_preferences(**kwargs) -> dict:
    """Legacy function - maps to set_preferences."""
    return set_preferences(**kwargs)


def get_trip_preferences() -> dict:
    """Legacy function - maps to get_preferences."""
    return get_preferences()
