"""
STATE TOOLS - Session State Management
=======================================
Tools for persisting data to session state.

USED BY: Clarifier Agent

KEY TOOL: update_trip_preferences
- Saves user preferences to session.state
- Allows other agents to read saved preferences
- Tracks confidence levels for each field

This is how the Clarifier "communicates" gathered info to other agents.
"""

from google.adk.tools import FunctionTool
from typing import Optional


def update_trip_preferences(
    destination: Optional[str] = None,
    budget: Optional[str] = None,
    dates: Optional[str] = None,
    preferences: Optional[str] = None,
    destination_confidence: str = "high",
    budget_confidence: str = "high",
    dates_confidence: str = "high"
) -> dict:
    """
    Save user's trip preferences to session state.
    Called by Clarifier to persist gathered information.
    
    Args:
        destination: Travel destination (e.g., "Tokyo, Japan")
        budget: Budget amount or level (e.g., "$3000", "mid-range", "luxury")
        dates: Travel dates or duration (e.g., "January 15-22", "3 days")
        preferences: Additional preferences (e.g., "family-friendly, cultural, food tours")
        destination_confidence: Confidence level - "high", "medium", or "low"
        budget_confidence: Confidence level - "high", "medium", or "low"
        dates_confidence: Confidence level - "high", "medium", or "low"
    
    Returns:
        Confirmation of what was saved with confidence levels
    
    Note:
        In ADK, this function receives a ToolContext automatically when
        decorated with @tool_context. The context provides access to 
        session.state for persistence.
    """
    saved = {}
    confidence = {}
    
    if destination:
        saved["destination"] = destination
        confidence["destination"] = destination_confidence
    
    if budget:
        saved["budget"] = budget
        confidence["budget"] = budget_confidence
    
    if dates:
        saved["dates"] = dates
        confidence["dates"] = dates_confidence
    
    if preferences:
        saved["preferences"] = preferences
    
    # Track what fields have low confidence (were assumed)
    low_confidence_fields = [
        field for field, conf in confidence.items() 
        if conf == "low"
    ]
    
    return {
        "status": "saved",
        "saved_fields": saved,
        "confidence": confidence,
        "low_confidence_warning": low_confidence_fields if low_confidence_fields else None,
        "instruction": "These preferences are now available to other agents via session state"
    }


def get_trip_preferences() -> dict:
    """
    Retrieve currently saved trip preferences.
    Used by Research and Builder agents to access saved state.
    
    Returns:
        Dictionary of saved preferences or empty if none set
    
    Note:
        This would read from ToolContext.state in production.
        Currently returns a placeholder showing the expected structure.
    """
    return {
        "instruction": "Read from session.state keys: user:destination, user:budget, user:dates, user:preferences",
        "expected_keys": {
            "user:destination": "The travel destination",
            "user:destination_confidence": "high/medium/low",
            "user:budget": "Budget amount or level",
            "user:budget_confidence": "high/medium/low", 
            "user:dates": "Travel dates",
            "user:dates_confidence": "high/medium/low",
            "user:preferences": "Additional preferences"
        }
    }


# Wrap as ADK FunctionTools
update_trip_preferences_tool = FunctionTool(update_trip_preferences)
get_trip_preferences_tool = FunctionTool(get_trip_preferences)
