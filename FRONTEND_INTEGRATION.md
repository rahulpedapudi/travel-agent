# Frontend Integration Guide

## API Endpoints

### Standard Chat (Non-Streaming)

```
POST /chat
Content-Type: application/json

{
  "message": "Your message here",
  "session_id": "optional-uuid"
}
```

**Response:**

```json
{
  "response": "Text from the agent",
  "session_id": "uuid",
  "ui": {
    "type": "budget_slider",
    "props": { ... },
    "required": true
  }
}
```

---

### Streaming Chat (SSE)

```
POST /chat/stream
Content-Type: application/json

{
  "message": "Your message here",
  "session_id": "optional-uuid"
}
```

**Event Stream Format:**

| Event Type      | Payload                                                                                        |
| --------------- | ---------------------------------------------------------------------------------------------- |
| `token`         | `{"type": "token", "text": "partial text"}`                                                    |
| `thinking`      | `{"type": "thinking", "message": "Searching...", "tool": "find_places_nearby"}`                |
| `plan`          | `{"type": "plan", "tasks": [{"id": "research", "label": "Researching", "status": "pending"}]}` |
| `task_start`    | `{"type": "task_start", "taskId": "research", "label": "Researching destinations"}`            |
| `task_complete` | `{"type": "task_complete", "taskId": "research"}`                                              |
| `done`          | `{"type": "done", "session_id": "uuid", "ui": {...}}`                                          |
| `error`         | `{"type": "error", "message": "..."}`                                                          |

**React Implementation:**

```jsx
async function streamChat(message, sessionId, onToken, onThinking, onComplete) {
  const response = await fetch("/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const lines = decoder.decode(value).split("\n");
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = JSON.parse(line.slice(6));
        if (data.type === "token") onToken(data.text);
        if (data.type === "thinking") onThinking(data.message);
        if (data.type === "plan") onPlan(data.tasks);
        if (data.type === "task_start") onTaskStart(data.taskId);
        if (data.type === "task_complete") onTaskComplete(data.taskId);
        if (data.type === "done") onComplete(data);
      }
    }
  }
}
```

The `ui` field is **optional** - only present when a special component should be rendered.

---

## UI Component Types

### 1. budget_slider

**When:** Agent asks about budget

```json
{
  "type": "budget_slider",
  "props": {
    "min": 10000,
    "max": 500000,
    "step": 5000,
    "currency": "INR",
    "presets": ["Budget (₹10k-50k)", "Mid-range (₹50k-1.5L)", "Luxury (₹2L+)"]
  },
  "required": true
}
```

**User response:** Send the selected value as the message, e.g., `"₹50000"` or `"Mid-range"`

---

### 2. date_range_picker

**When:** Agent asks about travel dates

```json
{
  "type": "date_range_picker",
  "props": {
    "min_date": null,
    "max_date": null,
    "default_duration": 3,
    "show_presets": true
  },
  "required": true
}
```

**User response:** `"January 15-18, 2026"` or `"next week"`

---

### 3. preference_chips

**When:** Agent asks about interests

```json
{
  "type": "preference_chips",
  "props": {
    "options": [
      { "id": "food", "label": "🍜 Food & Dining", "selected": false },
      { "id": "museums", "label": "🏛️ Museums & Art", "selected": false },
      { "id": "nature", "label": "🌲 Nature & Outdoors", "selected": false },
      { "id": "nightlife", "label": "🌙 Nightlife", "selected": false },
      { "id": "shopping", "label": "🛍️ Shopping", "selected": false },
      { "id": "history", "label": "🏰 History & Culture", "selected": false },
      { "id": "adventure", "label": "🎢 Adventure", "selected": false },
      { "id": "relaxation", "label": "🧘 Relaxation", "selected": false }
    ],
    "multi_select": true,
    "min_selections": 0,
    "max_selections": null
  },
  "required": true
}
```

**User response:** `"food, museums, nightlife"`

---

### 4. companion_selector

**When:** Agent asks who's traveling

```json
{
  "type": "companion_selector",
  "props": {
    "options": [
      { "id": "solo", "label": "Solo", "icon": "👤" },
      { "id": "couple", "label": "Couple", "icon": "💑" },
      { "id": "family_kids", "label": "Family with Kids", "icon": "👨‍👩‍👧" },
      { "id": "family_adults", "label": "Family (Adults)", "icon": "👨‍👩‍👦‍👦" },
      { "id": "friends", "label": "Friends", "icon": "👥" }
    ],
    "show_kids_age_input": true
  },
  "required": true
}
```

**User response:** `"couple"` or `"family with kids, ages 8 and 12"`

---

### 5. rating_feedback

**When:** After showing itinerary

```json
{
  "type": "rating_feedback",
  "props": {
    "scale": 5,
    "show_comment": true,
    "prompt": "How's this itinerary?"
  },
  "required": false
}
```

**User response:** `"5"` or `"4 - can you add more food options?"`

---

### 6. itinerary_card

**When:** Showing a day's plan

```json
{
  "type": "itinerary_card",
  "props": {
    "day_number": 1,
    "date": "2026-01-15",
    "theme": "Cultural Exploration",
    "activities": [
      {
        "time": "9:00 AM",
        "title": "Visit Senso-ji Temple",
        "location": "Asakusa",
        "duration": "2 hours",
        "type": "attraction",
        "notes": "Arrive early to avoid crowds"
      }
    ],
    "allow_actions": true
  }
}
```

---

### 7. quick_actions

**When:** Offering refinement options

```json
{
  "type": "quick_actions",
  "props": {
    "actions": [
      { "id": "swap", "label": "🔄 Swap Activity" },
      { "id": "add", "label": "➕ Add More" },
      { "id": "remove", "label": "➖ Remove" },
      { "id": "done", "label": "✅ Looks Good!" }
    ]
  }
}
```

---

## React Implementation Example

```jsx
// componentRegistry.js
import BudgetSlider from "./BudgetSlider";
import DateRangePicker from "./DateRangePicker";
import PreferenceChips from "./PreferenceChips";
import CompanionSelector from "./CompanionSelector";
import RatingFeedback from "./RatingFeedback";
import ItineraryCard from "./ItineraryCard";
import QuickActions from "./QuickActions";

export const UI_COMPONENTS = {
  budget_slider: BudgetSlider,
  date_range_picker: DateRangePicker,
  preference_chips: PreferenceChips,
  companion_selector: CompanionSelector,
  rating_feedback: RatingFeedback,
  itinerary_card: ItineraryCard,
  quick_actions: QuickActions,
};

// MessageBubble.jsx
function MessageBubble({ message, onSendMessage }) {
  const UIComponent = message.ui ? UI_COMPONENTS[message.ui.type] : null;

  return (
    <div className="message-bubble">
      <p>{message.response}</p>

      {UIComponent && (
        <UIComponent
          {...message.ui.props}
          onSubmit={(value) => onSendMessage(value)}
        />
      )}
    </div>
  );
}
```

---

## Get UI Schema

```
GET /ui-schema

Returns all component schemas for reference.
```

---

## Session Management

- Generate `session_id` on first message (use `crypto.randomUUID()`)
- Store in `localStorage`
- Send with every request to maintain conversation
- Call `DELETE /session/{id}` to start fresh
