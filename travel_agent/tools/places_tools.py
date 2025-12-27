"""
PLACES TOOLS - Google Maps Places API
======================================
Find hotels, restaurants, and attractions using Google Places API.

USED BY: Research Agent

API ENDPOINT: places.googleapis.com/v1/places:searchText
REQUIRES: GOOGLE_MAPS_API_KEY in environment

NOTE: Using synchronous requests for Google AI API compatibility.
"""

from google.adk.tools import FunctionTool
from typing import Optional
import os

# Use requests (sync) instead of httpx (async) for compatibility
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def find_places_nearby(
    location: str,
    place_type: str,
    max_results: int = 5
) -> dict:
    """
    Find hotels, restaurants, or attractions near a location.
    Returns structured data with ratings, prices, and addresses.
    
    Args:
        location: City or area to search (e.g., "Tokyo, Japan", "Paris city center")
        place_type: Type of place to find: "hotel", "restaurant", "attraction", "cafe", "museum"
        max_results: Maximum number of results (1-10, default 5)
    
    Returns:
        List of places with name, rating, price_level, address
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return {
            "error": "GOOGLE_MAPS_API_KEY not set",
            "places": [],
            "fallback": f"Use google_search to find '{place_type} in {location}'"
        }
    
    if not HAS_REQUESTS:
        return {
            "error": "requests library not installed",
            "places": [],
            "fallback": f"Use google_search to find '{place_type} in {location}'"
        }
    
    # Map user-friendly types to Google Places API types
    type_mapping = {
        "hotel": "lodging",
        "lodging": "lodging",
        "restaurant": "restaurant",
        "attraction": "tourist_attraction",
        "cafe": "cafe",
        "museum": "museum",
        "spa": "spa",
        "bar": "bar",
        "park": "park"
    }
    
    included_type = type_mapping.get(place_type.lower(), place_type)
    url = "https://places.googleapis.com/v1/places:searchText"
    
    try:
        response = requests.post(
            url,
            headers={
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.displayName,places.rating,places.priceLevel,places.formattedAddress"
            },
            json={
                "textQuery": f"{place_type} in {location}",
                "includedType": included_type,
                "maxResultCount": min(max_results, 10)
            },
            timeout=15
        )
        
        if response.status_code != 200:
            return {
                "error": f"API error: {response.status_code}",
                "places": [],
                "fallback": f"Use google_search to find '{place_type} in {location}'"
            }
        
        data = response.json()
    except Exception as e:
        return {
            "error": str(e)[:100],
            "places": [],
            "fallback": f"Use google_search to find '{place_type} in {location}'"
        }
    
    # Parse results
    places = []
    for p in data.get("places", []):
        places.append({
            "name": p.get("displayName", {}).get("text", "Unknown"),
            "rating": p.get("rating"),
            "price_level": p.get("priceLevel", "UNSPECIFIED"),
            "address": p.get("formattedAddress")
        })
    
    return {
        "query": f"{place_type} in {location}",
        "result_count": len(places),
        "places": places
    }


# Export as FunctionTool
find_places_nearby_tool = FunctionTool(find_places_nearby)

