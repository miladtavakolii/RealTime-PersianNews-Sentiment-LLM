import jdatetime
from datetime import datetime
from typing import Union

# Convert Persian digits to English digits
def fa_to_en_numbers(s: str) -> str:
    fa_numbers = "۰۱۲۳۴۵۶۷۸۹"
    en_numbers = "0123456789"
    for f, e in zip(fa_numbers, en_numbers):
        s = s.replace(f, e)
    return s

# Mapping Persian month names to numbers
month_map = {
    "فروردین": 1, "اردیبهشت": 2, "خرداد": 3, "تیر": 4,
    "مرداد": 5, "شهریور": 6, "مهر": 7, "آبان": 8,
    "آذر": 9, "دی": 10, "بهمن": 11, "اسفند": 12
}

def parse_date(date_str: str) -> Union[datetime, jdatetime.datetime]:
    """
    Parse a Persian or Gregorian date string and return the corresponding Gregorian datetime.

    Args:
        date_str: The date string in Persian or Gregorian format.

    Returns:
        Returns a Gregorian `datetime` object if the date is in Gregorian format, or a `jdatetime.datetime` object if the date is in Persian format.

    Raises:
        ValueError: If the date format is unrecognized.
    """
    date_str = fa_to_en_numbers(date_str.strip())

    # ISO 8601 format (Gregorian)
    if "T" in date_str:
        dt = datetime.fromisoformat(date_str)
        return dt.replace(tzinfo=None)
    
    # Short Persian date with month name: 10 azar(fa) 04 - 14:15
    if "-" in date_str and any(m in date_str for m in month_map):
        date_part, time_part = date_str.split(" - ")
        day, _, year = map(int, date_part.split())
        _, month_name, _ = date_part.split()
        month = month_map[month_name]
        if year < 100:
            year += 1400
        hour, minute = map(int, time_part.split(":"))
        return jdatetime.datetime(year, month, int(day), hour, minute).togregorian()

    # Full Persian date: 1404-09-10 14:34
    if "-" in date_str and " " in date_str:
        date_part, time_part = date_str.split(" ")
        year, month, day = map(int, date_part.split("-"))
        if year < 100:
            year += 1400
        hour, minute = map(int, time_part.split(":"))
        return jdatetime.datetime(year, month, day, hour, minute).togregorian()


    raise ValueError(f"Unrecognized date format: {date_str}")
