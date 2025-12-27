"""
DATETIME TOOLS
==============
Shared datetime utilities used by multiple agents.

IMPORTANT RULE: 
We cannot plan trips for dates that have already passed.
If a date is in the past, automatically use next year's date.
"""

from google.adk.tools import FunctionTool
from datetime import datetime, timedelta
from typing import Optional
import re

# Try to import pytz, fall back to simple UTC if not available
try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False


def _ensure_future_date(dt: datetime, today: datetime) -> datetime:
    """
    Ensure the date is in the future. If it's in the past, move to next year.
    
    Rule: We cannot plan trips for dates < today's date.
    """
    if dt.date() < today.date():
        # Date is in the past, use next year
        try:
            return dt.replace(year=dt.year + 1)
        except ValueError:
            # Handle Feb 29 edge case
            return dt.replace(year=dt.year + 1, day=28)
    return dt


def _parse_month_day(text: str) -> Optional[tuple]:
    """
    Parse month and day from various formats.
    Returns (month, day) tuple or None.
    """
    text = text.strip().lower()
    
    # Month name mapping
    months = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
        'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
        'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
        'aug': 8, 'august': 8, 'sep': 9, 'sept': 9, 'september': 9,
        'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    # Pattern: "jan 1", "january 15", "1 jan", "15 january"
    for pattern in [
        r'([a-z]+)\s+(\d{1,2})',  # jan 1
        r'(\d{1,2})\s+([a-z]+)',  # 1 jan
    ]:
        match = re.search(pattern, text)
        if match:
            g1, g2 = match.groups()
            if g1.isdigit():
                day, month_str = int(g1), g2
            else:
                month_str, day = g1, int(g2)
            
            if month_str in months:
                return (months[month_str], day)
    
    return None


def get_current_datetime(timezone: str = "UTC") -> dict:
    """
    Get current date and time in specified timezone.
    
    Args:
        timezone: IANA timezone name (e.g., "Asia/Tokyo", "Europe/London")
    
    Returns:
        Current datetime information
    """
    try:
        if HAS_PYTZ:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
        else:
            now = datetime.utcnow()
            if timezone != "UTC":
                return {
                    "error": "pytz not installed, only UTC supported",
                    "datetime": now.isoformat(),
                    "timezone": "UTC"
                }
    except Exception:
        now = datetime.utcnow()
        timezone = "UTC"
    
    return {
        "datetime": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "timezone": timezone,
        "year": now.year
    }


def get_calendar_dates(date_input: str, end_date_input: Optional[str] = None) -> dict:
    """
    Parse dates and ensure they are in the future.
    
    IMPORTANT RULE: Dates in the past are automatically moved to next year.
    For example, if today is Dec 27, 2025 and user says "jan 1 to jan 3",
    this returns January 1-3, 2026 (not 2025).
    
    Args:
        date_input: Start date like "jan 1", "next week", "tomorrow", "January 15"
        end_date_input: Optional end date like "jan 3", "January 18"
    
    Returns:
        Start and end dates, guaranteed to be in the future
    """
    today = datetime.now()
    date_lower = date_input.lower().strip()
    confidence = "high"
    year_adjusted = False
    
    # First check for relative dates
    if "tomorrow" in date_lower:
        start = today + timedelta(days=1)
    elif "today" in date_lower:
        start = today
    elif "next week" in date_lower:
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        start = today + timedelta(days=days_until_monday)
    elif "this weekend" in date_lower:
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0 and today.weekday() != 5:
            days_until_saturday = 7
        start = today + timedelta(days=days_until_saturday)
    elif "next month" in date_lower:
        if today.month == 12:
            start = today.replace(year=today.year + 1, month=1, day=1)
        else:
            start = today.replace(month=today.month + 1, day=1)
        confidence = "medium"
    elif match := re.search(r"in\s+(\d+)\s+days?", date_lower):
        days = int(match.group(1))
        start = today + timedelta(days=days)
    else:
        # Try to parse as explicit date (jan 1, January 15, etc.)
        parsed = _parse_month_day(date_input)
        if parsed:
            month, day = parsed
            start = datetime(today.year, month, day)
            start = _ensure_future_date(start, today)
            if start.year > today.year:
                year_adjusted = True
        else:
            # Try standard date formats
            for fmt in ["%B %d", "%d %B", "%m/%d", "%B %d, %Y", "%Y-%m-%d"]:
                try:
                    start = datetime.strptime(date_input.strip(), fmt)
                    if start.year == 1900:  # No year specified
                        start = start.replace(year=today.year)
                    start = _ensure_future_date(start, today)
                    if start.year > today.year:
                        year_adjusted = True
                    break
                except ValueError:
                    continue
            else:
                # Couldn't parse, default to next week
                start = today + timedelta(days=7)
                confidence = "low"
    
    # Parse end date if provided
    if end_date_input:
        end_lower = end_date_input.lower().strip()
        parsed_end = _parse_month_day(end_date_input)
        if parsed_end:
            month, day = parsed_end
            # Use same year as start by default
            end = datetime(start.year, month, day)
            # If end is before start, it might be next year
            if end < start:
                end = datetime(start.year + 1, month, day)
        else:
            # Try to parse as number of days
            if match := re.search(r"(\d+)\s*days?", end_lower):
                days = int(match.group(1))
                end = start + timedelta(days=days - 1)
            else:
                # Default duration
                end = start + timedelta(days=2)
                confidence = "medium"
    else:
        # Default 3-day trip
        end = start + timedelta(days=2)
    
    duration_days = (end - start).days + 1
    
    result = {
        "original_input": date_input,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "start_formatted": start.strftime("%B %d, %Y"),
        "end_formatted": end.strftime("%B %d, %Y"),
        "duration_days": duration_days,
        "confidence": confidence,
    }
    
    if year_adjusted:
        result["year_adjusted"] = True
        result["note"] = f"Date was in the past, adjusted to {start.year}"
    
    return result


def add_time_duration(start_time: str, duration_minutes: int) -> dict:
    """
    Calculate end time by adding duration to start time.
    
    Args:
        start_time: Start time in HH:MM format (e.g., "09:00", "14:30")
        duration_minutes: Duration in minutes
    
    Returns:
        End time and formatted duration string
    """
    try:
        start = datetime.strptime(start_time, "%H:%M")
    except ValueError:
        try:
            start = datetime.strptime(start_time, "%I:%M %p")
        except ValueError:
            return {
                "error": f"Could not parse time '{start_time}'. Use HH:MM format.",
                "start_time": start_time,
                "duration_minutes": duration_minutes
            }
    
    end = start + timedelta(minutes=duration_minutes)
    
    hours, mins = divmod(duration_minutes, 60)
    if hours and mins:
        duration_str = f"{hours}h {mins}m"
    elif hours:
        duration_str = f"{hours}h"
    else:
        duration_str = f"{mins}m"
    
    return {
        "start_time": start.strftime("%H:%M"),
        "end_time": end.strftime("%H:%M"),
        "start_time_12h": start.strftime("%I:%M %p"),
        "end_time_12h": end.strftime("%I:%M %p"),
        "duration_minutes": duration_minutes,
        "duration_formatted": duration_str
    }


# Wrap as ADK FunctionTools (kept for backwards compatibility)
get_current_datetime_tool = FunctionTool(get_current_datetime)
get_calendar_dates_tool = FunctionTool(get_calendar_dates)
add_time_duration_tool = FunctionTool(add_time_duration)
