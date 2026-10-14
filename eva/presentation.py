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
