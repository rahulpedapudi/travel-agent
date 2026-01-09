# AI Travel Agent 🌍✈️

A next-generation travel planning assistant powered by **Google Gemini 2.5**, **Google Maps**, and **Server-Driven UI**.

This agent doesn't just chat—it builds interactive itineraries, searches for flights, pins locations on a map, and adapts to your preferences in real-time.

## ✨ Key Features

- **🧠 Multi-Agent Orchestration**: A specialized team of 6 AI agents (Supervisor, Researcher, Planner, etc.) working together.
- **🗺️ Interactive Maps**: Visualizes day-by-day itineraries with Google Maps pins and routes.
- **✈️ Flight Integration**: Searches and displays flight options with real-time pricing formats.
- **� Server-Driven UI (SDUI)**: The backend controls the frontend experience, rendering rich components like Flight Cards, Itinerary Timelines, and Interest Sliders.
- **🎭 Demo Mode**: Built-in mock data mode to showcase full capabilities without hitting external APIs.
- **🛡️ Enterprise-Grade Reliability**: Prompt hardening against injection attacks, Pydantic validation, and Redis state persistence.

## 🚀 Quick Start (Demo Mode)

Want to see it in action without configuring API keys? Use the **Demo Mode**.

1.  **Clone the repository**

    ```bash
    git clone https://github.com/rahulpedapudi/travel-agent.git
    cd travel-agent
    ```

2.  **Set up environment**
    Create a `.env` file in `travel_agent/`:

    ```env
    DEMO_MODE=true
    LLM_MODEL=gemini-2.5-flash
    ```

3.  **Run the Backend**

    ```bash
    uvicorn travel_agent.api:app --reload
    ```

4.  **Test specific destinations**
    The demo mode has pre-built full itineraries for:
    - _"Plan a trip to Mumbai"_
    - _"I want to go to Tokyo"_
    - _"Paris vacation"_
    - _"Goa beach trip"_

## 🛠️ Technical Architecture

### The Agent Swarm

The system uses a **Hub-and-Spoke** architecture managed by a Root Supervisor:

| Agent                   | Responsibility                                                                   |
| ----------------------- | -------------------------------------------------------------------------------- |
| **Root Supervisor**     | Orchestrates the team, delegates tasks, and manages conversation flow.           |
| **Clarifier**           | Asks follow-up questions to understand user intent (budget, dates, vibes).       |
| **Researcher**          | Uses Google Places API to find hotels, restaurants, and attractions.             |
| **Activity Specialist** | Recommends niche activities based on user persona (e.g., "Foodie", "Adventure"). |
| **Builder**             | Constructs the deterministic schedule, accounting for travel time and logic.     |
| **Refinement**          | Handles mid-plan changes (e.g., "Swap the museum for a beach").                  |

### Server-Driven UI (SDUI)

The backend returns UI components dynamically. The frontend is a "dumb" renderer.

**Example Response:**

```json
{
  "response": "Here are some flight options for Tokyo...",
  "ui_components": [
    {
      "type": "flight_card",
      "props": { "flights": [...], "price": "45000" }
    },
    {
      "type": "map_view",
      "props": { "markers": [...] }
    }
  ]
}
```

## 📦 Installation (Production)

### Prerequisites

- Python 3.10+
- Node.js 18+
- One Redis instance (or usage of simple in-memory state for dev)
- Google Cloud Project with:
  - Gemini API enabled
  - Google Maps/Places API enabled

### Backend Setup

1.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration**
    Update `.env`:

    ```env
    GOOGLE_API_KEY=your_gemini_key
    GOOGLE_MAPS_API_KEY=your_maps_key
    REDIS_URL=redis://localhost:6379
    DEMO_MODE=false
    ```

3.  **Run Server**
    ```bash
    uvicorn travel_agent.api:app --host 0.0.0.0 --port 8080
    ```

### Frontend Setup

See the integration guides for React component implementation:

- [Maps Integration Guide](./MAPS_INTEGRATION_GUIDE.md)
- [Flights Integration Guide](./FLIGHTS_INTEGRATION_GUIDE.md)

## 📂 Project Structure

```
travel_agent/
├── agents/             # The brain of the operation
│   ├── root_agent.py   # Main router/supervisor
│   ├── researcher.py   # RAG & Search tools
│   └── builder.py      # Logic & Scheduling
├── tools/              # Capability layer
│   ├── flight_tools.py # Mock/Real flight search
│   ├── ui_tools.py     # SDUI component generators
│   └── map_tools.py    # Google Maps wrappers
├── api.py              # FastAPI endpoints
├── schemas.py          # Pydantic models for SDUI
└── demo_data.py        # Mock itineraries for demo mode
```

## 🔒 Security

- **Prompt Hardening**: Agents use `<SYSTEM_BOUNDARY>` tags to prevent jailbreaks.
- **Input Validation**: Strictly typed Pydantic models for all tool inputs.
- **Session Isolation**: Chat history and state are isolated by session ID.

---
