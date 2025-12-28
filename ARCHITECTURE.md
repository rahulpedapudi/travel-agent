# Travel Agent Architecture Guide

A comprehensive overview of agents, tools, and workflow.

---

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                     ROOT AGENT                          │
│              (Supervisor / Orchestrator)                │
│                                                         │
│   Personality: Friendly travel expert                   │
│   Model: gemini-2.5-flash                              │
│   Tools: render_ui + 5 sub-agents                       │
└─────────────────────────────────────────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │          │          │          │          │
    ▼          ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Clarifier│ │Research│ │Activity│ │Builder │ │Refine  │
│  Agent  │ │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

---

## Agents

### 1. Root Agent (`root_agent.py`)

**Role**: Orchestrates everything, talks directly to user

| Property | Value                                                                                                |
| -------- | ---------------------------------------------------------------------------------------------------- |
| Name     | `supervisor`                                                                                         |
| Model    | `gemini-3-flash`                                                                                     |
| Tools    | `clarifier_tool`, `researcher_tool`, `activity_tool`, `builder_tool`, `refinement_tool`, `render_ui` |

**Current Instructions Summary**:

- Personality: Warm, enthusiastic, conversational
- Never mention "agents", "tools", or internal workings
- Always complete work in same turn (no "give me a moment")
- Ask ONE question at a time
- Use `render_ui` for interactive components

---

### 2. Clarifier Agent (`clarifier.py`)

**Role**: Gather trip requirements and preferences

| Property | Value                                                                                      |
| -------- | ------------------------------------------------------------------------------------------ |
| Name     | `clarifier_agent`                                                                          |
| Model    | `gemini-2.5-flash`                                                                         |
| Tools    | `validate_destination`, `validate_budget`, `get_calendar_dates`, `update_trip_preferences` |

**Current Instructions Summary**:

- Two modes: GUIDED (ask questions) and SURPRISE_ME (use defaults)
- Ask ONE question at a time
- Questions: Destination → Dates → Budget → Companions → Interests → Style → Accommodation → Avoids

---

### 3. Researcher Agent (`researcher.py`)

**Role**: Find real data about destinations

| Property | Value                                                                                  |
| -------- | -------------------------------------------------------------------------------------- |
| Name     | `researcher_agent`                                                                     |
| Model    | `gemini-2.5-flash`                                                                     |
| Tools    | `find_places_nearby`, `get_current_datetime`, `search_transport`, `search_travel_info` |

**Current Instructions Summary**:

- Never mention "tools", "API", "search"
- Speak naturally as if YOU know these places
- Find: Hotels (3-5), Attractions, Restaurants

---

### 4. Activity Agent (`activity_agent.py`)

**Role**: Recommend activities based on interests

| Property | Value                                                 |
| -------- | ----------------------------------------------------- |
| Name     | `activity_agent`                                      |
| Model    | `gemini-2.5-flash`                                    |
| Tools    | `find_places_nearby`, `filter_activities_by_interest` |

**Current Instructions Summary**:

- Never mention "tools", "filters", "algorithms"
- Match activities to interests (food, museums, nightlife)
- Kid-friendly for families, romantic for couples

---

### 5. Builder Agent (`builder.py`)

**Role**: Create day-by-day itineraries

| Property | Value                                                              |
| -------- | ------------------------------------------------------------------ |
| Name     | `itinerary_builder`                                                |
| Model    | `gemini-2.5-flash`                                                 |
| Tools    | `compute_route_matrix`, `validate_open_hours`, `add_time_duration` |

**Current Instructions Summary**:

- Never mention "route matrix", "API", "calculations"
- Group nearby places (less travel time)
- 3-4 activities per day, include meal breaks
- Format with emojis: 🌅 Morning, 🍜 Lunch, 🌇 Afternoon, 🌙 Evening

---

### 6. Refinement Agent (`refinement_agent.py`)

**Role**: Handle mid-plan changes

| Property | Value                                    |
| -------- | ---------------------------------------- |
| Name     | `refinement_agent`                       |
| Model    | `gemini-2.5-flash`                       |
| Tools    | `find_places_nearby`, `apply_refinement` |

**Current Instructions Summary**:

- Never mention "refinement", "processing"
- Handle: Swap X for Y, Add more X, Remove X, Budget adjustments
- Confirm change briefly, show updated itinerary

---

## Tools

### DateTime Tools (`datetime_tools.py`)

| Tool                   | Purpose                                          |
| ---------------------- | ------------------------------------------------ |
| `get_current_datetime` | Get current date/time in any timezone            |
| `get_calendar_dates`   | Parse dates, auto-adjust past dates to next year |
| `add_time_duration`    | Add duration to time (e.g., 9:00 + 2h = 11:00)   |

### Search Tools (`search_tools.py`)

| Tool                 | Purpose                                      |
| -------------------- | -------------------------------------------- |
| `search_travel_info` | General travel information via Google Search |
| `search_transport`   | Find flights, trains, buses                  |

### Places Tools (`places_tools.py`)

| Tool                 | Purpose                                                     |
| -------------------- | ----------------------------------------------------------- |
| `find_places_nearby` | Find hotels, restaurants, attractions via Google Places API |

### Maps Tools (`maps_tools.py`)

| Tool                   | Purpose                                  |
| ---------------------- | ---------------------------------------- |
| `compute_route_matrix` | Calculate travel times between locations |
| `validate_open_hours`  | Check if place is open at proposed time  |

### State Tools (`state_tools.py`)

| Tool                      | Purpose                                |
| ------------------------- | -------------------------------------- |
| `update_trip_preferences` | Save user preferences for other agents |
| `get_trip_preferences`    | Retrieve saved preferences             |

### Validation Tools (`validation_tools.py`)

| Tool                   | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| `validate_destination` | Fix typos (e.g., "Tokio" → "Tokyo, Japan") |
| `validate_budget`      | Parse "$5k", "mid-range", "luxury"         |

### UI Tools (`ui_tools.py`)

| Tool        | Purpose                                                         |
| ----------- | --------------------------------------------------------------- |
| `render_ui` | Specify UI component to show (budget_slider, date_picker, etc.) |

---

## Workflow

```
User: "Plan a trip to Tokyo"
         │
         ▼
    ┌─────────┐
    │  ROOT   │──▶ Asks: "When are you going?"
    │  AGENT  │    + render_ui("date_range_picker")
    └─────────┘
         │
User: "Next week"
         │
         ▼
    ┌─────────┐
    │  ROOT   │──▶ Calls: clarifier_agent
    └─────────┘    (gathers more info: budget, companions, interests)
         │
         ▼
    ┌─────────┐
    │  ROOT   │──▶ Calls: researcher_agent
    └─────────┘    (finds hotels, restaurants, attractions)
         │
         ▼
    ┌─────────┐
    │  ROOT   │──▶ Calls: activity_agent
    └─────────┘    (filters activities by interests)
         │
         ▼
    ┌─────────┐
    │  ROOT   │──▶ Calls: builder_agent
    └─────────┘    (creates day-by-day itinerary)
         │
         ▼
    Returns complete itinerary to user
         │
User: "Can you swap the museum for shopping?"
         │
         ▼
    ┌─────────┐
    │  ROOT   │──▶ Calls: refinement_agent
    └─────────┘    (modifies itinerary)
```

---

## File Structure

```
travel_agent/
├── api.py              # FastAPI endpoints (/chat, /chat/stream)
├── schemas.py          # UI component schemas (Pydantic models)
├── agents/
│   ├── root_agent.py   # Supervisor (entry point)
│   ├── clarifier.py    # Gathers preferences
│   ├── researcher.py   # Finds places
│   ├── activity_agent.py # Recommends activities
│   ├── builder.py      # Creates itinerary
│   └── refinement_agent.py # Handles changes
└── tools/
    ├── datetime_tools.py
    ├── search_tools.py
    ├── places_tools.py
    ├── maps_tools.py
    ├── state_tools.py
    ├── validation_tools.py
    └── ui_tools.py
```

---

## Prompt Guidelines

When modifying agent instructions:

1. **Never mention internals** - No "tools", "API", "algorithms", "processing"
2. **Be conversational** - Like chatting with a friend
3. **Use emojis** - For visual structure in itineraries
4. **One question at a time** - For proper UI rendering
5. **Complete the work** - No "give me a moment" messages
6. **Handle errors naturally** - "I couldn't find that" not "API error"
