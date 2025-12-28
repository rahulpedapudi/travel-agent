"""
TOOLS PACKAGE
=============
Exports all tools for the travel agent system.

IMPORTANT: google_search cannot be used in sub-agents (AgentTool limitation).
Only use google_search in agents that are NOT wrapped as AgentTool.
"""

# DateTime tools
from .datetime_tools import (
    get_current_datetime,
    get_calendar_dates,
    add_time_duration,
)

# Search tools
from .search_tools import (
    search_travel_info,
    search_transport,
)

# Places tools
from .places_tools import (
    find_places_nearby,
)

# Maps tools
from .maps_tools import (
    compute_route_matrix,
    validate_open_hours,
)

# State tools - Structured state management
from .state_tools import (
    set_preferences,
    get_preferences,
    add_places,
    get_places,
    set_recommended_activities,
    set_itinerary,
    get_itinerary,
    get_trip_state,
    set_phase,
    add_warning,
    clear_state,
    # Legacy compatibility
    update_trip_preferences,
    get_trip_preferences,
)

# Extraction tools - Entity extraction for slot-filling
from .extraction_tools import (
    extract_trip_entities,
    get_next_question,
)

# Validation tools
from .validation_tools import (
    validate_destination,
    validate_budget,
)

# UI tools
from .ui_tools import (
    render_ui,
    render_itinerary_card,
    set_chat_title,
)


# Grouped exports by agent

RESEARCH_TOOLS = [
    find_places_nearby,
    get_current_datetime,
    search_transport,
    search_travel_info,
    add_places,  # To save results to state
    get_preferences,  # To read user preferences
]

BUILDER_TOOLS = [
    compute_route_matrix,
    validate_open_hours,
    add_time_duration,
    get_places,  # Read places from state
    get_preferences,  # Read preferences from state
    set_itinerary,  # Save final itinerary
    render_ui,  # Trigger UI display
]

CLARIFIER_TOOLS = [
    validate_destination,
    validate_budget,
    get_calendar_dates,
    set_preferences,
    get_preferences,
    extract_trip_entities,
    get_next_question,
    render_ui,  # Required for server-driven UI
]

ACTIVITY_TOOLS = [
    find_places_nearby,
    get_places,  # Read places from state
    get_preferences,  # Read user interests
    set_recommended_activities,  # Save filtered results
]


__all__ = [
    # DateTime
    "get_current_datetime",
    "get_calendar_dates",
    "add_time_duration",
    # Search
    "search_travel_info",
    "search_transport",
    # Places
    "find_places_nearby",
    # Maps
    "compute_route_matrix",
    "validate_open_hours",
    # State
    "set_preferences",
    "get_preferences",
    "add_places",
    "get_places",
    "set_recommended_activities",
    "set_itinerary",
    "get_itinerary",
    "get_trip_state",
    "set_phase",
    "add_warning",
    "clear_state",
    "update_trip_preferences",
    "get_trip_preferences",
    # Extraction
    "extract_trip_entities",
    "get_next_question",
    # Validation
    "validate_destination",
    "validate_budget",
    # UI
    "render_ui",
    "set_chat_title",
    # Tool groups
    "RESEARCH_TOOLS",
    "BUILDER_TOOLS",
    "CLARIFIER_TOOLS",
    "ACTIVITY_TOOLS",
]
