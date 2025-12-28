"""
TRIP STATE MODELS
=================
Pydantic models for structured state management between agents.

WHY PYDANTIC:
- Type validation at runtime
- Easy JSON serialization/deserialization
- Clear schema for all agents to follow
- No more parsing LLM text output

FLOW:
1. Clarifier extracts entities → writes to TripState.preferences
2. Researcher finds places → writes to TripState.hotels, .restaurants, .attractions
3. Activity agent filters → writes to TripState.activities
4. Builder reads all data → creates TripState.itinerary
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import date


# ============================================================
# ENUMS
# ============================================================

class TripMode(str, Enum):
    GUIDED = "guided"
    SURPRISE_ME = "surprise_me"


class CompanionType(str, Enum):
    SOLO = "solo"
    COUPLE = "couple"
    FAMILY_WITH_KIDS = "family_with_kids"
    FAMILY_ADULTS = "family_adults"
    FRIENDS = "friends"
    BUSINESS = "business"


class TravelPace(str, Enum):
    RELAXED = "relaxed"
    MODERATE = "moderate"
    PACKED = "packed"


class BudgetLevel(str, Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    LUXURY = "luxury"


# ============================================================
# PLACE MODELS (Structured data from APIs)
# ============================================================

class Location(BaseModel):
    """Geographic coordinates for route planning."""
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    address: Optional[str] = Field(None, description="Formatted address")


class OpeningHours(BaseModel):
    """Business hours for scheduling."""
    open: str = Field(..., description="Opening time, e.g., '09:00'")
    close: str = Field(..., description="Closing time, e.g., '18:00'")
    closed_days: List[str] = Field(default=[], description="Days closed, e.g., ['Monday']")


class Place(BaseModel):
    """
    Structured place data from Google Places API.
    Used by Researcher and Activity agents.
    """
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Place name")
    type: str = Field(..., description="hotel, restaurant, attraction, cafe, museum, etc.")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Rating out of 5")
    price_level: Optional[str] = Field(None, description="$, $$, $$$, $$$$")
    location: Optional[Location] = Field(None, description="Geographic location")
    hours: Optional[OpeningHours] = Field(None, description="Opening hours")
    image_url: Optional[str] = Field(None, description="Photo URL")
    features: List[str] = Field(default=[], description="Amenities or highlights")
    description: Optional[str] = Field(None, description="Brief description")
    
    # Metadata for filtering
    tags: List[str] = Field(default=[], description="Tags like 'kid-friendly', 'romantic'")
    match_score: Optional[int] = Field(None, description="Relevance score from Activity agent")


# ============================================================
# PREFERENCES MODEL (From Clarifier)
# ============================================================

class TripDates(BaseModel):
    """Parsed date information."""
    start_date: Optional[str] = Field(None, description="Start date, YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="End date, YYYY-MM-DD")
    duration_days: int = Field(3, description="Number of days")
    flexibility: Optional[str] = Field(None, description="flexible, fixed")


class Budget(BaseModel):
    """Parsed budget information."""
    amount: Optional[int] = Field(None, description="Amount in INR")
    level: BudgetLevel = Field(BudgetLevel.MID_RANGE, description="Budget category")
    currency: str = Field("INR", description="Currency code")
    per_day: Optional[int] = Field(None, description="Daily budget if specified")


class TripPreferences(BaseModel):
    """
    All user preferences gathered by Clarifier.
    Single source of truth for personalization.
    """
    # Mode
    mode: TripMode = Field(TripMode.GUIDED)
    
    # Basic info
    destination: Optional[str] = Field(None, description="Destination city/country")
    dates: Optional[TripDates] = Field(None, description="Travel dates")
    budget: Optional[Budget] = Field(None, description="Budget info")
    
    # Travel style
    companions: Optional[CompanionType] = Field(None)
    pace: TravelPace = Field(TravelPace.MODERATE)
    
    # Interests (for activity filtering)
    interests: List[str] = Field(
        default=[],
        description="food, museums, nature, nightlife, shopping, history, adventure, relaxation"
    )
    
    # Accommodation
    hotel_style: Optional[str] = Field(None, description="luxury, boutique, mid-range, budget, airbnb")
    
    # Constraints
    must_haves: List[str] = Field(default=[], description="Required features")
    avoids: List[str] = Field(default=[], description="Things to avoid")
    
    # Extraction confidence
    extracted_entities: Dict[str, bool] = Field(
        default={},
        description="Which fields were extracted vs asked"
    )


# ============================================================
# ITINERARY MODEL (From Builder)
# ============================================================

class ScheduledActivity(BaseModel):
    """Single activity with scheduled time."""
    time: str = Field(..., description="Start time, e.g., '09:00'")
    end_time: Optional[str] = Field(None, description="End time")
    duration_minutes: int = Field(60, description="Duration in minutes")
    place: Place = Field(..., description="The place/activity")
    travel_from_previous: Optional[int] = Field(None, description="Travel time from previous in minutes")
    notes: Optional[str] = Field(None, description="Tips or notes")


class ItineraryDay(BaseModel):
    """Single day plan."""
    day_number: int = Field(..., description="Day 1, 2, 3...")
    date: Optional[str] = Field(None, description="Actual date if known")
    theme: Optional[str] = Field(None, description="Day theme, e.g., 'Cultural Exploration'")
    activities: List[ScheduledActivity] = Field(default=[])
    total_travel_time: Optional[int] = Field(None, description="Total travel time in minutes")


# ============================================================
# MAIN TRIP STATE
# ============================================================

class TripState(BaseModel):
    """
    Complete trip state - single source of truth.
    
    All agents read/write to this structured state.
    No more parsing chat logs!
    """
    # User preferences (written by Clarifier)
    preferences: TripPreferences = Field(default_factory=TripPreferences)
    
    # Research data (written by Researcher)
    hotels: List[Place] = Field(default=[])
    restaurants: List[Place] = Field(default=[])
    attractions: List[Place] = Field(default=[])
    
    # Filtered activities (written by Activity Agent)
    recommended_activities: List[Place] = Field(default=[])
    
    # Final itinerary (written by Builder)
    itinerary: List[ItineraryDay] = Field(default=[])
    
    # Metadata
    phase: str = Field("clarifying", description="clarifying, researching, building, complete")
    last_updated: Optional[str] = Field(None, description="ISO timestamp")
    warnings: List[str] = Field(default=[], description="Any issues or notes")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_place_from_api(api_result: dict, place_type: str) -> Place:
    """Convert Google Places API result to Place model."""
    import uuid
    
    return Place(
        id=api_result.get("place_id", str(uuid.uuid4())[:8]),
        name=api_result.get("name", "Unknown"),
        type=place_type,
        rating=api_result.get("rating"),
        price_level=api_result.get("price_level"),
        location=Location(
            lat=api_result.get("lat", 0),
            lng=api_result.get("lng", 0),
            address=api_result.get("address")
        ) if api_result.get("address") else None,
        features=api_result.get("features", []),
        description=api_result.get("description")
    )


def trip_state_to_dict(state: TripState) -> dict:
    """Serialize TripState for session storage."""
    return state.model_dump()


def dict_to_trip_state(data: dict) -> TripState:
    """Deserialize TripState from session storage."""
    if data is None:
        return TripState()
    return TripState.model_validate(data)
