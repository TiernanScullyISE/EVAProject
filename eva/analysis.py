"""Pure calculations: no files, user input, printing or plotting."""

from itertools import accumulate
from typing import NamedTuple


class DurationCategories(NamedTuple):
    short: int
    standard: int
    long: int

    @property
    def total(self):
        return self.short + self.standard + self.long


def select_country(records, country):
    """Preserve the inherited exact-match country filter."""
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
