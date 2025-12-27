"""
SEARCH TOOLS - Vertex AI Search Grounding
==========================================
Provides grounded search capabilities for the Research Agent.

WHY VERTEX AI SEARCH GROUNDING:
- More accurate than basic google_search
- Returns citations and sources
- Can be configured for specific domains (travel, weather, etc.)
- Reduces hallucinations by grounding responses in real data

NOTE: The built-in google_search tool from ADK already uses Google Search grounding.
For Vertex AI Search with custom datastores, you'd need to configure a datastore ID.
"""

from google.adk.tools import FunctionTool, google_search
from typing import Optional
import os


# Re-export the built-in google_search tool
# This uses Google Search with grounding enabled automatically
grounded_search_tool = google_search


def search_travel_info(
    query: str,
    destination: Optional[str] = None,
    category: Optional[str] = None
) -> dict:
    """
    Search for travel-related information with context.
    Wrapper that enhances queries for better travel results.
    
    Args:
        query: The search query (e.g., "weather", "events December", "visa requirements")
        destination: Optional destination to include in search context
        category: Optional category hint: "weather", "events", "flights", "visa", "safety"
    
    Returns:
        Enhanced search query ready to pass to google_search
    """
    # Enhance the query with travel context
    enhanced_parts = []
    
    if destination:
        enhanced_parts.append(destination)
    
    enhanced_parts.append(query)
    
    # Add category-specific enhancements
    if category:
        category_hints = {
            "weather": "weather forecast",
            "events": "events festivals activities",
            "flights": "flight prices airlines",
            "visa": "visa requirements entry",
            "safety": "travel safety advisories"
        }
        if category.lower() in category_hints:
            enhanced_parts.append(category_hints[category.lower()])
    
    enhanced_query = " ".join(enhanced_parts)
    
    return {
        "enhanced_query": enhanced_query,
        "original_query": query,
        "destination": destination,
        "category": category,
        "instruction": "Use the google_search tool with the enhanced_query"
    }


def search_transport(
    origin: str,
    destination: str,
    travel_date: Optional[str] = None,
    transport_type: str = "flight"
) -> dict:
    """
    Search for transportation options between locations.
    
    Args:
        origin: Starting city/airport
        destination: Ending city/airport
        travel_date: Optional date in YYYY-MM-DD format
        transport_type: "flight", "train", "bus"
    
    Returns:
        Search query and context for transport search
    """
    query_parts = [transport_type, "from", origin, "to", destination]
    
    if travel_date:
        query_parts.extend(["on", travel_date])
    
    query_parts.append("prices booking")
    
    return {
        "search_query": " ".join(query_parts),
        "origin": origin,
        "destination": destination,
        "date": travel_date,
        "transport_type": transport_type,
        "instruction": "Use google_search with the search_query to find options"
    }


# Wrap as ADK FunctionTools
search_travel_info_tool = FunctionTool(search_travel_info)
search_transport_tool = FunctionTool(search_transport)
