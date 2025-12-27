"""State management package - exports session utilities."""
from .session import (
    WorkflowPhase,
    ConfidenceLevel,
    RequirementConfidence,
    TravelRequirements,
    ResearchData,
    STATE_KEYS,
    DEFAULT_BUDGET,
    DEFAULT_DURATION,
    initialize_session_state
)

__all__ = [
    "WorkflowPhase",
    "ConfidenceLevel",
    "RequirementConfidence",
    "TravelRequirements", 
    "ResearchData",
    "STATE_KEYS",
    "DEFAULT_BUDGET",
    "DEFAULT_DURATION",
    "initialize_session_state"
]
