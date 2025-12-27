"""
STATE MANAGEMENT MODULE
=======================
WHY THIS IS NEEDED:
- Your current agents use keyword markers like "READY", "RESEARCH_COMPLETE" 
  to signal transitions. This is fragile because:
  1. The LLM might output the keyword incorrectly or forget it
  2. There's no structured way to pass data between agents
  3. You can't persist or resume a conversation

HOW ADK STATE WORKS:
- ADK provides `session.state` - a shared dictionary that all agents can 
  read/write during a conversation
- Data persists throughout the session lifecycle
- We use consistent key names so agents know where to find data

KEY PATTERN: "namespace:key_name"
- "user:" prefix = user-provided data (destination, budget, dates)
- "app:" prefix  = application state (current phase, research results)
- "temp:" prefix = temporary data (cleared between turns)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class WorkflowPhase(Enum):
    """
    Tracks which stage of the travel planning workflow we're in.
    
    WHY USE AN ENUM:
    - Prevents typos (can't accidentally write "clarifyng" instead of "clarifying")
    - IDE autocomplete support
    - Easy to add new phases later if needed
    """
    CLARIFYING = "clarifying"      # Gathering destination, budget, dates
    RESEARCHING = "researching"    # Searching for flights, hotels, attractions
    BUILDING = "building"          # Creating the day-by-day itinerary
    COMPLETE = "complete"          # Final plan delivered to user


class ConfidenceLevel(Enum):
    """
    Tracks how confident we are in each requirement value.
    
    WHY TRACK CONFIDENCE:
    - Allows the agent to proceed with smart defaults instead of blocking
    - Makes it transparent to the user which values were assumed
    - Enables the agent to ask for confirmation on low-confidence items
    """
    HIGH = "high"        # User explicitly stated this value
    MEDIUM = "medium"    # Inferred with reasonable certainty (e.g., dates from "next week")
    LOW = "low"          # Default/assumed value (e.g., "mid-range" budget if not specified)


@dataclass
class RequirementConfidence:
    """
    Tracks confidence levels for each travel requirement.
    """
    destination: ConfidenceLevel = ConfidenceLevel.LOW
    budget: ConfidenceLevel = ConfidenceLevel.LOW
    dates: ConfidenceLevel = ConfidenceLevel.LOW


# Smart defaults when user doesn't specify
DEFAULT_BUDGET = "mid-range (approximately $100-200/day)"
DEFAULT_DURATION = "3 days"


@dataclass
class TravelRequirements:
    """
    Holds the "Big 3" user requirements that clarifier_agent gathers.
    
    WHY A DATACLASS:
    - Type hints catch bugs early (e.g., passing int instead of str)
    - Easy to serialize to JSON for session state storage
    - Clear structure that all agents understand
    
    SMART DEFAULTS:
    - If dates missing → assume 3-day trip, tag as LOW confidence
    - If budget missing → infer "mid-range", tag as LOW confidence
    - User-provided values get HIGH confidence
    """
    destination: Optional[str] = None   # e.g., "Tokyo, Japan"
    budget: Optional[str] = None        # e.g., "$3000" or "mid-range"
    dates: Optional[str] = None         # e.g., "January 15-22, 2025" or "3 days"
    preferences: Optional[str] = None   # e.g., "family-friendly, cultural"
    
    # Confidence tracking for each field
    confidence: RequirementConfidence = field(default_factory=RequirementConfidence)
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled (including defaults)."""
        return all([self.destination, self.budget, self.dates])
    
    def apply_defaults(self) -> None:
        """
        Apply smart defaults for missing values.
        Sets confidence to LOW for defaulted fields.
        """
        if not self.budget:
            self.budget = DEFAULT_BUDGET
            self.confidence.budget = ConfidenceLevel.LOW
        
        if not self.dates:
            self.dates = DEFAULT_DURATION
            self.confidence.dates = ConfidenceLevel.LOW
    
    def get_low_confidence_fields(self) -> list:
        """Return list of fields that have LOW confidence (were assumed)."""
        low_conf = []
        if self.confidence.destination == ConfidenceLevel.LOW:
            low_conf.append("destination")
        if self.confidence.budget == ConfidenceLevel.LOW:
            low_conf.append("budget")
        if self.confidence.dates == ConfidenceLevel.LOW:
            low_conf.append("dates")
        return low_conf


@dataclass
class ResearchData:
    """
    Structured container for researcher_agent's findings.
    
    WHY STRUCTURE THIS:
    - Instead of parsing JSON from LLM text output (error-prone),
      we store research in a predictable format
    - builder_agent can easily access hotels, attractions, etc.
    """
    hotels: List[Dict[str, Any]] = field(default_factory=list)
    attractions: List[Dict[str, Any]] = field(default_factory=list)
    flights: List[Dict[str, Any]] = field(default_factory=list)
    weather: Optional[str] = None


# ============================================================
# SESSION STATE KEYS
# ============================================================
# These are the exact keys used in session.state dictionary.
# All agents should import and use these constants instead of 
# hardcoding strings - prevents typos and makes refactoring easy.

STATE_KEYS = {
    # Current workflow phase (WorkflowPhase enum value)
    "phase": "app:workflow_phase",
    
    # User's travel requirements (TravelRequirements dataclass)
    "requirements": "user:requirements",
    
    # Research findings (ResearchData dataclass)
    "research": "app:research_data",
    
    # Final itinerary output (dict with day-by-day plan)
    "itinerary": "app:final_itinerary",
    
    # Error state for graceful recovery
    "last_error": "temp:last_error"
}


def initialize_session_state(state: dict) -> dict:
    """
    Set up initial state values when a new session starts.
    
    WHY THIS FUNCTION:
    - Ensures consistent initial state across all sessions
    - Prevents KeyError when agents try to read state before it's set
    - Called once at session creation in runner.py
    
    Args:
        state: The session.state dictionary from ADK
        
    Returns:
        The initialized state dictionary
    """
    state[STATE_KEYS["phase"]] = WorkflowPhase.CLARIFYING.value
    state[STATE_KEYS["requirements"]] = None
    state[STATE_KEYS["research"]] = None
    state[STATE_KEYS["itinerary"]] = None
    state[STATE_KEYS["last_error"]] = None
    return state
