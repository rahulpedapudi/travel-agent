"""
BUILDER AGENT - Create multi-day itinerary in JSON format.
"""

from google.adk.agents import Agent
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from ..tools import BUILDER_TOOLS
from ..tools.scheduler_tools import build_schedule, optimize_route_order


# ============================================================
# OUTPUT SCHEMA - Enforces structured itinerary output
# ============================================================

class Activity(BaseModel):
    """Single activity in an itinerary day."""
    start_time: str = Field(..., description="Start time in HH:MM format, e.g., '09:00'")
    end_time: str = Field(..., description="End time in HH:MM format, e.g., '11:00'")
    duration: Optional[str] = Field(None, description="Duration, e.g., '2h' or '1h 30m'")
    title: str = Field(..., description="Activity name")
    location: str = Field(..., description="Place address or area")
    type: Literal["attraction", "food", "shopping", "nature", "transport", "hotel"] = Field(
        ..., description="Activity type"
    )
    description: Optional[str] = Field(None, description="Brief description")
    notes: List[str] = Field(default_factory=list, description="Tips or additional info")
    travel_duration: Optional[str] = Field(None, description="Travel time from previous activity")
    travel_method: Optional[str] = Field(None, description="Transit method, e.g., 'Metro', 'Walk'")


class Day(BaseModel):
    """Single day in the itinerary."""
    day_number: int = Field(..., description="Day 1, 2, 3, etc.")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    theme: str = Field(..., description="Day theme, e.g., 'Cultural Exploration'")
    activities: List[Activity] = Field(..., description="List of activities for the day")


class ItineraryOutput(BaseModel):
    """Complete itinerary output from the builder agent."""
    days: List[Day] = Field(..., description="Complete list of days in the itinerary")
    summary: str = Field(..., description="Brief 1-2 sentence summary of the trip")


# ============================================================
# BUILDER AGENT
# ============================================================

builder_agent = Agent(
    name="itinerary_builder",
    model="gemini-2.5-flash",
    tools=[*BUILDER_TOOLS, build_schedule, optimize_route_order],
    
    instruction="""
  You create complete, realistic multi-day travel itineraries using researched places.

  ## WORKFLOW

  1. Call `get_places()` to retrieve the researched hotels, attractions, and restaurants
  2. Call `get_preferences()` to get user preferences (dates, companions, interests)
  3. Call `build_schedule()` to help organize the timeline
  4. Call `set_itinerary(days=[...])` to save the itinerary
  5. Call `render_ui("itinerary_card", {"days": [...]})` to display it

  ❌ NEVER skip the set_itinerary or render_ui calls
  ✅ ALWAYS call both before providing your summary

  ## DAY COMPLETENESS RULES

  Each day MUST:
  * Run from ~8:00-9:00 AM to ~9:00-10:30 PM
  * Include Breakfast, Lunch, and Dinner (type: "food")
  * Have at least one rest/buffer period
  * Have no unexplained gaps > 60 minutes
  * Group activities by neighborhood to minimize transit

  ## ACTIVITY TYPES

  Use ONLY: "attraction", "food", "shopping", "nature", "transport", "hotel"

  ## OUTPUT

  Your output will be parsed as JSON matching the ItineraryOutput schema.
  Include a brief, friendly summary describing the trip highlights.
"""

)

