"""
EXTRACTION TOOLS - Entity Extraction for Slot Filling
======================================================
Parse user input to extract travel entities BEFORE asking questions.

WHY THIS MATTERS:
- User says: "3-day trip to Tokyo next week with my wife, budget around 50k"
- BAD: Agent asks "Where do you want to go?"
- GOOD: Agent extracts {destination: Tokyo, duration: 3, companions: couple, budget: 50000}
         and only asks for MISSING info

This is slot-filling, not interrogation.
"""

import re
from typing import Optional, List, Dict
from datetime import datetime, timedelta


def extract_trip_entities(user_input: str) -> dict:
    """
    Extract travel entities from natural language user input.
    
    Args:
        user_input: User's message, e.g., "3-day trip to Tokyo next week with my wife"
    
    Returns:
        Dictionary of extracted entities with confidence levels:
        {
            "destination": {"value": "Tokyo", "confidence": "high"},
            "duration_days": {"value": 3, "confidence": "high"},
            "companions": {"value": "couple", "confidence": "high"},
            "budget_amount": {"value": 50000, "confidence": "medium"},
            "interests": {"value": ["food"], "confidence": "medium"},
            "missing_required": ["dates"],  # What we still need to ask
            "missing_optional": ["hotel_style", "avoids"]
        }
    
    Example:
        Input: "Plan a 5-day family trip to Goa in February, budget 2 lakhs"
        Output: {
            destination: {value: "Goa", confidence: "high"},
            duration_days: {value: 5, confidence: "high"},
            companions: {value: "family_with_kids", confidence: "medium"},
            budget_amount: {value: 200000, confidence: "high"},
            start_date: {value: "2025-02-01", confidence: "low"},
            missing_required: [],
            missing_optional: ["interests", "hotel_style"]
        }
    """
    text = user_input.lower()
    extracted = {}
    
    # 1. DESTINATION EXTRACTION
    destination_patterns = [
        r"(?:to|visit|in|trip to|travel to|going to|vacation in|holiday in)\s+([a-z]+(?:\s+[a-z]+)?)",
        r"([a-z]+)\s+(?:trip|vacation|holiday|tour)",
    ]
    for pattern in destination_patterns:
        match = re.search(pattern, text)
        if match:
            dest = match.group(1).strip()
            # Filter out common false positives
            if dest not in ["a", "the", "my", "our", "i", "we", "next", "this"]:
                extracted["destination"] = {"value": dest.title(), "confidence": "high"}
                break
    
    # 2. DURATION EXTRACTION
    duration_patterns = [
        r"(\d+)\s*(?:day|days|night|nights)",
        r"(\d+)d\b",
        r"a\s+week",  # "a week" = 7 days
        r"weekend",   # "weekend" = 2-3 days
    ]
    for pattern in duration_patterns:
        match = re.search(pattern, text)
        if match:
            if "week" in pattern:
                extracted["duration_days"] = {"value": 7, "confidence": "high"}
            elif "weekend" in pattern:
                extracted["duration_days"] = {"value": 3, "confidence": "medium"}
            else:
                extracted["duration_days"] = {"value": int(match.group(1)), "confidence": "high"}
            break
    
    # 3. DATE EXTRACTION
    today = datetime.now()
    date_patterns = [
        (r"next\s+week", 7),
        (r"this\s+weekend", (5 - today.weekday()) % 7),  # Next Saturday
        (r"next\s+weekend", (5 - today.weekday()) % 7 + 7),
        (r"next\s+month", 30),
        (r"in\s+(\d+)\s+days", None),  # Dynamic
    ]
    for pattern, offset in date_patterns:
        match = re.search(pattern, text)
        if match:
            if offset is None:
                offset = int(match.group(1))
            start = today + timedelta(days=offset)
            extracted["start_date"] = {
                "value": start.strftime("%Y-%m-%d"),
                "confidence": "medium"
            }
            break
    
    # Month-based dates (e.g., "in February", "this December")
    months = ["january", "february", "march", "april", "may", "june", 
              "july", "august", "september", "october", "november", "december"]
    for i, month in enumerate(months):
        if month in text:
            year = today.year if i + 1 >= today.month else today.year + 1
            extracted["start_date"] = {
                "value": f"{year}-{i+1:02d}-01",
                "confidence": "low"
            }
            break
    
    # 4. BUDGET EXTRACTION
    budget_patterns = [
        (r"(\d+)\s*(?:lakh|lac|l)\b", lambda x: int(x) * 100000),
        (r"(\d+)\s*k\b", lambda x: int(x) * 1000),
        (r"(?:rs\.?|₹|inr)\s*(\d+(?:,\d+)*)", lambda x: int(x.replace(",", ""))),
        (r"(\d+(?:,\d+)*)\s*(?:rs|rupees|inr)", lambda x: int(x.replace(",", ""))),
        (r"budget\s*(?:of|around|is|:)?\s*(\d+(?:,\d+)*)", lambda x: int(x.replace(",", ""))),
    ]
    for pattern, converter in budget_patterns:
        match = re.search(pattern, text)
        if match:
            extracted["budget_amount"] = {
                "value": converter(match.group(1)),
                "confidence": "high"
            }
            break
    
    # Budget level keywords
    if "cheap" in text or "budget" in text:
        extracted["budget_level"] = {"value": "budget", "confidence": "medium"}
    elif "luxury" in text or "expensive" in text or "premium" in text:
        extracted["budget_level"] = {"value": "luxury", "confidence": "high"}
    elif "mid" in text or "moderate" in text:
        extracted["budget_level"] = {"value": "mid_range", "confidence": "medium"}
    
    # 5. COMPANIONS EXTRACTION
    if any(word in text for word in ["wife", "husband", "partner", "girlfriend", "boyfriend", "couple", "romantic", "honeymoon"]):
        extracted["companions"] = {"value": "couple", "confidence": "high"}
    elif any(word in text for word in ["family", "kids", "children", "son", "daughter"]):
        extracted["companions"] = {"value": "family_with_kids", "confidence": "high"}
    elif any(word in text for word in ["friends", "group", "gang", "buddies"]):
        extracted["companions"] = {"value": "friends", "confidence": "high"}
    elif any(word in text for word in ["solo", "alone", "myself", "by myself"]):
        extracted["companions"] = {"value": "solo", "confidence": "high"}
    elif any(word in text for word in ["parents", "mom", "dad", "family"]) and "kids" not in text:
        extracted["companions"] = {"value": "family_adults", "confidence": "medium"}
    
    # 6. INTERESTS EXTRACTION
    interests = []
    interest_keywords = {
        "food": ["food", "culinary", "eating", "restaurants", "cuisine", "foodie", "street food"],
        "museums": ["museum", "art", "gallery", "exhibition"],
        "history": ["history", "historical", "ancient", "heritage", "monuments"],
        "nature": ["nature", "outdoors", "scenic", "landscape", "mountains", "hills"],
        "beaches": ["beach", "beaches", "coast", "sea", "ocean", "island"],
        "adventure": ["adventure", "hiking", "trekking", "sports", "adrenaline"],
        "nightlife": ["nightlife", "party", "club", "bars", "nightclub", "pub"],
        "shopping": ["shopping", "markets", "mall", "buy"],
        "relaxation": ["relax", "spa", "wellness", "peaceful", "chill"]
    }
    for interest, keywords in interest_keywords.items():
        if any(kw in text for kw in keywords):
            interests.append(interest)
    
    if interests:
        extracted["interests"] = {"value": interests, "confidence": "high"}
    
    # 7. PACE/STYLE EXTRACTION
    if any(word in text for word in ["relaxed", "slow", "chill", "easy"]):
        extracted["pace"] = {"value": "relaxed", "confidence": "high"}
    elif any(word in text for word in ["packed", "busy", "everything", "max"]):
        extracted["pace"] = {"value": "packed", "confidence": "high"}
    
    # 8. HOTEL STYLE
    if any(word in text for word in ["5 star", "luxury hotel", "premium"]):
        extracted["hotel_style"] = {"value": "luxury", "confidence": "high"}
    elif any(word in text for word in ["boutique", "unique"]):
        extracted["hotel_style"] = {"value": "boutique", "confidence": "high"}
    elif any(word in text for word in ["airbnb", "rental", "apartment"]):
        extracted["hotel_style"] = {"value": "airbnb", "confidence": "high"}
    elif any(word in text for word in ["budget hotel", "cheap stay", "hostel"]):
        extracted["hotel_style"] = {"value": "budget", "confidence": "high"}
    
    # 9. SURPRISE ME MODE
    if any(phrase in text for phrase in ["surprise me", "you decide", "whatever you think", "best option"]):
        extracted["mode"] = {"value": "surprise_me", "confidence": "high"}
    
    # Determine what's missing
    required_fields = ["destination", "duration_days", "budget_amount"]
    optional_fields = ["companions", "interests", "hotel_style", "pace"]
    
    # Budget level can substitute for budget amount
    if "budget_level" in extracted and "budget_amount" not in extracted:
        required_fields.remove("budget_amount")
    
    extracted["missing_required"] = [f for f in required_fields if f not in extracted]
    extracted["missing_optional"] = [f for f in optional_fields if f not in extracted]
    
    # For surprise_me mode, nothing is really "missing"
    if extracted.get("mode", {}).get("value") == "surprise_me":
        extracted["missing_required"] = [f for f in ["destination"] if f not in extracted]
        extracted["missing_optional"] = []
    
    return extracted


def get_next_question(extracted: dict) -> dict:
    """
    Determine what question to ask next based on extracted entities.
    
    Returns:
        {
            "field": "dates",
            "question": "When are you planning to go?",
            "ui_component": "date_range_picker"
        }
    """
    # Priority order for required fields
    question_map = {
        "destination": {
            "question": "Where would you like to go?",
            "ui_component": None
        },
        "duration_days": {
            "question": "How many days are you planning for?",
            "ui_component": "date_range_picker"
        },
        "budget_amount": {
            "question": "What's your budget for this trip?",
            "ui_component": "budget_slider"
        },
        "companions": {
            "question": "Who's traveling with you?",
            "ui_component": "companion_selector"
        },
        "interests": {
            "question": "What kind of experiences are you interested in?",
            "ui_component": "preference_chips"
        }
    }
    
    # Check required first
    for field in extracted.get("missing_required", []):
        if field in question_map:
            return {
                "field": field,
                **question_map[field]
            }
    
    # Then optional (only top priority ones)
    priority_optional = ["companions", "interests"]
    for field in priority_optional:
        if field in extracted.get("missing_optional", []):
            return {
                "field": field,
                **question_map[field]
            }
    
    return {"field": None, "question": None, "complete": True}
