"""
VALIDATION TOOLS - Input Validation
====================================
Tools for validating and correcting user input.

USED BY: Clarifier Agent

KEY TOOL: validate_destination
- Fixes typos like "Tokio" → "Tokyo"
- Uses Places Autocomplete for accurate matches
- Returns standardized destination names

NOTE: Using synchronous requests for Google AI API compatibility.
"""

from google.adk.tools import FunctionTool
from typing import Optional
import os
import re

# Use requests (sync) instead of httpx (async) for compatibility
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# Common destination corrections (fallback if API unavailable)
COMMON_CORRECTIONS = {
    "tokio": "Tokyo, Japan",
    "tokyo": "Tokyo, Japan",
    "paris": "Paris, France",
    "newyork": "New York, USA",
    "new york": "New York, USA",
    "nyc": "New York, USA",
    "la": "Los Angeles, USA",
    "sf": "San Francisco, USA",
    "san fran": "San Francisco, USA",
    "london": "London, United Kingdom",
    "rome": "Rome, Italy",
    "barcelona": "Barcelona, Spain",
    "bangkok": "Bangkok, Thailand",
    "singapore": "Singapore",
    "sydney": "Sydney, Australia",
    "dubai": "Dubai, UAE",
    "bali": "Bali, Indonesia",
    "switzerland": "Switzerland",
    "swiss": "Switzerland",
}


def validate_destination(query: str) -> dict:
    """
    Validate and autocomplete destination names.
    Fixes typos and returns standardized location names.
    
    Args:
        query: User's destination input (e.g., "Tokio", "sf", "paris")
    
    Returns:
        Validated destination with confidence and alternatives
    """
    query_cleaned = query.strip().lower()
    
    # Check common corrections first
    if query_cleaned in COMMON_CORRECTIONS:
        return {
            "valid": True,
            "original": query,
            "corrected": COMMON_CORRECTIONS[query_cleaned],
            "confidence": "high",
            "source": "common_corrections"
        }
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key or not HAS_REQUESTS:
        # Fallback: basic validation + common corrections
        if len(query.strip()) < 2:
            return {
                "valid": False,
                "original": query,
                "error": "Destination name too short"
            }
        
        # Capitalize properly
        corrected = query.strip().title()
        return {
            "valid": True,
            "original": query,
            "corrected": corrected,
            "confidence": "medium",
            "source": "basic_validation"
        }
    
    # Use Google Places Autocomplete (sync)
    url = "https://places.googleapis.com/v1/places:autocomplete"
    
    try:
        response = requests.post(
            url,
            headers={
                "X-Goog-Api-Key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "input": query,
                "includedPrimaryTypes": ["locality", "administrative_area_level_1", "country"]
            },
            timeout=10
        )
        
        if response.status_code != 200:
            return {
                "valid": True,
                "original": query,
                "corrected": query.strip().title(),
                "confidence": "low"
            }
        
        data = response.json()
    except Exception as e:
        return {
            "valid": True,
            "original": query,
            "corrected": query.strip().title(),
            "confidence": "low"
        }
    
    suggestions = data.get("suggestions", [])
    
    if not suggestions:
        # No results, but assume user input is valid
        return {
            "valid": True,
            "original": query,
            "corrected": query.strip().title(),
            "confidence": "low"
        }
    
    # Get top suggestion
    top = suggestions[0].get("placePrediction", {})
    corrected_text = top.get("text", {}).get("text", query.title())
    
    # Calculate confidence
    if query.lower() in corrected_text.lower():
        confidence = "high"
    else:
        confidence = "medium"
    
    return {
        "valid": True,
        "original": query,
        "corrected": corrected_text,
        "confidence": confidence
    }


def validate_budget(budget_input: str) -> dict:
    """
    Validate and normalize budget input.
    Converts various formats to standardized representation.
    
    Args:
        budget_input: User's budget (e.g., "$5000", "5k", "mid-range", "luxury")
    
    Returns:
        Standardized budget with category
    """
    budget_lower = budget_input.lower().strip()
    
    # Handle descriptive budgets
    budget_categories = {
        "budget": {"level": "budget", "range": "$50-100/day", "total_estimate": "$300-600"},
        "cheap": {"level": "budget", "range": "$50-100/day", "total_estimate": "$300-600"},
        "low": {"level": "budget", "range": "$50-100/day", "total_estimate": "$300-600"},
        "mid-range": {"level": "mid-range", "range": "$100-250/day", "total_estimate": "$600-1500"},
        "moderate": {"level": "mid-range", "range": "$100-250/day", "total_estimate": "$600-1500"},
        "medium": {"level": "mid-range", "range": "$100-250/day", "total_estimate": "$600-1500"},
        "luxury": {"level": "luxury", "range": "$300-500+/day", "total_estimate": "$1800-3000+"},
        "high-end": {"level": "luxury", "range": "$300-500+/day", "total_estimate": "$1800-3000+"},
        "expensive": {"level": "luxury", "range": "$300-500+/day", "total_estimate": "$1800-3000+"},
        "no budget": {"level": "luxury", "range": "No limit", "total_estimate": "Open"},
        "unlimited": {"level": "luxury", "range": "No limit", "total_estimate": "Open"},
    }
    
    for keyword, category in budget_categories.items():
        if keyword in budget_lower:
            return {
                "valid": True,
                "original": budget_input,
                "normalized": category["level"],
                "daily_range": category["range"],
                "total_estimate": category["total_estimate"],
                "confidence": "high"
            }
    
    # Try to extract numeric amount
    # Match patterns like: ₹5000, 5000, 5k, ₹5k, 50000, 1L, 1.5L
    amount_match = re.search(r'[₹$€£]?\s*(\d+(?:,\d{3})*(?:\.\d{1,2})?)\s*([kKlL])?', budget_input)
    
    if amount_match:
        amount = float(amount_match.group(1).replace(',', ''))
        multiplier = amount_match.group(2)
        if multiplier:
            if multiplier.lower() == 'k':
                amount *= 1000
            elif multiplier.lower() == 'l':  # Lakh
                amount *= 100000
        
        # Categorize based on amount (INR)
        if amount < 50000:
            level = "budget"
        elif amount < 150000:
            level = "mid-range"
        else:
            level = "luxury"
        
        return {
            "valid": True,
            "original": budget_input,
            "amount": amount,
            "normalized": f"₹{amount:,.0f}",
            "level": level,
            "confidence": "high"
        }
    
    # Can't parse
    return {
        "valid": False,
        "original": budget_input,
        "error": "Could not parse budget. Use format like '₹50000', '50k', '1.5L', or 'mid-range'"
    }


# Wrap as ADK FunctionTools
validate_destination_tool = FunctionTool(validate_destination)
validate_budget_tool = FunctionTool(validate_budget)
