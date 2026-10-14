"""Known inputs and exact expected country-comparison results."""

import unittest
from datetime import datetime

from eva.analysis import compare_countries, summarise_country
from eva.preparation import EVARecord
from tests.test_analysis import record


class CountryComparisonTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            record(1999, 50),
            record(2000, 1.5),
            record(2001, 2.5),
            EVARecord(datetime(2002, 12, 31), 3, "USA"),
            record(2003, 50),
            record(2000, 1, "Russia"),
            record(2002, 2, "Russia"),
            record(2004, 0),
        ]

    def test_both_year_boundaries_and_known_statistics(self):
        result = compare_countries(self.records, "USA", "Russia", 2000, 2002)
        self.assertEqual(result.country_a, ("USA", 3, 7, 7 / 3))
        self.assertEqual(result.country_b, ("Russia", 2, 3, 1.5))
        self.assertEqual(result.winner, "USA")
        self.assertEqual((result.start_year, result.end_year), (2000, 2002))

    def test_country_b_can_win(self):
        result = compare_countries(self.records, "Russia", "USA", 2000, 2002)
        self.assertEqual(result.winner, "USA")

    def test_single_year(self):
        result = compare_countries(self.records, "USA", "Russia", 2002, 2002)
        self.assertEqual(result.country_a, ("USA", 1, 3, 3))
        self.assertEqual(result.country_b, ("Russia", 1, 2, 2))

    def test_known_country_with_no_matches(self):
        result = compare_countries(self.records, "USA", "Russia", 2001, 2001)
        self.assertEqual(result.country_b, ("Russia", 0, 0, None))
        self.assertEqual(result.winner, "USA")

    def test_both_countries_empty_is_a_tie(self):
        result = compare_countries(self.records, "USA", "Russia", 2025, 2026)
        self.assertEqual(result.country_a, ("USA", 0, 0, None))
        self.assertEqual(result.country_b, ("Russia", 0, 0, None))
        self.assertIsNone(result.winner)

    def test_zero_duration_is_counted_and_average_is_available(self):
        result = compare_countries(self.records, "USA", "Russia", 2004, 2004)
        self.assertEqual(result.country_a, ("USA", 1, 0, 0))
        self.assertEqual(result.country_b, ("Russia", 0, 0, None))
        self.assertIsNone(result.winner)

    def test_equal_nonzero_totals_and_rounding_noise(self):
        records = [record(2000, 0.1), record(2000, 0.2), record(2000, 0.3, "Russia")]
        result = compare_countries(records, "USA", "Russia", 2000, 2000)
        self.assertAlmostEqual(result.country_a.total_hours, 0.3)
        self.assertEqual(result.country_b.total_hours, 0.3)
        self.assertIsNone(result.winner)

    def test_same_country_is_a_tie(self):
        result = compare_countries(self.records, "USA", "USA", 2000, 2002)
        self.assertEqual(result.country_a, result.country_b)
        self.assertIsNone(result.winner)

    def test_names_ignore_case_and_surrounding_spaces(self):
        result = compare_countries(iter(self.records), " usa ", "RUSSIA", 2000, 2002)
        self.assertEqual(result.country_a.country, "USA")
        self.assertEqual(result.country_b.country, "Russia")
        self.assertEqual(result.country_a.total_hours, 7)

    def test_unknown_country_is_rejected_even_in_an_empty_period(self):
        for a, b in (("Atlantis", "USA"), ("USA", "Atlantis")):
            with self.subTest(a=a, b=b), self.assertRaisesRegex(ValueError, "Unknown country"):
                compare_countries(self.records, a, b, 2025, 2026)

    def test_invalid_year_ranges(self):
        for start, end in ((2002, 2000), (0, 2000), (2000, 10000), ("2000", 2002), (2000.5, 2002), (True, 2002)):
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                compare_countries(self.records, "USA", "Russia", start, end)

    def test_empty_dataset_and_invalid_country_names(self):
        with self.assertRaisesRegex(ValueError, "Unknown country"):
            compare_countries([], "USA", "Russia", 2000, 2002)
        for name in ("", " ", None, 42):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Country must"):
                compare_countries(self.records, name, "Russia", 2000, 2002)

    def test_summary_reuses_existing_analysis_without_mutating_records(self):
        before = list(self.records)
        self.assertEqual(summarise_country(iter(self.records), "USA", 2000, 2002), ("USA", 3, 7, 7 / 3))
        self.assertEqual(self.records, before)


if __name__ == "__main__":
    unittest.main()
