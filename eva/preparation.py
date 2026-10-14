"""Validate raw data and convert it into chronologically ordered records."""

from datetime import datetime
from typing import NamedTuple


class EVARecord(NamedTuple):
    """The shared record interface; durations are measured in hours."""

    date: datetime
    duration_hours: float
    country: str


def prepare_records(data):
    """Skip incomplete rows as before; reject malformed populated fields."""
    if not isinstance(data, list):
        raise ValueError("EVA data must be a JSON array.")
    records = []
    for index, eva in enumerate(data, start=1):
        if not isinstance(eva, dict):
            raise ValueError(f"EVA record {index} must be an object.")
        date_text = eva.get("date")
        duration_text = eva.get("duration")
        country_text = eva.get("country")
        if not date_text or not duration_text or not country_text:
            continue
        try:
            if not isinstance(country_text, str) or not country_text.strip():
                raise ValueError("country must be a non-empty string")
            date = datetime.fromisoformat(date_text)
            hours, minutes = map(int, duration_text.split(":"))
            if hours < 0 or not 0 <= minutes < 60:
                raise ValueError("duration must be non-negative H:MM")
        except (ValueError, TypeError, AttributeError) as error:
            raise ValueError(f"Invalid EVA record {index}: {error}") from error
        records.append(EVARecord(date, hours + minutes / 60, country_text))
    try:
        records.sort(key=lambda record: record.date)
    except TypeError as error:
        raise ValueError("EVA dates must use a consistent timezone format.") from error
    return records
