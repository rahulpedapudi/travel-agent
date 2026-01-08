# Google Maps Frontend Integration Guide

This guide explains how to integrate the `map_view` and `route_view` UI components in your React frontend.

## Prerequisites

```bash
npm install @react-google-maps/api
```

## 1. API Key Setup

Add to your `.env`:

```
REACT_APP_GOOGLE_MAPS_API_KEY=your_api_key_here
```

## 2. Map Provider Component

Create `src/components/MapProvider.jsx`:

```jsx
import { LoadScript } from "@react-google-maps/api";

const libraries = ["places", "directions"];

export function MapProvider({ children }) {
  return (
    <LoadScript
      googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}
      libraries={libraries}>
      {children}
    </LoadScript>
  );
}
```

## 3. MapView Component

Create `src/components/ui/MapView.jsx`:

```jsx
import { GoogleMap, Marker, InfoWindow } from "@react-google-maps/api";
import { useState } from "react";

const markerIcons = {
  hotel: "🏨",
  attraction: "📍",
  restaurant: "🍽️",
  activity: "🎯",
};

const markerColors = {
  hotel: "#4A90D9",
  attraction: "#E74C3C",
  restaurant: "#F39C12",
  activity: "#27AE60",
};

export function MapView({ props }) {
  const { center, zoom = 13, markers = [], title } = props;
  const [selectedMarker, setSelectedMarker] = useState(null);

  const mapContainerStyle = {
    width: "100%",
    height: "400px",
    borderRadius: "12px",
  };

  return (
    <div className="map-container">
      {title && <h3 className="map-title">{title}</h3>}

      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={center}
        zoom={zoom}
        options={{
          styles: darkMapStyle, // Optional: custom map style
          disableDefaultUI: false,
          zoomControl: true,
          mapTypeControl: false,
        }}>
        {markers.map((marker, index) => (
          <Marker
            key={`${marker.title}-${index}`}
            position={{ lat: marker.lat, lng: marker.lng }}
            label={{
              text: marker.day
                ? String(marker.day)
                : markerIcons[marker.type] || "📍",
              color: "white",
              fontSize: "12px",
            }}
            onClick={() => setSelectedMarker(marker)}
          />
        ))}

        {selectedMarker && (
          <InfoWindow
            position={{ lat: selectedMarker.lat, lng: selectedMarker.lng }}
            onCloseClick={() => setSelectedMarker(null)}>
            <div className="info-window">
              <h4>{selectedMarker.title}</h4>
              <span className="marker-type">{selectedMarker.type}</span>
              {selectedMarker.description && (
                <p>{selectedMarker.description}</p>
              )}
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
    </div>
  );
}
```

## 4. RouteView Component

Create `src/components/ui/RouteView.jsx`:

```jsx
import { GoogleMap, DirectionsRenderer, Marker } from "@react-google-maps/api";
import { useState, useEffect } from "react";

export function RouteView({ props }) {
  const {
    origin,
    destination,
    waypoints = [],
    travel_mode = "TRANSIT",
    day_number,
  } = props;
  const [directions, setDirections] = useState(null);

  useEffect(() => {
    const directionsService = new window.google.maps.DirectionsService();

    const waypointsList = waypoints.map((wp) => ({
      location: { lat: wp.lat, lng: wp.lng },
      stopover: true,
    }));

    directionsService.route(
      {
        origin: { lat: origin.lat, lng: origin.lng },
        destination: { lat: destination.lat, lng: destination.lng },
        waypoints: waypointsList,
        travelMode: window.google.maps.TravelMode[travel_mode],
        optimizeWaypoints: false,
      },
      (result, status) => {
        if (status === "OK") {
          setDirections(result);
        }
      }
    );
  }, [origin, destination, waypoints, travel_mode]);

  const mapContainerStyle = {
    width: "100%",
    height: "400px",
    borderRadius: "12px",
  };

  const center = {
    lat: (origin.lat + destination.lat) / 2,
    lng: (origin.lng + destination.lng) / 2,
  };

  return (
    <div className="route-container">
      {day_number && <h3>Day {day_number} Route</h3>}

      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={center}
        zoom={12}>
        {directions && (
          <DirectionsRenderer
            directions={directions}
            options={{
              polylineOptions: {
                strokeColor: "#4A90D9",
                strokeWeight: 4,
              },
              suppressMarkers: false,
            }}
          />
        )}

        {/* Custom markers for waypoints with times */}
        {waypoints.map((wp, index) => (
          <Marker
            key={wp.title}
            position={{ lat: wp.lat, lng: wp.lng }}
            label={{
              text: String(wp.order),
              color: "white",
            }}
            title={`${wp.title} - ${wp.arrival_time || ""}`}
          />
        ))}
      </GoogleMap>
    </div>
  );
}
```

## 5. Handle UI Components in Chat

Update your chat message renderer to handle map types:

```jsx
function UIComponentRenderer({ ui }) {
  switch (ui.type) {
    case "map_view":
      return <MapView props={ui.props} />;

    case "route_view":
      return <RouteView props={ui.props} />;

    case "itinerary_card":
      return <ItineraryCard props={ui.props} />;

    // ... other components

    default:
      return null;
  }
}
```

## 6. API Response Structure

The backend returns map data in this format:

```json
{
  "ui_component": {
    "type": "map_view",
    "props": {
      "center": { "lat": 35.6762, "lng": 139.6503 },
      "zoom": 13,
      "markers": [
        {
          "lat": 35.6586,
          "lng": 139.7454,
          "title": "Tokyo Tower",
          "type": "attraction",
          "day": 1
        }
      ],
      "title": "Tokyo Trip Locations"
    }
  }
}
```

## 7. Styling (Optional)

```css
.map-container {
  margin: 16px 0;
}

.map-title {
  margin-bottom: 8px;
  font-size: 18px;
  font-weight: 600;
}

.info-window {
  padding: 8px;
}

.info-window h4 {
  margin: 0 0 4px;
}

.marker-type {
  font-size: 12px;
  color: #666;
  text-transform: capitalize;
}
```

## Summary

1. Backend calls `render_map()` → returns `map_view` UI component
2. Backend calls `render_route()` → returns `route_view` UI component
3. Frontend receives `ui_component` in response
4. `UIComponentRenderer` renders appropriate map component
5. Google Maps JS API handles rendering

The map will automatically show all researched locations with color-coded pins and optionally display routes for each day's journey.
