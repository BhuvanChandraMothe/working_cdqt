from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import func, cast, Date
import uuid
import json
from Backend.db.database import ProfilingRunModel


# Helper function for duration calculation
def get_time_filter(duration: str) -> datetime:
    now = datetime.now()
    if duration.lower() == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif duration.lower() == "last 7 days":
        return now - timedelta(days=7)
    elif duration.lower() == "last 30 days":
        return now - timedelta(days=30)
    # Add more duration options as needed
    return now - timedelta(days=30) # Default

# Helper for formatting duration
def format_duration_display(duration_str: Optional[str]) -> str:
    if duration_str is None:
        return "N/A"
    try:
        # Assuming duration_str is 'HH:MM:SS'
        parts = list(map(int, duration_str.split(':')))
        total_seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
        if total_seconds >= 3600: # Hours
            return f"{total_seconds // 3600}h"
        elif total_seconds >= 60: # Minutes
            return f"{total_seconds // 60}m"
        else:
            return f"{total_seconds}s"
    except (ValueError, IndexError):
        return duration_str # Return as is if parsing fails
    
    

# New helper to parse top_freq_values string
def parse_top_freq_values(top_freq_values_str: Optional[str]) -> List[dict]:
    """Parses the 'top_freq_values' string into a list of value-count dictionaries."""
    if not top_freq_values_str:
        return []
    try:
        # Assuming top_freq_values is a JSON string, e.g., '[{"value": "A", "count": 10}, {"value": "B", "count": 5}]'
        # Or it might be a simple comma-separated string like "value1:count1,value2:count2"
        # Adjust parsing logic based on actual format. For now, assuming JSON-like
        return json.loads(top_freq_values_str)
    except json.JSONDecodeError:
        # If it's not JSON, try to parse as "value:count,value:count"
        parsed_values = []
        pairs = top_freq_values_str.split(',')
        for pair in pairs:
            if ':' in pair:
                value, count_str = pair.split(':', 1)
                try:
                    parsed_values.append({"value": value.strip(), "count": int(count_str.strip())})
                except ValueError:
                    # Fallback if count is not an integer
                    parsed_values.append({"value": value.strip(), "count": 0})
            else:
                # If just value is present, assume count 1 or unknown
                parsed_values.append({"value": pair.strip(), "count": 0})
        return parsed_values

# New helper to determine latest successful run for a table group
def get_latest_successful_run_id(db, table_group_id: uuid.UUID) -> Optional[uuid.UUID]:
    """
    Finds the profile_run_id for the latest successful run of a given table group.
    """
    # from models import ProfilingRunModel # Import here to avoid circular dependency

    latest_run = db.query(ProfilingRunModel)\
        .filter(ProfilingRunModel.table_groups_id == table_group_id)\
        .filter(ProfilingRunModel.status == 'Complete')\
        .order_by(ProfilingRunModel.profiling_endtime.desc())\
        .first()
    return latest_run.id if latest_run else None

# New helper to calculate success rate change (simplified for example)
def calculate_success_rate_change(current_rate: float, previous_rate: float) -> str:
    if previous_rate == 0:
        return "N/A" # Avoid division by zero
    change = ((current_rate - previous_rate) / previous_rate) * 100
    return f"{'+' if change >= 0 else ''}{change:.0f}%"

# Helper for formatting large numbers 
def format_large_number(number: int) -> str:
    """
    Formats a large integer into a human-readable string (e.g., 1.2M, 34K).

    Args:
        number: The integer to format.

    Returns:
        A string representation of the formatted number.
    """
    if not isinstance(number, (int, float)):
        raise TypeError("Input must be an integer or float.")

    if number < 1000:
        return str(number)
    elif number < 1_000_000:
        return f"{number / 1000:.1f}K"
    elif number < 1_000_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number < 1_000_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    else:
        return f"{number / 1_000_000_000_000:.1f}T"