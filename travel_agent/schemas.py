"""
SDUI RESPONSE SCHEMAS
======================
Server-Driven UI component definitions.
Frontend renders components based on these types.

USAGE:
  response = ChatResponse(
      response="What's your budget?",
      session_id="...",
      ui=UIComponent(
          type=UIType.BUDGET_SLIDER,
          props=BudgetSliderProps(min=500, max=10000)
      )
  )
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Union, Literal
from enum import Enum


# ============================================================
# UI COMPONENT TYPES
# ============================================================

class UIType(str, Enum):
    """All available UI component types."""
    
    # Input components
    BUDGET_SLIDER = "budget_slider"
    DATE_RANGE_PICKER = "date_range_picker"
    PREFERENCE_CHIPS = "preference_chips"
    COMPANION_SELECTOR = "companion_selector"
    TEXT_INPUT = "text_input"
    
    # Display components
    ITINERARY_CARD = "itinerary_card"
    ITINERARY_TIMELINE = "itinerary_timeline"
    PLACE_CARD = "place_card"
    DAY_SUMMARY = "day_summary"
    MAP_VIEW = "map_view"  # Map with markers
    ROUTE_VIEW = "route_view"  # Map with path/directions
    FLIGHT_CARD = "flight_card"  # Flight options display
    
    # Action components
    QUICK_ACTIONS = "quick_actions"
    RATING_FEEDBACK = "rating_feedback"
    CONFIRMATION = "confirmation"


# ============================================================
# COMPONENT PROPS
# ============================================================

class BudgetSliderProps(BaseModel):
    """Props for budget_slider component."""
    min: int = Field(10000, description="Minimum budget in INR")
    max: int = Field(500000, description="Maximum budget in INR")
    step: int = Field(5000, description="Slider step value")
    default: Optional[int] = Field(None, description="Default value")
    currency: str = Field("INR", description="Currency code")
    presets: List[str] = Field(
        default=["Budget (₹10k-50k)", "Mid-range (₹50k-1.5L)", "Luxury (₹2L+)"],
        description="Quick select buttons"
    )


class DateRangePickerProps(BaseModel):
    """Props for date_range_picker component."""
    min_date: Optional[str] = Field(None, description="Earliest selectable date (YYYY-MM-DD)")
    max_date: Optional[str] = Field(None, description="Latest selectable date")
    default_duration: int = Field(3, description="Default trip length in days")
    show_presets: bool = Field(True, description="Show 'This weekend', 'Next week' buttons")


class PreferenceChipsProps(BaseModel):
    """Props for preference_chips component."""
    options: List[dict] = Field(
        default=[
            {"id": "food", "label": "🍜 Food & Dining", "selected": False},
            {"id": "museums", "label": "🏛️ Museums & Art", "selected": False},
            {"id": "nature", "label": "🌲 Nature & Outdoors", "selected": False},
            {"id": "nightlife", "label": "🌙 Nightlife", "selected": False},
            {"id": "shopping", "label": "🛍️ Shopping", "selected": False},
            {"id": "history", "label": "🏰 History & Culture", "selected": False},
            {"id": "adventure", "label": "🎢 Adventure", "selected": False},
            {"id": "relaxation", "label": "🧘 Relaxation", "selected": False},
        ],
        description="Selectable preference options"
    )
    multi_select: bool = Field(True, description="Allow multiple selections")
    min_selections: int = Field(0, description="Minimum required selections")
    max_selections: Optional[int] = Field(None, description="Maximum allowed selections")


class CompanionSelectorProps(BaseModel):
    """Props for companion_selector component."""
    options: List[dict] = Field(
        default=[
            {"id": "solo", "label": "Solo", "icon": "👤"},
            {"id": "couple", "label": "Couple", "icon": "💑"},
            {"id": "family_kids", "label": "Family with Kids", "icon": "👨‍👩‍👧"},
            {"id": "family_adults", "label": "Family (Adults)", "icon": "👨‍👩‍👦‍👦"},
            {"id": "friends", "label": "Friends", "icon": "👥"},
        ],
        description="Companion type options"
    )
    show_kids_age_input: bool = Field(True, description="Show age input for family_kids")


class QuickActionsProps(BaseModel):
    """Props for quick_actions component."""
    actions: List[dict] = Field(
        default=[],
        description="Action buttons like {'id': 'swap', 'label': 'Swap Activity', 'icon': '🔄'}"
    )


class RatingFeedbackProps(BaseModel):
    """Props for rating_feedback component."""
    scale: int = Field(5, description="Rating scale (1-5)")
    show_comment: bool = Field(True, description="Show optional comment input")
    prompt: str = Field("How's this itinerary?", description="Feedback prompt text")


class ActivityItem(BaseModel):
    """Single activity in an itinerary."""
    time: str = Field(..., description="Time slot, e.g., '9:00 AM'")
    title: str = Field(..., description="Activity name")
    location: Optional[str] = Field(None, description="Place name or address")
    duration: Optional[str] = Field(None, description="e.g., '2 hours'")
    type: Optional[str] = Field(None, description="meal, attraction, transport, etc.")
    notes: Optional[str] = Field(None, description="Tips or additional info")
    image_url: Optional[str] = Field(None, description="Optional image")


class ItineraryCardProps(BaseModel):
    """Props for itinerary_card component (single day)."""
    day_number: int = Field(..., description="Day 1, 2, 3, etc.")
    date: Optional[str] = Field(None, description="Actual date if known")
    theme: Optional[str] = Field(None, description="Day theme like 'Cultural Exploration'")
    activities: List[ActivityItem] = Field(default=[], description="Day's activities")
    allow_actions: bool = Field(True, description="Show swap/add buttons")


class TimelineSegment(BaseModel):
    """Single segment in a timeline (departure, arrival, transfer, activity)."""
    time: str = Field(..., description="Time in HH:MM format, e.g., '14:10'")
    title: str = Field(..., description="Location or activity name")
    type: str = Field(..., description="departure, arrival, transfer, activity, transit")
    duration: Optional[str] = Field(None, description="Duration, e.g., '3h 25m'")
    carrier: Optional[str] = Field(None, description="Airline/train name, e.g., 'Lufthansa LH1445'")
    vehicle: Optional[str] = Field(None, description="Vehicle type, e.g., 'Airbus A320-212'")
    class_type: Optional[str] = Field(None, description="Economy, Business, etc.")
    notes: List[str] = Field(default=[], description="Additional notes or tips")
    location: Optional[dict] = Field(None, description="Location details: {name, address, lat, lng}")
    image_url: Optional[str] = Field(None, description="Optional image URL")


class ItineraryTimelineProps(BaseModel):
    """Props for itinerary_timeline component (visual timeline display)."""
    day_number: int = Field(..., description="Day 1, 2, 3, etc.")
    date: str = Field(..., description="Date string, e.g., 'Thu, Jul 8'")
    route: str = Field(..., description="Route summary, e.g., 'Washington → London'")
    total_duration: Optional[str] = Field(None, description="Total duration, e.g., '10h'")
    segments: List[TimelineSegment] = Field(default=[], description="Timeline segments")


class PlaceCardProps(BaseModel):
    """Props for place_card component (hotel, restaurant, attraction)."""
    name: str
    type: str = Field(..., description="hotel, restaurant, attraction")
    rating: Optional[float] = Field(None, description="Rating out of 5")
    price_level: Optional[str] = Field(None, description="$, $$, $$$, $$$$")
    address: Optional[str] = None
    image_url: Optional[str] = None
    features: List[str] = Field(default=[], description="Amenities or highlights")


class ConfirmationProps(BaseModel):
    """Props for confirmation component."""
    title: str = Field("Confirm your choices")
    items: List[dict] = Field(
        default=[],
        description="Items to confirm: [{'label': 'Destination', 'value': 'Tokyo'}]"
    )
    confirm_text: str = Field("Looks good!", description="Confirm button text")
    edit_text: str = Field("Make changes", description="Edit button text")


# ============================================================
# MAP COMPONENTS
# ============================================================

class MapMarker(BaseModel):
    """A single marker on the map."""
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    title: str = Field(..., description="Marker title/name")
    type: Literal["hotel", "attraction", "restaurant", "activity"] = Field(
        "attraction", description="Marker type for styling"
    )
    description: Optional[str] = Field(None, description="Optional description")
    day: Optional[int] = Field(None, description="Day number for color coding")


class MapViewProps(BaseModel):
    """Props for map_view component - shows pins on a map."""
    center: dict = Field(
        ..., 
        description="Map center: {'lat': 35.6762, 'lng': 139.6503}"
    )
    zoom: int = Field(13, description="Map zoom level (1-20)")
    markers: List[MapMarker] = Field(
        default=[], 
        description="List of markers to display"
    )
    title: Optional[str] = Field(None, description="Map title")


class RouteWaypoint(BaseModel):
    """A waypoint in a route."""
    lat: float
    lng: float
    title: str
    order: int = Field(..., description="Stop order (1, 2, 3...)")
    arrival_time: Optional[str] = Field(None, description="Expected arrival time")


class RouteViewProps(BaseModel):
    """Props for route_view component - shows path between locations."""
    origin: dict = Field(..., description="Start point: {'lat': x, 'lng': y, 'title': 'Hotel'}")
    destination: dict = Field(..., description="End point: {'lat': x, 'lng': y, 'title': 'Airport'}")
    waypoints: List[RouteWaypoint] = Field(
        default=[], 
        description="Intermediate stops"
    )
    travel_mode: Literal["DRIVING", "WALKING", "TRANSIT", "BICYCLING"] = Field(
        "TRANSIT", 
        description="Travel mode for directions"
    )
    day_number: Optional[int] = Field(None, description="Day this route belongs to")
    show_traffic: bool = Field(False, description="Show traffic layer")


# ============================================================
# FLIGHT COMPONENTS
# ============================================================

class FlightSegment(BaseModel):
    """A single flight leg."""
    departure_airport: str = Field(..., description="Departure airport code, e.g., 'DEL'")
    departure_city: str = Field(..., description="Departure city name")
    departure_time: str = Field(..., description="Departure time, e.g., '14:30'")
    arrival_airport: str = Field(..., description="Arrival airport code, e.g., 'NRT'")
    arrival_city: str = Field(..., description="Arrival city name")
    arrival_time: str = Field(..., description="Arrival time, e.g., '22:45'")
    duration: str = Field(..., description="Flight duration, e.g., '6h 15m'")
    airline: str = Field(..., description="Airline name")
    flight_number: str = Field(..., description="Flight number, e.g., 'NH828'")
    aircraft: Optional[str] = Field(None, description="Aircraft type, e.g., 'Boeing 787'")
    cabin_class: str = Field("Economy", description="Economy, Business, First")


class FlightOption(BaseModel):
    """A complete flight option (may have multiple segments for connections)."""
    id: str = Field(..., description="Unique flight option ID")
    segments: List[FlightSegment] = Field(..., description="Flight segments (legs)")
    total_duration: str = Field(..., description="Total journey time")
    stops: int = Field(0, description="Number of stops (0 = direct)")
    price: float = Field(..., description="Price in local currency")
    currency: str = Field("INR", description="Currency code")
    price_formatted: str = Field(..., description="Formatted price, e.g., '₹45,000'")
    booking_class: str = Field("Economy", description="Cabin class")


class FlightCardProps(BaseModel):
    """Props for flight_card component."""
    origin: str = Field(..., description="Origin city")
    destination: str = Field(..., description="Destination city")
    departure_date: str = Field(..., description="Departure date YYYY-MM-DD")
    return_date: Optional[str] = Field(None, description="Return date for round trips")
    passengers: int = Field(1, description="Number of passengers")
    flights: List[FlightOption] = Field(default=[], description="Available flight options")
    show_return: bool = Field(False, description="Show return flights")


# ============================================================
# UI COMPONENT WRAPPER
# ============================================================

class UIComponent(BaseModel):
    """Wrapper for any UI component."""
    type: UIType
    props: Union[
        BudgetSliderProps,
        DateRangePickerProps,
        PreferenceChipsProps,
        CompanionSelectorProps,
        QuickActionsProps,
        RatingFeedbackProps,
        ItineraryCardProps,
        ItineraryTimelineProps,
        PlaceCardProps,
        ConfirmationProps,
        MapViewProps,
        RouteViewProps,
        FlightCardProps,
        dict  # Fallback for unknown types
    ] = Field(default_factory=dict)
    required: bool = Field(False, description="Whether user must interact before continuing")


# ============================================================
# CHAT RESPONSE WITH UI
# ============================================================

class ChatResponse(BaseModel):
    """Enhanced chat response with optional UI component."""
    response: str = Field(..., description="Text response from agent")
    session_id: str = Field(..., description="Session identifier")
    ui: Optional[UIComponent] = Field(None, description="Optional UI component to render")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "What's your budget for this trip?",
                "session_id": "abc-123",
                "ui": {
                    "type": "budget_slider",
                    "props": {
                        "min": 500,
                        "max": 10000,
                        "presets": ["Budget", "Mid-range", "Luxury"]
                    },
                    "required": True
                }
            }
        }


# ============================================================
# NOTE: UI Component Selection
# ============================================================
# UI components are now selected by the LLM via the render_ui tool
# in travel_agent/tools/ui_tools.py. The agent calls render_ui()
# to specify which component to show, and the API extracts it
# from the tool response.
