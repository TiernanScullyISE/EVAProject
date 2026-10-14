"""Coordinate the inherited workflow and the optional country comparison."""

import argparse

from .analysis import compare_countries, cumulative_hours, duration_categories, select_country
from .loading import load_data
from .preparation import prepare_records
from .presentation import plot_cumulative, report_categories, report_comparison, report_error


def run_legacy():
    input_file = input("What is the data file name: ")
    data = load_data(input_file)
    country = input("Please input the country you want to see data for: ")
    records = prepare_records(data)
    output_path = f"cumulative_duration_{country}.png"
    for selected, label in (
        (records, "all countries"),
        (select_country(records, country, case_sensitive=False), country),
    ):
        dates, hours = cumulative_hours(selected)
        plot_cumulative(dates, hours, label, output_path)
    report_categories(duration_categories(records))


def run_comparison(args):
    input_file = args.file if args.file is not None else input("What is the data file name: ")
    country_a = args.country_a if args.country_a is not None else input("Country A: ")
    country_b = args.country_b if args.country_b is not None else input("Country B: ")
    try:
        start_year = args.start_year if args.start_year is not None else int(input("Start year: "))
        end_year = args.end_year if args.end_year is not None else int(input("End year: "))
    except ValueError as error:
        raise ValueError("Years must be whole numbers between 1 and 9999.") from error
    records = prepare_records(load_data(input_file))
    comparison = compare_countries(records, country_a, country_b, start_year, end_year)
    report_comparison(comparison)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Plot EVA activity or compare two countries.")
    commands = parser.add_subparsers(dest="command")
    compare = commands.add_parser("compare", help="Compare EVA activity over an inclusive year range")
    compare.add_argument("--file", help="JSON data file; prompts if omitted")
    compare.add_argument("--country-a", help="First country; prompts if omitted")
    compare.add_argument("--country-b", help="Second country; prompts if omitted")
    compare.add_argument("--start-year", type=int, help="First included year; prompts if omitted")
    compare.add_argument("--end-year", type=int, help="Last included year; prompts if omitted")
    args = parser.parse_args(argv)
    try:
        if args.command == "compare":
            run_comparison(args)
        else:
            run_legacy()
    except (OSError, ValueError) as error:
        report_error(str(error))
        return 1
    except (EOFError, KeyboardInterrupt):
        report_error("Input cancelled.")
        return 1
    return 0
