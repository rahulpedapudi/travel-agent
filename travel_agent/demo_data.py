"""
DEMO DATA - Pre-built responses for demo mode.
Bypasses LLM when DEMO_MODE=true in .env
"""

import json
import re
from typing import Optional, Tuple


# Destination detection patterns
DESTINATION_PATTERNS = {
    "mumbai": ["mumbai", "bombay", "gateway of india", "marine drive"],
    "tokyo": ["tokyo", "japan", "shibuya", "shinjuku", "akihabara"],
    "paris": ["paris", "france", "eiffel", "louvre"],
    "goa": ["goa", "beaches", "calangute", "baga"],
    "dubai": ["dubai", "uae", "burj khalifa", "emirates"],
}


def detect_destination(user_input: str) -> Optional[str]:
    """Detect destination from user input."""
    text = user_input.lower()
    for dest, keywords in DESTINATION_PATTERNS.items():
        if any(kw in text for kw in keywords):
            return dest
    return None


def get_demo_response(user_input: str, session_id: str) -> Optional[dict]:
    """
    Get a demo response based on user input.
    Returns None if no matching demo data.
    """
    dest = detect_destination(user_input)
    if not dest:
        return None
    
    data = DEMO_ITINERARIES.get(dest)
    if not data:
        return None
    
    return {
        "response": data["intro_text"],
        "session_id": session_id,
        "ui_components": data["ui_components"],
        "demo_mode": True
    }


# ============================================================
# MOCK ITINERARIES
# ============================================================

DEMO_ITINERARIES = {
    "mumbai": {
        "intro_text": """Perfect! I've put together an amazing 3-day Mumbai itinerary for you! 🌆

You'll experience the best of Mumbai - from iconic landmarks like the Gateway of India to the bustling streets of Colaba, delicious street food at Chowpatty Beach, and the vibrant nightlife of Bandra.

Here's your complete trip plan with flights, hotels, and day-by-day activities:""",
        
        "ui_components": [
            # Flight Card
            {
                "type": "flight_card",
                "props": {
                    "origin": "Delhi",
                    "destination": "Mumbai",
                    "departure_date": "2026-01-15",
                    "passengers": 2,
                    "flights": [
                        {
                            "id": "FL1AI302",
                            "segments": [{
                                "departure_airport": "DEL",
                                "departure_city": "Delhi",
                                "departure_time": "06:30",
                                "arrival_airport": "BOM",
                                "arrival_city": "Mumbai",
                                "arrival_time": "08:45",
                                "duration": "2h 15m",
                                "airline": "Air India",
                                "flight_number": "AI302",
                                "aircraft": "Airbus A320",
                                "cabin_class": "Economy"
                            }],
                            "total_duration": "2h 15m",
                            "stops": 0,
                            "price": 5500,
                            "currency": "INR",
                            "price_formatted": "₹5.5K",
                            "booking_class": "Economy"
                        },
                        {
                            "id": "FL26E205",
                            "segments": [{
                                "departure_airport": "DEL",
                                "departure_city": "Delhi",
                                "departure_time": "09:15",
                                "arrival_airport": "BOM",
                                "arrival_city": "Mumbai",
                                "arrival_time": "11:30",
                                "duration": "2h 15m",
                                "airline": "IndiGo",
                                "flight_number": "6E205",
                                "aircraft": "Airbus A321",
                                "cabin_class": "Economy"
                            }],
                            "total_duration": "2h 15m",
                            "stops": 0,
                            "price": 4800,
                            "currency": "INR",
                            "price_formatted": "₹4.8K",
                            "booking_class": "Economy"
                        }
                    ]
                }
            },
            # Itinerary Card
            {
                "type": "itinerary_card",
                "props": {
                    "days": [
                        {
                            "day_number": 1,
                            "date": "2026-01-15",
                            "theme": "South Mumbai Heritage",
                            "activities": [
                                {"start_time": "09:00", "duration": "1h", "title": "Arrival at Mumbai Airport", "location": "Chhatrapati Shivaji International Airport", "type": "transport"},
                                {"start_time": "10:30", "duration": "1h", "title": "Check-in at Taj Mahal Palace", "location": "Apollo Bunder, Colaba", "type": "hotel", "notes": ["Sea-facing heritage room"]},
                                {"start_time": "12:00", "duration": "1h 30m", "title": "Lunch at Leopold Cafe", "location": "Colaba Causeway", "type": "food", "notes": ["Try the butter chicken"]},
                                {"start_time": "14:00", "duration": "2h", "title": "Gateway of India", "location": "Apollo Bunder", "type": "attraction", "notes": ["Iconic colonial monument", "Great photo spot"]},
                                {"start_time": "16:30", "duration": "1h 30m", "title": "Colaba Causeway Shopping", "location": "Colaba", "type": "shopping"},
                                {"start_time": "18:30", "duration": "1h", "title": "Marine Drive Sunset Walk", "location": "Marine Drive", "type": "nature", "notes": ["Queen's Necklace view at dusk"]},
                                {"start_time": "20:00", "duration": "2h", "title": "Dinner at Trishna", "location": "Kala Ghoda", "type": "food", "notes": ["Famous butter garlic crab"]}
                            ]
                        },
                        {
                            "day_number": 2,
                            "date": "2026-01-16",
                            "theme": "Culture & Street Food",
                            "activities": [
                                {"start_time": "08:00", "duration": "1h", "title": "Breakfast at Hotel", "location": "Taj Mahal Palace", "type": "food"},
                                {"start_time": "09:30", "duration": "3h", "title": "Elephanta Caves", "location": "Elephanta Island", "type": "attraction", "notes": ["UNESCO World Heritage Site", "Ferry from Gateway"]},
                                {"start_time": "13:00", "duration": "1h", "title": "Lunch at Britannia & Co", "location": "Ballard Estate", "type": "food", "notes": ["Legendary berry pulao"]},
                                {"start_time": "14:30", "duration": "2h", "title": "Chhatrapati Shivaji Terminus", "location": "CST", "type": "attraction", "notes": ["Victorian Gothic architecture"]},
                                {"start_time": "17:00", "duration": "2h", "title": "Chowpatty Beach & Street Food", "location": "Girgaon Chowpatty", "type": "food", "notes": ["Pav bhaji", "Bhel puri", "Kulfi"]},
                                {"start_time": "19:30", "duration": "2h 30m", "title": "Dinner at Masala Library", "location": "Bandra Kurla Complex", "type": "food", "notes": ["Modern Indian molecular gastronomy"]}
                            ]
                        },
                        {
                            "day_number": 3,
                            "date": "2026-01-17",
                            "theme": "Bandra & Departure",
                            "activities": [
                                {"start_time": "08:00", "duration": "1h", "title": "Breakfast at Yoga House", "location": "Bandra", "type": "food"},
                                {"start_time": "09:30", "duration": "2h", "title": "Bandra-Worli Sea Link Drive", "location": "Bandra", "type": "attraction", "notes": ["Stunning cable-stayed bridge"]},
                                {"start_time": "12:00", "duration": "1h 30m", "title": "Lunch at Pali Village Cafe", "location": "Bandra West", "type": "food"},
                                {"start_time": "14:00", "duration": "2h", "title": "Bandra Bandstand & Carter Road", "location": "Bandra", "type": "nature", "notes": ["Celebrity spotting area"]},
                                {"start_time": "16:30", "duration": "1h", "title": "Check-out & Travel to Airport", "location": "Taj Mahal Palace", "type": "transport"},
                                {"start_time": "19:00", "duration": "2h 15m", "title": "Flight to Delhi", "location": "BOM → DEL", "type": "transport"}
                            ]
                        }
                    ]
                }
            },
            # Map View
            {
                "type": "map_view",
                "props": {
                    "center": {"lat": 18.9220, "lng": 72.8347},
                    "zoom": 12,
                    "title": "Mumbai Trip Locations",
                    "markers": [
                        {"lat": 18.9220, "lng": 72.8347, "title": "Gateway of India", "type": "attraction", "day": 1},
                        {"lat": 18.9217, "lng": 72.8332, "title": "Taj Mahal Palace", "type": "hotel", "day": 1},
                        {"lat": 18.9440, "lng": 72.8234, "title": "Marine Drive", "type": "attraction", "day": 1},
                        {"lat": 18.9633, "lng": 72.8088, "title": "Elephanta Caves Ferry", "type": "attraction", "day": 2},
                        {"lat": 18.9398, "lng": 72.8355, "title": "CST Station", "type": "attraction", "day": 2},
                        {"lat": 18.9548, "lng": 72.8147, "title": "Chowpatty Beach", "type": "food", "day": 2},
                        {"lat": 19.0596, "lng": 72.8295, "title": "Bandra Bandstand", "type": "attraction", "day": 3}
                    ]
                }
            }
        ]
    },
    
    "tokyo": {
        "intro_text": """Sugoi! I've crafted the ultimate 4-day Tokyo adventure for you! 🗼🇯🇵

From ancient temples to neon-lit streets, you'll experience the incredible contrast that makes Tokyo magical. I've included the best ramen spots, serene gardens, and exciting neighborhoods like Shibuya and Akihabara.

Here's your complete trip:""",
        
        "ui_components": [
            # Flight Card
            {
                "type": "flight_card",
                "props": {
                    "origin": "Delhi",
                    "destination": "Tokyo",
                    "departure_date": "2026-02-10",
                    "passengers": 2,
                    "flights": [
                        {
                            "id": "FL1NH828",
                            "segments": [{
                                "departure_airport": "DEL",
                                "departure_city": "Delhi",
                                "departure_time": "14:30",
                                "arrival_airport": "NRT",
                                "arrival_city": "Tokyo",
                                "arrival_time": "06:45",
                                "duration": "8h 15m",
                                "airline": "ANA",
                                "flight_number": "NH828",
                                "aircraft": "Boeing 787 Dreamliner",
                                "cabin_class": "Economy"
                            }],
                            "total_duration": "8h 15m",
                            "stops": 0,
                            "price": 48000,
                            "currency": "INR",
                            "price_formatted": "₹48K",
                            "booking_class": "Economy"
                        },
                        {
                            "id": "FL1AI306",
                            "segments": [{
                                "departure_airport": "DEL",
                                "departure_city": "Delhi",
                                "departure_time": "20:15",
                                "arrival_airport": "NRT",
                                "arrival_city": "Tokyo",
                                "arrival_time": "08:30",
                                "duration": "8h 15m",
                                "airline": "Air India",
                                "flight_number": "AI306",
                                "aircraft": "Boeing 777",
                                "cabin_class": "Economy"
                            }],
                            "total_duration": "8h 15m",
                            "stops": 0,
                            "price": 42000,
                            "currency": "INR",
                            "price_formatted": "₹42K",
                            "booking_class": "Economy"
                        }
                    ]
                }
            },
            # Itinerary Card
            {
                "type": "itinerary_card",
                "props": {
                    "days": [
                        {
                            "day_number": 1,
                            "date": "2026-02-10",
                            "theme": "Arrival & Shibuya",
                            "activities": [
                                {"start_time": "07:00", "duration": "2h", "title": "Arrival at Narita Airport", "location": "Narita International Airport", "type": "transport"},
                                {"start_time": "10:00", "duration": "1h", "title": "Check-in at Park Hyatt Tokyo", "location": "Shinjuku", "type": "hotel", "notes": ["Lost in Translation hotel", "52nd floor views"]},
                                {"start_time": "12:00", "duration": "1h", "title": "Ichiran Ramen Lunch", "location": "Shibuya", "type": "food", "notes": ["Solo booth dining experience"]},
                                {"start_time": "14:00", "duration": "2h", "title": "Shibuya Crossing & Hachiko", "location": "Shibuya Station", "type": "attraction", "notes": ["World's busiest crossing"]},
                                {"start_time": "16:30", "duration": "2h", "title": "Harajuku & Takeshita Street", "location": "Harajuku", "type": "shopping", "notes": ["Youth fashion hub", "Crepes!"]},
                                {"start_time": "19:00", "duration": "2h", "title": "Dinner at Gonpachi", "location": "Nishi-Azabu", "type": "food", "notes": ["Kill Bill restaurant", "Yakitori"]}
                            ]
                        },
                        {
                            "day_number": 2,
                            "date": "2026-02-11",
                            "theme": "Traditional Tokyo",
                            "activities": [
                                {"start_time": "06:00", "duration": "2h", "title": "Tsukiji Outer Market", "location": "Tsukiji", "type": "food", "notes": ["Fresh sushi breakfast", "Tamagoyaki"]},
                                {"start_time": "09:00", "duration": "2h", "title": "Senso-ji Temple", "location": "Asakusa", "type": "attraction", "notes": ["Tokyo's oldest temple", "Nakamise shopping street"]},
                                {"start_time": "12:00", "duration": "1h", "title": "Lunch at Asakusa Imahan", "location": "Asakusa", "type": "food", "notes": ["Sukiyaki since 1895"]},
                                {"start_time": "14:00", "duration": "2h", "title": "Tokyo Skytree", "location": "Sumida", "type": "attraction", "notes": ["634m tall observation deck"]},
                                {"start_time": "16:30", "duration": "2h", "title": "Ueno Park & Museums", "location": "Ueno", "type": "nature"},
                                {"start_time": "19:00", "duration": "2h", "title": "Dinner at Sushi Saito", "location": "Roppongi", "type": "food", "notes": ["3-Michelin star omakase"]}
                            ]
                        },
                        {
                            "day_number": 3,
                            "date": "2026-02-12",
                            "theme": "Pop Culture & Akihabara",
                            "activities": [
                                {"start_time": "09:00", "duration": "1h", "title": "Breakfast at Hotel", "location": "Park Hyatt Tokyo", "type": "food"},
                                {"start_time": "10:30", "duration": "3h", "title": "Akihabara Electric Town", "location": "Akihabara", "type": "shopping", "notes": ["Anime, manga, electronics"]},
                                {"start_time": "14:00", "duration": "1h 30m", "title": "Maid Cafe Experience", "location": "Akihabara", "type": "food"},
                                {"start_time": "16:00", "duration": "2h", "title": "teamLab Borderless", "location": "Odaiba", "type": "attraction", "notes": ["Digital art museum"]},
                                {"start_time": "18:30", "duration": "2h", "title": "Robot Restaurant Show", "location": "Shinjuku", "type": "attraction", "notes": ["Wild cyberpunk show"]},
                                {"start_time": "21:00", "duration": "2h", "title": "Golden Gai Bar Hopping", "location": "Shinjuku", "type": "food", "notes": ["Tiny themed bars"]}
                            ]
                        },
                        {
                            "day_number": 4,
                            "date": "2026-02-13",
                            "theme": "Departure",
                            "activities": [
                                {"start_time": "08:00", "duration": "1h", "title": "Breakfast & Check-out", "location": "Park Hyatt Tokyo", "type": "hotel"},
                                {"start_time": "09:30", "duration": "2h", "title": "Meiji Shrine", "location": "Shibuya", "type": "attraction", "notes": ["Peaceful forest shrine"]},
                                {"start_time": "12:00", "duration": "1h", "title": "Last Ramen at Fuunji", "location": "Shinjuku", "type": "food"},
                                {"start_time": "14:00", "duration": "2h", "title": "Travel to Narita Airport", "location": "Narita Express", "type": "transport"},
                                {"start_time": "17:00", "duration": "8h", "title": "Flight to Delhi", "location": "NRT → DEL", "type": "transport"}
                            ]
                        }
                    ]
                }
            },
            # Map View
            {
                "type": "map_view",
                "props": {
                    "center": {"lat": 35.6762, "lng": 139.6503},
                    "zoom": 11,
                    "title": "Tokyo Trip Locations",
                    "markers": [
                        {"lat": 35.6852, "lng": 139.7528, "title": "Park Hyatt Tokyo", "type": "hotel", "day": 1},
                        {"lat": 35.6595, "lng": 139.7004, "title": "Shibuya Crossing", "type": "attraction", "day": 1},
                        {"lat": 35.6702, "lng": 139.7030, "title": "Harajuku", "type": "shopping", "day": 1},
                        {"lat": 35.7148, "lng": 139.7967, "title": "Senso-ji Temple", "type": "attraction", "day": 2},
                        {"lat": 35.7101, "lng": 139.8107, "title": "Tokyo Skytree", "type": "attraction", "day": 2},
                        {"lat": 35.6984, "lng": 139.7731, "title": "Akihabara", "type": "shopping", "day": 3},
                        {"lat": 35.6264, "lng": 139.7798, "title": "teamLab Borderless", "type": "attraction", "day": 3}
                    ]
                }
            }
        ]
    },
    
    "paris": {
        "intro_text": """Magnifique! I've designed a romantic 3-day Paris escape for you! 🗼🇫🇷

From the iconic Eiffel Tower to charming Montmartre, you'll experience the City of Light at its finest. I've included the best patisseries, world-class museums, and quintessential Parisian experiences.

Voilà, your complete itinerary:""",
        
        "ui_components": [
            {
                "type": "flight_card",
                "props": {
                    "origin": "Delhi",
                    "destination": "Paris",
                    "departure_date": "2026-03-15",
                    "passengers": 2,
                    "flights": [
                        {
                            "id": "FL1AF226",
                            "segments": [{
                                "departure_airport": "DEL",
                                "departure_city": "Delhi",
                                "departure_time": "02:30",
                                "arrival_airport": "CDG",
                                "arrival_city": "Paris",
                                "arrival_time": "08:45",
                                "duration": "9h 15m",
                                "airline": "Air France",
                                "flight_number": "AF226",
                                "aircraft": "Airbus A350",
                                "cabin_class": "Economy"
                            }],
                            "total_duration": "9h 15m",
                            "stops": 0,
                            "price": 52000,
                            "currency": "INR",
                            "price_formatted": "₹52K",
                            "booking_class": "Economy"
                        }
                    ]
                }
            },
            {
                "type": "itinerary_card",
                "props": {
                    "days": [
                        {
                            "day_number": 1,
                            "date": "2026-03-15",
                            "theme": "Iconic Paris",
                            "activities": [
                                {"start_time": "09:00", "duration": "1h", "title": "Arrival at CDG", "location": "Charles de Gaulle Airport", "type": "transport"},
                                {"start_time": "11:00", "duration": "1h", "title": "Check-in at Le Meurice", "location": "1st Arrondissement", "type": "hotel"},
                                {"start_time": "12:30", "duration": "1h 30m", "title": "Lunch at Café de Flore", "location": "Saint-Germain-des-Prés", "type": "food"},
                                {"start_time": "14:30", "duration": "3h", "title": "Louvre Museum", "location": "1st Arrondissement", "type": "attraction", "notes": ["Mona Lisa", "Venus de Milo"]},
                                {"start_time": "18:00", "duration": "2h", "title": "Eiffel Tower Sunset", "location": "Champ de Mars", "type": "attraction"},
                                {"start_time": "20:30", "duration": "2h", "title": "Dinner at Le Jules Verne", "location": "Eiffel Tower", "type": "food", "notes": ["Michelin star dining"]}
                            ]
                        },
                        {
                            "day_number": 2,
                            "date": "2026-03-16",
                            "theme": "Art & Montmartre",
                            "activities": [
                                {"start_time": "08:30", "duration": "1h", "title": "Croissants at Pierre Hermé", "location": "Saint-Germain", "type": "food"},
                                {"start_time": "10:00", "duration": "3h", "title": "Musée d'Orsay", "location": "7th Arrondissement", "type": "attraction", "notes": ["Impressionist masterpieces"]},
                                {"start_time": "13:30", "duration": "1h 30m", "title": "Lunch at Bouillon Chartier", "location": "9th Arrondissement", "type": "food"},
                                {"start_time": "15:30", "duration": "3h", "title": "Montmartre & Sacré-Cœur", "location": "18th Arrondissement", "type": "attraction"},
                                {"start_time": "19:00", "duration": "2h 30m", "title": "Dinner at Pink Mamma", "location": "10th Arrondissement", "type": "food"}
                            ]
                        },
                        {
                            "day_number": 3,
                            "date": "2026-03-17",
                            "theme": "Departure",
                            "activities": [
                                {"start_time": "09:00", "duration": "1h", "title": "Breakfast & Check-out", "location": "Le Meurice", "type": "hotel"},
                                {"start_time": "10:30", "duration": "2h", "title": "Champs-Élysées & Arc de Triomphe", "location": "8th Arrondissement", "type": "attraction"},
                                {"start_time": "13:00", "duration": "1h 30m", "title": "Last Lunch at L'Avenue", "location": "Avenue Montaigne", "type": "food"},
                                {"start_time": "15:00", "duration": "1h 30m", "title": "Travel to CDG", "location": "RER B", "type": "transport"},
                                {"start_time": "18:30", "duration": "9h", "title": "Flight to Delhi", "location": "CDG → DEL", "type": "transport"}
                            ]
                        }
                    ]
                }
            },
            {
                "type": "map_view",
                "props": {
                    "center": {"lat": 48.8566, "lng": 2.3522},
                    "zoom": 12,
                    "title": "Paris Trip Locations",
                    "markers": [
                        {"lat": 48.8651, "lng": 2.3360, "title": "Le Meurice Hotel", "type": "hotel", "day": 1},
                        {"lat": 48.8606, "lng": 2.3376, "title": "Louvre Museum", "type": "attraction", "day": 1},
                        {"lat": 48.8584, "lng": 2.2945, "title": "Eiffel Tower", "type": "attraction", "day": 1},
                        {"lat": 48.8600, "lng": 2.3266, "title": "Musée d'Orsay", "type": "attraction", "day": 2},
                        {"lat": 48.8867, "lng": 2.3431, "title": "Sacré-Cœur", "type": "attraction", "day": 2},
                        {"lat": 48.8738, "lng": 2.2950, "title": "Arc de Triomphe", "type": "attraction", "day": 3}
                    ]
                }
            }
        ]
    },
    
    "goa": {
        "intro_text": """Susegad vibes incoming! 🏖️ I've planned the perfect 3-day Goa getaway for you!

Sun, sand, seafood, and stunning sunsets await. From the vibrant beaches of North Goa to Portuguese heritage in Old Goa, this trip has it all.

Here's your beach vacation:""",
        
        "ui_components": [
            {
                "type": "flight_card",
                "props": {
                    "origin": "Delhi",
                    "destination": "Goa",
                    "departure_date": "2026-01-20",
                    "passengers": 2,
                    "flights": [
                        {
                            "id": "FL16E101",
                            "segments": [{
                                "departure_airport": "DEL",
                                "departure_city": "Delhi",
                                "departure_time": "07:00",
                                "arrival_airport": "GOI",
                                "arrival_city": "Goa",
                                "arrival_time": "09:30",
                                "duration": "2h 30m",
                                "airline": "IndiGo",
                                "flight_number": "6E101",
                                "aircraft": "Airbus A320neo",
                                "cabin_class": "Economy"
                            }],
                            "total_duration": "2h 30m",
                            "stops": 0,
                            "price": 4200,
                            "currency": "INR",
                            "price_formatted": "₹4.2K",
                            "booking_class": "Economy"
                        }
                    ]
                }
            },
            {
                "type": "itinerary_card",
                "props": {
                    "days": [
                        {
                            "day_number": 1,
                            "date": "2026-01-20",
                            "theme": "North Goa Beaches",
                            "activities": [
                                {"start_time": "10:00", "duration": "1h", "title": "Arrival at Goa Airport", "location": "Dabolim Airport", "type": "transport"},
                                {"start_time": "11:30", "duration": "1h", "title": "Check-in at Taj Fort Aguada", "location": "Sinquerim", "type": "hotel"},
                                {"start_time": "13:00", "duration": "1h 30m", "title": "Lunch at Britto's", "location": "Baga Beach", "type": "food", "notes": ["Fresh seafood"]},
                                {"start_time": "15:00", "duration": "3h", "title": "Baga Beach & Water Sports", "location": "Baga", "type": "nature", "notes": ["Parasailing", "Jet ski"]},
                                {"start_time": "18:30", "duration": "1h 30m", "title": "Sunset at Chapora Fort", "location": "Chapora", "type": "attraction", "notes": ["Dil Chahta Hai fort!"]},
                                {"start_time": "20:30", "duration": "2h 30m", "title": "Dinner & Party at Tito's", "location": "Baga", "type": "food"}
                            ]
                        },
                        {
                            "day_number": 2,
                            "date": "2026-01-21",
                            "theme": "Heritage & South Goa",
                            "activities": [
                                {"start_time": "08:00", "duration": "1h", "title": "Breakfast at Hotel", "location": "Taj Fort Aguada", "type": "food"},
                                {"start_time": "09:30", "duration": "2h", "title": "Old Goa Churches", "location": "Old Goa", "type": "attraction", "notes": ["Basilica of Bom Jesus", "Se Cathedral"]},
                                {"start_time": "12:00", "duration": "1h 30m", "title": "Lunch at Vinayak Family Restaurant", "location": "Assagao", "type": "food"},
                                {"start_time": "14:00", "duration": "3h", "title": "Palolem Beach", "location": "South Goa", "type": "nature", "notes": ["Crescent-shaped beach"]},
                                {"start_time": "17:30", "duration": "1h", "title": "Sunset Kayaking", "location": "Palolem", "type": "nature"},
                                {"start_time": "19:30", "duration": "2h", "title": "Dinner at Martin's Corner", "location": "Betalbatim", "type": "food"}
                            ]
                        },
                        {
                            "day_number": 3,
                            "date": "2026-01-22",
                            "theme": "Relaxation & Departure",
                            "activities": [
                                {"start_time": "08:00", "duration": "2h", "title": "Spa at Taj", "location": "Taj Fort Aguada", "type": "nature"},
                                {"start_time": "10:30", "duration": "1h", "title": "Late Breakfast", "location": "Hotel", "type": "food"},
                                {"start_time": "12:00", "duration": "2h", "title": "Anjuna Flea Market", "location": "Anjuna", "type": "shopping"},
                                {"start_time": "14:30", "duration": "1h", "title": "Lunch at Curlies", "location": "Anjuna", "type": "food"},
                                {"start_time": "16:00", "duration": "1h", "title": "Check-out & Airport", "location": "Dabolim", "type": "transport"},
                                {"start_time": "18:30", "duration": "2h 30m", "title": "Flight to Delhi", "location": "GOI → DEL", "type": "transport"}
                            ]
                        }
                    ]
                }
            },
            {
                "type": "map_view",
                "props": {
                    "center": {"lat": 15.4989, "lng": 73.8278},
                    "zoom": 10,
                    "title": "Goa Trip Locations",
                    "markers": [
                        {"lat": 15.4989, "lng": 73.8278, "title": "Taj Fort Aguada", "type": "hotel", "day": 1},
                        {"lat": 15.5560, "lng": 73.7542, "title": "Baga Beach", "type": "nature", "day": 1},
                        {"lat": 15.6059, "lng": 73.7441, "title": "Chapora Fort", "type": "attraction", "day": 1},
                        {"lat": 15.5010, "lng": 73.9116, "title": "Old Goa Churches", "type": "attraction", "day": 2},
                        {"lat": 15.0100, "lng": 74.0230, "title": "Palolem Beach", "type": "nature", "day": 2},
                        {"lat": 15.5737, "lng": 73.7415, "title": "Anjuna Flea Market", "type": "shopping", "day": 3}
                    ]
                }
            }
        ]
    }
}


def get_clarifier_demo_response(user_input: str, session_id: str) -> Optional[dict]:
    """Get initial clarifier response based on destination detection."""
    dest = detect_destination(user_input)
    
    if dest:
        dest_names = {
            "mumbai": "Mumbai",
            "tokyo": "Tokyo",
            "paris": "Paris", 
            "goa": "Goa",
            "dubai": "Dubai"
        }
        return {
            "response": f"Excellent choice! {dest_names.get(dest, dest.title())} is amazing! 🎉\n\nLet me quickly gather a few details to personalize your trip. When are you planning to travel?",
            "session_id": session_id,
            "ui_components": [
                {
                    "type": "date_range_picker",
                    "props": {
                        "min_date": "2026-01-15",
                        "default_duration": 3
                    }
                }
            ],
            "demo_mode": True,
            "detected_destination": dest
        }
    
    return None
