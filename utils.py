import datetime
import re
from employee import Leave


def parse_date_natural_language(date_string: str) -> datetime.date | None:
    """Parses a date in natural language into a datetime.date object
    """
    date_string = date_string.lower().strip()
    today = datetime.date.today()
    current_year = today.year

    if date_string == "today":
        return today
    elif date_string == "tomorrow":
        return today + datetime.timedelta(days=1)
    elif date_string == "yesterday":
        # TODO: Custom error
        pass

    weekdays = {
        "sunday": 0, "monday": 1, "tuesday": 2, "wednesday": 3, "thursday": 4,
        "friday": 5, "saturday": 6
    }

    # specific day in a week
    if date_string.startswith("next ") and date_string[5:] in weekdays:
        target_weekday = weekdays[date_string[5:]]
        days_ahead = (target_weekday - today.weekday() + 7) % 7
        if days_ahead == 0:  # current day target == weekday next week
            days_ahead = 7
        return today + datetime.timedelta(days=days_ahead)

    match_month_day = re.match(r"(?:on )?([a-z]+) (\d{1,2})", date_string)
    if match_month_day:
        month_name, day_str = match_month_day.groups()
        month_map = {
            "january": 1, "february": 2, "march": 3,
            "april": 4, "may": 5, "june": 6,
            "july": 7, "august": 8, "september": 9,
            "october": 10, "november": 11, "december": 12
        }
        month_num = month_map.get(month_name)
        if month_num:
            try:
                return datetime.date(current_year, month_num, int(day_str))
            except ValueError:
                # TODO:Custom error
                pass

    print(f"Couldn't pass through {date_string} ")
    return None


def format_date(raw_date: datetime.date) -> str:
    """Formats a datetime.date object into a string"""

    return raw_date.strftime("%B %d, %Y")


def get_current_year() -> int:
    return datetime.date.today().year


def get_leave_types() -> set[str]:
    return Leave._LEAVE_TYPES


def get_leave_status_types() -> set[str]:
    return Leave._LEAVE_STATUS_TYPES
