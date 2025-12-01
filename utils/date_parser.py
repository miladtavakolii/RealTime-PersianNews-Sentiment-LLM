import jdatetime
from datetime import datetime

# Convert Persian digits to English digits
def fa_to_en_numbers(s):
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

def parse_date(date_str):
    date_str = fa_to_en_numbers(date_str.strip())

    # ISO 8601 format (Gregorian)
    if "T" in date_str:
        dt = datetime.fromisoformat(date_str)
        return dt.replace(tzinfo=None).timestamp()
    
    # Short Persian date with month name: 10 azar(fa) 04 - 14:15
    if "-" in date_str and any(m in date_str for m in month_map):
        date_part, time_part = date_str.split(" - ")
        day, month_name, year = date_part.split()
        month = month_map[month_name]
        year = int(year)
        if year < 100:
            year += 1400
        hour, minute = map(int, time_part.split(":"))
        return jdatetime.datetime(year, month, int(day), hour, minute).togregorian().timestamp()

    # Full Persian date: 1404-09-10 14:34
    if "-" in date_str and " " in date_str:
        date_part, time_part = date_str.split(" ")
        year, month, day = map(int, date_part.split("-"))
        if year < 100:
            year += 1400
        hour, minute = map(int, time_part.split(":"))
        return jdatetime.datetime(year, month, day, hour, minute).togregorian().timestamp()


    raise ValueError(f"Unrecognized date format: {date_str}")
