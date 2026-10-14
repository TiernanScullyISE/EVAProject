"""Pure calculations: no files, user input, printing or plotting."""

from itertools import accumulate
from math import isclose
from typing import NamedTuple


class DurationCategories(NamedTuple):
    short: int
    standard: int
    long: int

    @property
    def total(self):
        return self.short + self.standard + self.long


def select_country(records, country, *, case_sensitive=True):
    """Use exact matching by default; comparison accepts user-friendly names."""
    if not case_sensitive:
        name = country.strip().casefold()
        return [record for record in records if record.country.strip().casefold() == name]
    return [record for record in records if record.country == country]


def cumulative_hours(records):
    """Return dates and running duration totals, preserving input order."""
    records = list(records)
    return (
        [record.date for record in records],
        list(accumulate(record.duration_hours for record in records)),
    )


def duration_categories(records):
    """Count short (<4), standard (4 to <7), and long (>=7) EVAs."""
    short = standard = long = 0
    for record in records:
        if record.duration_hours < 4:
            short += 1
        elif record.duration_hours < 7:
            standard += 1
        else:
            long += 1
    return DurationCategories(short, standard, long)


class CountrySummary(NamedTuple):
    country: str
    count: int
    total_hours: float
    average_hours: float | None


class CountryComparison(NamedTuple):
    country_a: CountrySummary
    country_b: CountrySummary
    start_year: int
    end_year: int
    winner: str | None  # None means a tie.


def validate_year_range(start_year, end_year):
    """Both ends must be whole calendar years, in ascending order."""
    if any(type(year) is not int or not 1 <= year <= 9999 for year in (start_year, end_year)):
        raise ValueError("Years must be whole numbers between 1 and 9999.")
    if start_year > end_year:
        raise ValueError("Start year must not be after end year.")


def summarise_country(records, country, start_year, end_year):
    """Summarise a known country over an inclusive period, reusing running totals."""
    validate_year_range(start_year, end_year)
    records = list(records)
    names = sorted({record.country for record in records})
    if not isinstance(country, str) or not country.strip():
        raise ValueError("Country must be a non-empty name.")
    requested = country.strip().casefold()
    name = next((name for name in names if name.strip().casefold() == requested), None)
    if name is None:
        available = ', '.join(names) or '(none)'
        raise ValueError(f"Unknown country: {country}. Available countries: {available}.")
    matching = [
        record for record in select_country(records, name, case_sensitive=False)
        if start_year <= record.date.year <= end_year
    ]
    _, totals = cumulative_hours(matching)
    total = totals[-1] if totals else 0.0
    count = len(matching)
    return CountrySummary(name, count, total, total / count if count else None)


def compare_countries(records, country_a, country_b, start_year, end_year):
    """Return both summaries and the country with greater duration, or a tie."""
    records = list(records)
    a = summarise_country(records, country_a, start_year, end_year)
    b = summarise_country(records, country_b, start_year, end_year)
    # Ignore floating-point noise far smaller than the source data's one-minute precision.
    if isclose(a.total_hours, b.total_hours, rel_tol=0.0, abs_tol=1e-9):
        winner = None
    else:
        winner = a.country if a.total_hours > b.total_hours else b.country
    return CountryComparison(a, b, start_year, end_year, winner)
