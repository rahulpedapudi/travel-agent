"""
FLIGHT TOOLS - Search and display flight options.
Currently uses mock data. Replace with real API (Amadeus/Skyscanner) for production.
"""

from typing import Optional, List
import json
import random
from datetime import datetime, timedelta


# Mock airline data
MOCK_AIRLINES = [
    {"code": "AI", "name": "Air India", "logo": "🇮🇳"},
    {"code": "6E", "name": "IndiGo", "logo": "✈️"},
    {"code": "SG", "name": "SpiceJet", "logo": "🌶️"},
    {"code": "UK", "name": "Vistara", "logo": "⭐"},
    {"code": "EK", "name": "Emirates", "logo": "🇦🇪"},
    {"code": "SQ", "name": "Singapore Airlines", "logo": "🇸🇬"},
    {"code": "TG", "name": "Thai Airways", "logo": "🇹🇭"},
    {"code": "NH", "name": "ANA", "logo": "🇯🇵"},
]

# Mock airport codes by city
AIRPORT_CODES = {
    "delhi": {"code": "DEL", "name": "Indira Gandhi International"},
    "mumbai": {"code": "BOM", "name": "Chhatrapati Shivaji International"},
    "bangalore": {"code": "BLR", "name": "Kempegowda International"},
    "chennai": {"code": "MAA", "name": "Chennai International"},
    "kolkata": {"code": "CCU", "name": "Netaji Subhas Chandra Bose"},
    "hyderabad": {"code": "HYD", "name": "Rajiv Gandhi International"},
    "tokyo": {"code": "NRT", "name": "Narita International"},
    "paris": {"code": "CDG", "name": "Charles de Gaulle"},
    "london": {"code": "LHR", "name": "Heathrow"},
    "new york": {"code": "JFK", "name": "John F. Kennedy"},
    "dubai": {"code": "DXB", "name": "Dubai International"},
    "singapore": {"code": "SIN", "name": "Changi"},
    "bangkok": {"code": "BKK", "name": "Suvarnabhumi"},
    "bali": {"code": "DPS", "name": "Ngurah Rai International"},
    "goa": {"code": "GOI", "name": "Goa International"},
}


def _get_airport(city: str) -> dict:
    """Get airport info for a city."""
    city_lower = city.lower().strip()
    if city_lower in AIRPORT_CODES:
        return {
            "code": AIRPORT_CODES[city_lower]["code"],
            "name": AIRPORT_CODES[city_lower]["name"],
            "city": city.title()
        }
    # Default fallback
    return {
        "code": city[:3].upper(),
        "name": f"{city.title()} Airport",
        "city": city.title()
    }


def _format_price(amount: float) -> str:
    """Format price in INR."""
    if amount >= 100000:
        return f"₹{amount/100000:.1f}L"
    elif amount >= 1000:
        return f"₹{amount/1000:.0f}K"
    else:
        return f"₹{amount:.0f}"


def _generate_mock_flights(origin: str, destination: str, date: str, count: int = 4) -> List[dict]:
    """Generate mock flight options."""
    origin_airport = _get_airport(origin)
    dest_airport = _get_airport(destination)
    
    flights = []
    base_price = random.randint(15000, 45000)
    
    # Generate departure times throughout the day
    departure_hours = [6, 9, 12, 15, 18, 21]
    random.shuffle(departure_hours)
    
    for i in range(min(count, len(departure_hours))):
        airline = random.choice(MOCK_AIRLINES)
        dep_hour = departure_hours[i]
        dep_minute = random.choice([0, 15, 30, 45])
        
        # Calculate duration (3-12 hours depending on route)
        is_domestic = origin.lower() in ["delhi", "mumbai", "bangalore", "chennai", "kolkata", "hyderabad", "goa"]
        is_domestic = is_domestic and destination.lower() in ["delhi", "mumbai", "bangalore", "chennai", "kolkata", "hyderabad", "goa"]
        
        if is_domestic:
            duration_hours = random.randint(2, 4)
        else:
            duration_hours = random.randint(5, 12)
        
        duration_minutes = random.choice([0, 15, 30, 45])
        total_minutes = duration_hours * 60 + duration_minutes
        
        # Calculate arrival time
        arr_hour = (dep_hour + duration_hours + (dep_minute + duration_minutes) // 60) % 24
        arr_minute = (dep_minute + duration_minutes) % 60
        
        # Determine if direct or with stops
        stops = 0 if duration_hours <= 6 else random.choice([0, 1])
        
        # Price variation
        price = base_price + random.randint(-5000, 10000)
        if stops == 0:
            price += 3000  # Direct flights cost more
        
        flight = {
            "id": f"FL{i+1}{airline['code']}{random.randint(100, 999)}",
            "segments": [
                {
                    "departure_airport": origin_airport["code"],
                    "departure_city": origin_airport["city"],
                    "departure_time": f"{dep_hour:02d}:{dep_minute:02d}",
                    "arrival_airport": dest_airport["code"],
                    "arrival_city": dest_airport["city"],
                    "arrival_time": f"{arr_hour:02d}:{arr_minute:02d}",
                    "duration": f"{duration_hours}h {duration_minutes}m",
                    "airline": airline["name"],
                    "flight_number": f"{airline['code']}{random.randint(100, 999)}",
                    "aircraft": random.choice(["Boeing 787", "Airbus A320", "Boeing 777", "Airbus A350"]),
                    "cabin_class": "Economy"
                }
            ],
            "total_duration": f"{duration_hours}h {duration_minutes}m",
            "stops": stops,
            "price": price,
            "currency": "INR",
            "price_formatted": _format_price(price),
            "booking_class": "Economy"
        }
        
        flights.append(flight)
    
    # Sort by price
    flights.sort(key=lambda x: x["price"])
    return flights


def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1
) -> str:
    """
    Search for flights between two cities.
    Currently returns mock data. Replace with real API for production.
    
    Args:
        origin: Departure city, e.g., "Delhi", "Mumbai"
        destination: Arrival city, e.g., "Tokyo", "Paris"
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Optional return date for round trips
        passengers: Number of passengers (default 1)
    
    Returns:
        JSON with flight options and UI component.
    
    Example:
        search_flights("Delhi", "Tokyo", "2026-01-15", passengers=2)
    """
    # Generate mock flights
    outbound_flights = _generate_mock_flights(origin, destination, departure_date)
    
    return_flights = []
    if return_date:
        return_flights = _generate_mock_flights(destination, origin, return_date)
    
    return json.dumps({
        "flights": {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": passengers,
            "outbound": outbound_flights,
            "return": return_flights if return_date else None,
            "currency": "INR"
        },
        "ui_component": {
            "type": "flight_card",
            "props": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "passengers": passengers,
                "flights": outbound_flights,
                "show_return": bool(return_date)
            },
            "required": False
        }
    })


def render_flights(
    flights: List[dict],
    origin: str,
    destination: str,
    departure_date: str
) -> str:
    """
    Render a flight card UI component with pre-fetched flight data.
    
    Args:
        flights: List of flight options (from search_flights)
        origin: Origin city
        destination: Destination city
        departure_date: Date in YYYY-MM-DD
    
    Returns:
        JSON with flight_card UI component.
    """
    return json.dumps({
        "ui_component": {
            "type": "flight_card",
            "props": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "flights": flights,
                "show_return": False
            },
            "required": False
        }
    })
