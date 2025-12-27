"""
UI TOOLS
========
Tools for rendering dynamic UI components.

The agent calls render_ui() to specify which UI component should be shown.
The API layer captures these tool calls and includes them in the response.
"""

from typing import Optional
import json


def render_ui(
    component_type: str,
    props: Optional[dict] = None,
    required: bool = True
) -> str:
    """
    Render a UI component for the user to interact with.
    
    Call this when you need the user to provide structured input.
    The UI component will be displayed alongside your text response.
    
    Args:
        component_type: The type of component to render. Must be one of:
            - "budget_slider": For budget selection (props: min, max, step, currency, presets)
            - "date_range_picker": For travel dates (props: min_date, max_date, default_duration)
            - "preference_chips": For interests/preferences (props: options, multi_select)
            - "companion_selector": For travel companions (props: options)
            - "quick_actions": For action buttons (props: actions)
            - "rating_feedback": For feedback collection (props: scale, prompt)
        
        props: Component-specific properties. If not provided, defaults will be used.
            Examples:
            - budget_slider: {"min": 10000, "max": 500000, "currency": "INR"}
            - date_range_picker: {"show_presets": true}
            - preference_chips: {"options": [{"id": "food", "label": "Food"}]}
            - companion_selector: {} (uses default options)
        
        required: Whether the user must interact with this component (default: True)
    
    Returns:
        Confirmation that the UI component will be rendered.
    
    Examples:
        # Ask about budget
        render_ui("budget_slider", {"min": 10000, "max": 200000, "currency": "INR"})
        
        # Ask about dates
        render_ui("date_range_picker", {"show_presets": True})
        
        # Ask about interests
        render_ui("preference_chips", {
            "options": [
                {"id": "food", "label": "🍜 Food & Dining"},
                {"id": "culture", "label": "🏛️ Culture & History"}
            ]
        })
    """
    if props is None:
        props = {}
    
    # Return structured data that API will parse
    return json.dumps({
        "ui_component": {
            "type": component_type,
            "props": props,
            "required": required
        }
    })
