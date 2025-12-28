"""
PLACES TOOLS - Google Maps Places API
======================================
Find hotels, restaurants, and attractions using Google Places API.

CACHING: Results are cached for 24 hours to:
- Reduce API costs
- Speed up repeated searches
- Enable fast refinements

USED BY: Research Agent
"""

from google.adk.tools import FunctionTool
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

# Import cache
try:
    from ..cache import get_cached_places, set_cached_places
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("Cache not available")

# Use requests (sync) instead of httpx (async) for compatibility
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def find_places_nearby(
    location: str,
    place_type: str,
    max_results: int = 5,
    skip_cache: bool = False
) -> dict:
    """
    Find hotels, restaurants, or attractions near a location.
    Returns structured data with ratings, prices, and addresses.
    
    Results are cached for 24 hours to improve performance.
    
    Args:
        location: City or area to search (e.g., "Tokyo, Japan", "Paris city center")
        place_type: Type of place to find. Common types include:
            - Travel: "hotel", "restaurant", "attraction", "cafe", "museum", "spa", "bar", "park"
            - Utilities: "bank", "atm", "pharmacy", "hospital", "gas_station"
            - Shopping: "shopping_mall", "supermarket", "convenience_store"
            - Transport: "train_station", "bus_station", "airport"
        max_results: Maximum number of results (1-10, default 5)
        skip_cache: Force fresh fetch (default False)
    
    Returns:
        List of places with name, rating, price_level, address
    """
    # Check cache first
    if CACHE_AVAILABLE and not skip_cache:
        cached = get_cached_places(location, place_type)
        if cached:
            logger.debug(f"Cache hit: {location} {place_type}")
            return {
                "query": f"{place_type} in {location}",
                "result_count": len(cached["places"]),
                "places": cached["places"],
                "cached": True
            }
    
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
        # Travel/Hospitality
        "hotel": "lodging",
        "lodging": "lodging",
        "restaurant": "restaurant",
        "attraction": "tourist_attraction",
        "cafe": "cafe",
        "museum": "museum",
        "spa": "spa",
        "bar": "bar",
        "park": "park",
        # Utilities
        "bank": "bank",
        "atm": "atm",
        "pharmacy": "pharmacy",
        "hospital": "hospital",
        "gas_station": "gas_station",
        "shopping_mall": "shopping_mall",
        "supermarket": "supermarket",
        "convenience_store": "convenience_store",
        # Transport
        "train_station": "train_station",
        "bus_station": "bus_station",
        "airport": "airport",
    }
    
    included_type = type_mapping.get(place_type.lower(), place_type)
    url = "https://places.googleapis.com/v1/places:searchText"
    
    try:
        response = requests.post(
            url,
            headers={
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.displayName,places.rating,places.priceLevel,places.formattedAddress,places.location"
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
    
    # Parse results into structured format
    places = []
    for i, p in enumerate(data.get("places", [])):
        loc = p.get("location", {})
        places.append({
            "id": f"{place_type[:3]}_{i+1}",
            "name": p.get("displayName", {}).get("text", "Unknown"),
            "type": place_type,
            "rating": p.get("rating"),
            "price_level": p.get("priceLevel", "UNSPECIFIED"),
            "address": p.get("formattedAddress"),
            "lat": loc.get("latitude"),
            "lng": loc.get("longitude")
        })
    
    result = {
        "query": f"{place_type} in {location}",
        "result_count": len(places),
        "places": places,
        "cached": False
    }
    
    # Cache the results
    if CACHE_AVAILABLE and places:
        set_cached_places(location, place_type, result)
        logger.debug(f"Cached: {location} {place_type}")
    
    return result


# Export as FunctionTool
find_places_nearby_tool = FunctionTool(find_places_nearby)
