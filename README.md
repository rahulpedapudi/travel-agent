# Travel Agent 🌍

AI-powered travel planning assistant built with Google ADK and Gemini.

## Features

- 💬 Natural conversational interface
- 🎯 Personalized recommendations based on interests
- 🗓️ Smart date handling (auto-adjusts past dates)
- ✏️ Mid-plan changes ("swap beach for shopping")
- 🎲 "Surprise me" mode


## API Endpoints

| Endpoint        | Method | Description                |
| --------------- | ------ | -------------------------- |
| `/chat`         | POST   | Send message, get response |
| `/health`       | GET    | Health check               |
| `/session/{id}` | DELETE | Clear session              |

## Architecture

```
travel_agent/
├── agents/           # AI agents
│   ├── root_agent.py     # Supervisor
│   ├── clarifier.py      # Gathers requirements
│   ├── researcher.py     # Finds places
│   ├── builder.py        # Creates itinerary
│   ├── activity_agent.py # Interest-based recs
│   └── refinement_agent.py # Mid-plan changes
├── tools/            # Agent tools
├── state/            # Session management
├── api.py            # FastAPI backend
└── config.py         # Settings
```


