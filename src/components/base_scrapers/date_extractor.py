import re
from datetime import datetime


def extract_date_components(date_string, alt_date):
    # Pattern to match "HH:MM DD Mon YYYY - HH:MM DD Mon YYYY"
    pattern = r"(\d{2}:\d{2}) (\d{1,2}) (\w{3}) (\d{4}) - (\d{2}:\d{2}) (\d{1,2}) (\w{3}) (\d{4})"

    # Alternative time and date patterns
    time_pattern = r"(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})\s*SAST\s*\(\+02:00\)"
    date_pattern = r"(\d{1,2})\s+([A-Za-z]{3})\s*(\d{4})?\s*SAST\s*\(\+02:00\)"  # Year is optional

    # Try first pattern (full timestamp extraction)
    match = re.search(pattern, date_string)

    if match:
        start_hour, start_minute = map(int, match.group(1).split(":"))
        start_day, start_month_str, start_year = int(match.group(2)), match.group(3), int(match.group(4))
        end_hour, end_minute = map(int, match.group(5).split(":"))
        end_day, end_month_str, end_year = int(match.group(6)), match.group(7), int(match.group(8))

    else:
        # Try the alternative approach
        time_match = re.search(time_pattern, date_string)
        date_match = re.search(date_pattern, alt_date)

        if not time_match or not date_match:
            return None, None  # No valid date found

        # Extract time components
        start_hour, start_minute, end_hour, end_minute = map(int, time_match.groups())

        # Extract date components
        day, month_str, year = date_match.groups()
        month = datetime.strptime(month_str, "%b").month
        day = int(day)
        year = int(year) if year else datetime.now().year  # Default to current year if missing

        start_day, start_month_str, start_year = day, month_str, year
        end_day, end_month_str, end_year = day, month_str, year

    # Convert month abbreviation to number
    start_month = datetime.strptime(start_month_str, "%b").month
    end_month = datetime.strptime(end_month_str, "%b").month

    # Create component dictionaries
    start_components = {
        "year": start_year,
        "month": start_month,
        "day": start_day,
        "hour": start_hour,
        "minute": start_minute
    }

    end_components = {
        "year": end_year,
        "month": end_month,
        "day": end_day,
        "hour": end_hour,
        "minute": end_minute
    }

    return start_components, end_components


# Example usage:
# date_string = "13:00 8 Mar 2025 - 02:00 9 Mar 2025 SAST (+02:00)"
# alt_date = "8 Mar - 9 Mar SAST (+02:00)"
#
# start, end = extract_date_components(date_string, alt_date)
#
# print("Start:", start)
# print("End:", end)
