"""
ACTIVITY AGENT
===============
Recommends activities based on user interests and preferences.

USES:
- TripPreferences from state (interests, travel_style, companions)
- find_places_nearby tool with filtering
- Themes: romantic, family-friendly, adventure, cultural, budget

KEY FEATURE: Interest-based filtering
- User says "I love food and museums" → prioritize food tours + museums
- Family with kids → filter for kid-friendly activities
- Adventure style → hiking, outdoor activities
"""

from google.adk.agents import Agent
from ..tools import find_places_nearby, get_current_datetime


def filter_activities_by_interest(
    activities: list,
    interests: list,
    companions: str = None,
    avoids: list = None
) -> dict:
    """
    Filter and score activities based on user preferences.
    
    Args:
        activities: List of activities from find_places_nearby
        interests: User interests like ["food", "museums", "hiking"]
        companions: Who's traveling (solo, couple, family_with_kids, etc.)
        avoids: Things to avoid like ["crowds", "long_walks"]
    
    Returns:
        Filtered and scored activities with recommendations
    """
    if not activities:
        return {"filtered": [], "message": "No activities to filter"}
    
    # Activity type mapping to interests
    interest_mapping = {
        "food": ["restaurant", "cafe", "bar", "bakery", "food_tour"],
        "museums": ["museum", "gallery", "art"],
        "history": ["museum", "monument", "historic", "temple", "palace"],
        "nature": ["park", "garden", "lake", "mountain", "beach"],
        "hiking": ["trail", "mountain", "park", "nature"],
        "shopping": ["mall", "market", "boutique", "shopping"],
        "nightlife": ["bar", "club", "nightclub", "pub"],
        "beaches": ["beach", "coast", "waterfront"],
        "adventure": ["adventure", "outdoor", "sports", "hiking"]
    }
    
    # Kid-friendly indicators
    kid_friendly = ["park", "zoo", "aquarium", "museum", "beach", "garden"]
    
    # Romantic indicators
    romantic = ["restaurant", "spa", "garden", "sunset", "rooftop"]
    
    scored = []
    for activity in activities:
        name_lower = activity.get("name", "").lower()
        activity_type = activity.get("type", "").lower()
        
        score = 0
        tags = []
        
        # Score by interests
        for interest in interests:
            if interest.lower() in interest_mapping:
                for keyword in interest_mapping[interest.lower()]:
                    if keyword in name_lower or keyword in activity_type:
                        score += 10
                        tags.append(interest)
                        break
        
        # Companion-based scoring
        if companions == "family_with_kids":
            for kf in kid_friendly:
                if kf in name_lower:
                    score += 5
                    tags.append("kid-friendly")
                    break
        elif companions == "couple":
            for r in romantic:
                if r in name_lower:
                    score += 5
                    tags.append("romantic")
                    break
        
        # Penalty for avoids
        if avoids:
            for avoid in avoids:
                if avoid.lower() in name_lower:
                    score -= 10
        
        scored.append({
            **activity,
            "match_score": score,
            "tags": list(set(tags))
        })
    
    # Sort by score
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {
        "total": len(scored),
        "top_matches": scored[:5],
        "all_filtered": scored
    }


activity_agent = Agent(
    name="activity_agent",
    model="gemini-2.5-flash",
    tools=[find_places_nearby, filter_activities_by_interest],
    
    instruction="""
    You are an Activity Recommendation Agent.
    Your job is to suggest activities tailored to user preferences.
    
    AVAILABLE TOOLS:
    - find_places_nearby: Find attractions, restaurants, etc. by location
    - filter_activities_by_interest: Score activities by user interests
    
    USER PREFERENCES TO CONSIDER:
    - Interests: food, museums, hiking, nightlife, shopping, beaches, etc.
    - Companions: solo, couple, family_with_kids, friends
    - Travel style: adventure, relaxed, cultural, luxury
    - Avoids: crowds, long_walks, spicy_food, etc.
    
    YOUR PROCESS:
    
    1. Check user preferences from context/state
    2. Use find_places_nearby to get activities for the destination
    3. Use filter_activities_by_interest to score and rank them
    4. Recommend top activities with explanations
    
    OUTPUT FORMAT:
    For each recommended activity:
    - Name and type
    - Why it matches their preferences (e.g., "Perfect for food lovers!")
    - Best time to visit
    - Any tips
    
    THEMES TO APPLY:
    - "romantic" → candlelit restaurants, sunset spots, spas
    - "family-friendly" → parks, zoos, interactive museums
    - "adventure" → hiking, water sports, outdoor activities
    - "cultural" → museums, temples, historical sites
    - "budget" → free parks, walking tours, street food
    
    If user says "kid-friendly", prioritize:
    - Parks and playgrounds
    - Interactive museums
    - Aquariums/zoos
    - Avoid bars/nightlife
    """
)
