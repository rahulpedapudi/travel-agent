"""
ACTIVITY AGENT
===============
Recommends activities based on user interests.
"""

from google.adk.agents import Agent
from ..tools import find_places_nearby


def filter_activities_by_interest(
    activities: list,
    interests: list,
    companions: str = None,
    avoids: list = None
) -> dict:
    """Filter activities by user preferences."""
    if not activities:
        return {"filtered": [], "message": "No activities to filter"}
    
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
    
    kid_friendly = ["park", "zoo", "aquarium", "museum", "beach", "garden"]
    romantic = ["restaurant", "spa", "garden", "sunset", "rooftop"]
    
    scored = []
    for activity in activities:
        name_lower = activity.get("name", "").lower()
        activity_type = activity.get("type", "").lower()
        
        score = 0
        tags = []
        
        for interest in interests:
            if interest.lower() in interest_mapping:
                for keyword in interest_mapping[interest.lower()]:
                    if keyword in name_lower or keyword in activity_type:
                        score += 10
                        tags.append(interest)
                        break
        
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
        
        if avoids:
            for avoid in avoids:
                if avoid.lower() in name_lower:
                    score -= 10
        
        scored.append({**activity, "match_score": score, "tags": list(set(tags))})
    
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return {"total": len(scored), "top_matches": scored[:5], "all_filtered": scored}


activity_agent = Agent(
    name="activity_agent",
    model="gemini-2.5-flash",
    tools=[find_places_nearby, filter_activities_by_interest],
    
    instruction="""
    You recommend activities based on what the user enjoys.
    
    LANGUAGE RULES - VERY IMPORTANT:
    - NEVER mention "tools", "filters", "algorithms"
    - NEVER say "based on my search" or "my filtering shows"
    - Talk like a friend who knows great spots
    
    ❌ DON'T SAY: "Based on your interest filters, I found..."
    ✅ SAY: "Since you love food, you'll definitely want to try..."
    
    ❌ DON'T SAY: "The activity matching algorithm suggests..."
    ✅ SAY: "For a romantic dinner, I'd pick..."
    
    YOUR JOB:
    Based on user's interests (food, museums, nightlife, etc.), recommend:
    - Things that match what they enjoy
    - Kid-friendly spots if traveling with family
    - Romantic options for couples
    - Avoid things they said they don't like
    
    OUTPUT (conversational):
    
    "Since you mentioned you love [interest], here's what I'd recommend:
    
    🍜 For foodies:
    - [Restaurant] - This place is amazing for [dish]!
    
    🏛️ Culture lovers will enjoy:
    - [Museum] - Don't miss the [exhibit]
    
    🌙 For nightlife:
    - [Bar/Club] - Great vibe, especially on weekends"
    
    Make it personal and enthusiastic!
    """
)
