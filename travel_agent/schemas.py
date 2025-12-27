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
    PLACE_CARD = "place_card"
    DAY_SUMMARY = "day_summary"
    
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
        PlaceCardProps,
        ConfirmationProps,
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
# UI HINT PATTERNS (for parsing agent output)
# ============================================================

UI_PATTERNS = {
    # Keywords that trigger specific UI components
    "budget": UIType.BUDGET_SLIDER,
    "how much": UIType.BUDGET_SLIDER,
    "when are you": UIType.DATE_RANGE_PICKER,
    "travel dates": UIType.DATE_RANGE_PICKER,
    "what do you enjoy": UIType.PREFERENCE_CHIPS,
    "interests": UIType.PREFERENCE_CHIPS,
    "who's traveling": UIType.COMPANION_SELECTOR,
    "traveling with": UIType.COMPANION_SELECTOR,
    "how's this": UIType.RATING_FEEDBACK,
    "rate": UIType.RATING_FEEDBACK,
}


def detect_ui_component(text: str) -> Optional[UIComponent]:
    """
    Detect which UI component to show based on agent response text.
    Returns None if no special UI needed.
    """
    text_lower = text.lower()
    
    for pattern, ui_type in UI_PATTERNS.items():
        if pattern in text_lower:
            if ui_type == UIType.BUDGET_SLIDER:
                return UIComponent(type=ui_type, props=BudgetSliderProps(), required=True)
            elif ui_type == UIType.DATE_RANGE_PICKER:
                return UIComponent(type=ui_type, props=DateRangePickerProps(), required=True)
            elif ui_type == UIType.PREFERENCE_CHIPS:
                return UIComponent(type=ui_type, props=PreferenceChipsProps(), required=True)
            elif ui_type == UIType.COMPANION_SELECTOR:
                return UIComponent(type=ui_type, props=CompanionSelectorProps(), required=True)
            elif ui_type == UIType.RATING_FEEDBACK:
                return UIComponent(type=ui_type, props=RatingFeedbackProps(), required=False)
    
    return None
