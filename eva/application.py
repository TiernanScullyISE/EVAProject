"""Coordinate the inherited interactive application."""

from .analysis import cumulative_hours, duration_categories, select_country
from .loading import load_data
from .preparation import prepare_records
from .presentation import plot_cumulative, report_categories


def run_legacy():
    input_file = input("What is the data file name: ")
    data = load_data(input_file)
    country = input("Please input the country you want to see data for: ")
    records = prepare_records(data)
    output_path = f"cumulative_duration_{country}.png"
    for selected, label in (
        (records, "all countries"),
        (select_country(records, country), country),
    ):
        dates, hours = cumulative_hours(selected)
        plot_cumulative(dates, hours, label, output_path)
    report_categories(duration_categories(records))


def main():
    run_legacy()
    return 0
