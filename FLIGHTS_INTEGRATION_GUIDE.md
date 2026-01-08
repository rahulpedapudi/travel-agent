# Flight Card Frontend Integration Guide

This guide explains how to integrate the `flight_card` UI component in your React frontend.

## 1. API Response Structure

The backend returns flight data in this format:

```json
{
  "ui_component": {
    "type": "flight_card",
    "props": {
      "origin": "Delhi",
      "destination": "Tokyo",
      "departure_date": "2026-01-15",
      "passengers": 2,
      "flights": [
        {
          "id": "FL1AI234",
          "segments": [
            {
              "departure_airport": "DEL",
              "departure_city": "Delhi",
              "departure_time": "14:30",
              "arrival_airport": "NRT",
              "arrival_city": "Tokyo",
              "arrival_time": "06:45",
              "duration": "6h 15m",
              "airline": "Air India",
              "flight_number": "AI306",
              "aircraft": "Boeing 787",
              "cabin_class": "Economy"
            }
          ],
          "total_duration": "6h 15m",
          "stops": 0,
          "price": 45000,
          "currency": "INR",
          "price_formatted": "₹45K",
          "booking_class": "Economy"
        }
      ]
    }
  }
}
```

## 2. FlightCard Component

Create `src/components/ui/FlightCard.jsx`:

```jsx
import { useState } from "react";
import "./FlightCard.css";

export function FlightCard({ props }) {
  const {
    origin,
    destination,
    departure_date,
    flights = [],
    passengers,
  } = props;
  const [selectedFlight, setSelectedFlight] = useState(null);

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="flight-card">
      <div className="flight-header">
        <div className="route">
          <span className="origin">{origin}</span>
          <span className="arrow">→</span>
          <span className="destination">{destination}</span>
        </div>
        <div className="date">{formatDate(departure_date)}</div>
        <div className="passengers">
          {passengers} passenger{passengers > 1 ? "s" : ""}
        </div>
      </div>

      <div className="flight-options">
        {flights.map((flight) => (
          <FlightOption
            key={flight.id}
            flight={flight}
            isSelected={selectedFlight?.id === flight.id}
            onSelect={() => setSelectedFlight(flight)}
          />
        ))}
      </div>

      {selectedFlight && (
        <div className="flight-actions">
          <button className="book-btn">
            Book {selectedFlight.price_formatted}
          </button>
        </div>
      )}
    </div>
  );
}

function FlightOption({ flight, isSelected, onSelect }) {
  const segment = flight.segments[0]; // Primary segment

  return (
    <div
      className={`flight-option ${isSelected ? "selected" : ""}`}
      onClick={onSelect}>
      <div className="airline-info">
        <span className="airline-logo">✈️</span>
        <div className="airline-details">
          <span className="airline-name">{segment.airline}</span>
          <span className="flight-number">{segment.flight_number}</span>
        </div>
      </div>

      <div className="times">
        <div className="departure">
          <span className="time">{segment.departure_time}</span>
          <span className="airport">{segment.departure_airport}</span>
        </div>

        <div className="duration-info">
          <span className="duration">{flight.total_duration}</span>
          <div className="line"></div>
          <span className="stops">
            {flight.stops === 0
              ? "Direct"
              : `${flight.stops} stop${flight.stops > 1 ? "s" : ""}`}
          </span>
        </div>

        <div className="arrival">
          <span className="time">{segment.arrival_time}</span>
          <span className="airport">{segment.arrival_airport}</span>
        </div>
      </div>

      <div className="price">
        <span className="amount">{flight.price_formatted}</span>
        <span className="class">{flight.booking_class}</span>
      </div>
    </div>
  );
}
```

## 3. FlightCard Styles

Create `src/components/ui/FlightCard.css`:

```css
.flight-card {
  background: linear-gradient(135deg, #1a1f35 0%, #0d1025 100%);
  border-radius: 16px;
  padding: 20px;
  margin: 16px 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.flight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.route {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #fff;
}

.arrow {
  color: #4a90d9;
}

.date,
.passengers {
  color: #9ca3af;
  font-size: 14px;
}

.flight-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.flight-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.flight-option:hover {
  background: rgba(255, 255, 255, 0.08);
}

.flight-option.selected {
  border-color: #4a90d9;
  background: rgba(74, 144, 217, 0.1);
}

.airline-info {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 120px;
}

.airline-logo {
  font-size: 24px;
}

.airline-details {
  display: flex;
  flex-direction: column;
}

.airline-name {
  font-weight: 600;
  color: #fff;
  font-size: 14px;
}

.flight-number {
  color: #9ca3af;
  font-size: 12px;
}

.times {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
  justify-content: center;
}

.departure,
.arrival {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.time {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.airport {
  color: #9ca3af;
  font-size: 12px;
}

.duration-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 80px;
}

.duration {
  color: #9ca3af;
  font-size: 12px;
}

.line {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, #4a90d9, #27ae60);
  border-radius: 2px;
}

.stops {
  color: #27ae60;
  font-size: 11px;
  font-weight: 500;
}

.price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 80px;
}

.amount {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.class {
  color: #9ca3af;
  font-size: 12px;
}

.flight-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.book-btn {
  width: 100%;
  padding: 14px 24px;
  background: linear-gradient(135deg, #4a90d9, #27ae60);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.book-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(74, 144, 217, 0.3);
}
```

## 4. Handle in UI Renderer

Update your chat message renderer:

```jsx
import { FlightCard } from "./ui/FlightCard";

function UIComponentRenderer({ ui }) {
  switch (ui.type) {
    case "flight_card":
      return <FlightCard props={ui.props} />;

    case "map_view":
      return <MapView props={ui.props} />;

    case "itinerary_card":
      return <ItineraryCard props={ui.props} />;

    default:
      return null;
  }
}
```

## 5. Multi-Segment Flights (Connections)

For flights with layovers, render multiple segments:

```jsx
function FlightSegments({ segments }) {
  return (
    <div className="segments">
      {segments.map((seg, i) => (
        <div key={i} className="segment">
          <div className="segment-route">
            {seg.departure_airport} → {seg.arrival_airport}
          </div>
          <div className="segment-time">
            {seg.departure_time} - {seg.arrival_time}
          </div>
          <div className="segment-airline">
            {seg.airline} {seg.flight_number}
          </div>
          {i < segments.length - 1 && <div className="layover">Layover</div>}
        </div>
      ))}
    </div>
  );
}
```

## Summary

1. Backend calls `search_flights()` → returns `flight_card` UI component
2. Frontend receives `ui_component.type === "flight_card"`
3. `FlightCard` component renders selectable flight options
4. User can select a flight and see booking action

The design uses a dark theme with gradient accents matching the travel app aesthetic.
