"""Display calculated results; no JSON loading or EVA calculations."""

import matplotlib.pyplot as plt


def plot_cumulative(dates, hours, country, output_path):
    """Keep the inherited plotting sequence, labels and saved PNG."""
    plt.plot(dates, hours)
    plt.title("Cumulative hours for " + country)
    plt.xlabel("Year")
    plt.ylabel("Cumulative EVA duration (hours)")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()


def report_categories(categories, country="all countries"):
    print(f"\nEVA duration categories for {country}")
    print("--------------------------------------")
    if categories.total == 0:
        print("No EVA records found.")
        return
    for label, count in (
        ("Short (Less than 4 hours)", categories.short),
        ("Standard (4 to 7 hours)", categories.standard),
        ("Long (More than 7 hours)", categories.long),
    ):
        print(f"{label}: {count}({count / categories.total * 100:.2f}%)")


def report_comparison(comparison):
    print(f"\nEVA comparison: {comparison.start_year} to {comparison.end_year} (inclusive)")
    for summary in (comparison.country_a, comparison.country_b):
        average = "unavailable" if summary.average_hours is None else f"{summary.average_hours:.2f}"
        print(f"\n{summary.country}")
        print(f"Total number of EVAs: {summary.count}")
        print(f"Total EVA duration (hours): {summary.total_hours:.2f}")
        print(f"Average EVA duration (hours): {average}")
    if comparison.winner is None:
        print("\nTie: both countries have equal total EVA duration.")
    else:
        print(f"\nGreater total EVA duration: {comparison.winner}")


def report_error(message):
    print(f"Error: {message}")
