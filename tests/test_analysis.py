"""Known-input tests for inherited calculations."""

import unittest
from datetime import datetime

from eva.analysis import cumulative_hours, duration_categories, select_country
from eva.preparation import EVARecord, prepare_records


def record(year, hours, country="USA"):
    return EVARecord(datetime(year, 1, 1), hours, country)


class ExistingAnalysisTests(unittest.TestCase):
    def test_cumulative_hours_has_known_results(self):
        records = [record(2000, 1.5), record(2001, 2), record(2002, 0)]
        dates, hours = cumulative_hours(iter(records))
        self.assertEqual(dates, [item.date for item in records])
        self.assertEqual(hours, [1.5, 3.5, 3.5])

    def test_category_boundaries(self):
        result = duration_categories([record(2000, h) for h in (0, 3.99, 4, 6.99, 7, 8)])
        self.assertEqual(result, (2, 2, 2))
        self.assertEqual(result.total, 6)

    def test_empty_analysis(self):
        self.assertEqual(cumulative_hours([]), ([], []))
        self.assertEqual(duration_categories([]), (0, 0, 0))

    def test_country_selection_is_exact_and_reusable(self):
        records = [record(2000, 1), record(2000, 2, "Russia")]
        self.assertEqual(select_country(records, "Russia"), [records[1]])
        self.assertEqual(select_country(records, "usa"), [])

    def test_preparation_sorts_skips_incomplete_and_keeps_zero(self):
        data = [
            {"date": "2001-01-01", "duration": "1:30", "country": "USA"},
            {"duration": "2:00", "country": "USA"},
            {"date": "2000-01-01", "duration": "0:00", "country": "Russia"},
        ]
        self.assertEqual(prepare_records(data), [record(2000, 0, "Russia"), record(2001, 1.5)])

    def test_preparation_rejects_malformed_duration(self):
        with self.assertRaisesRegex(ValueError, "Invalid EVA record 1"):
            prepare_records([{"date": "2000-01-01", "duration": "1:60", "country": "USA"}])


if __name__ == "__main__":
    unittest.main()
