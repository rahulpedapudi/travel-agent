"""
TOOLS PACKAGE
=============
Exports all tools for the travel agent system.

IMPORTANT: google_search cannot be used in sub-agents (AgentTool limitation).
Only use google_search in agents that are NOT wrapped as AgentTool.
"""

# Import raw functions (not FunctionTool wrappers for compatibility)
from .datetime_tools import (
    get_current_datetime,
    get_calendar_dates,
    add_time_duration,
)

from .search_tools import (
    search_travel_info,
    search_transport,
)

from .places_tools import (
    find_places_nearby,
)

from .maps_tools import (
    compute_route_matrix,
    validate_open_hours,
)

from .state_tools import (
    update_trip_preferences,
    get_trip_preferences,
)

from .validation_tools import (
    validate_destination,
    validate_budget,
)

from .ui_tools import (
    render_ui,
)


# Grouped exports by agent - NO google_search in sub-agents!
# google_search causes "Tool use with function calling is unsupported" in AgentTool

RESEARCH_TOOLS = [
    find_places_nearby,
    get_current_datetime,
    search_transport,
    search_travel_info,
]

BUILDER_TOOLS = [
    compute_route_matrix,
    validate_open_hours,
    add_time_duration,
]

CLARIFIER_TOOLS = [
    validate_destination,
    validate_budget,
    get_calendar_dates,
    update_trip_preferences,
]


__all__ = [
    "get_current_datetime",
    "get_calendar_dates",
    "add_time_duration",
    "search_travel_info",
    "search_transport",
    "find_places_nearby",
    "compute_route_matrix",
    "validate_open_hours",
    "update_trip_preferences",
    "get_trip_preferences",
    "validate_destination",
    "validate_budget",
    "render_ui",
    "RESEARCH_TOOLS",
    "BUILDER_TOOLS",
    "CLARIFIER_TOOLS",
]
