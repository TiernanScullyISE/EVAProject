"""Read JSON without interpreting EVA records."""

import json


def load_data(path):
    """Return the raw JSON value from a user-selected UTF-8 file."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
