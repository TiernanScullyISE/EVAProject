"""Exercise the user interface with a small real JSON file."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from eva.application import main


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "evas.json"
        self.path.write_text(json.dumps([
            {"date": "2000-01-01", "duration": "1:30", "country": "USA"},
            {"date": "2002-12-31", "duration": "2:30", "country": "USA"},
            {"date": "2000-01-01", "duration": "1:00", "country": "Russia"},
        ]), encoding="utf-8")

    def args(self, start="2000", end="2002", country_b="Russia"):
        return [
            "compare", "--file", str(self.path),
            "--country-a", "USA", "--country-b", country_b,
            "--start-year", start, "--end-year", end,
        ]

    def run_command(self, args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            status = main(args)
        return status, stdout.getvalue()

    def test_comparison_displays_exact_report(self):
        status, text = self.run_command(self.args())
        self.assertEqual(status, 0)
        self.assertEqual(text, (
            "\nEVA comparison: 2000 to 2002 (inclusive)\n"
            "\nUSA\nTotal number of EVAs: 2\nTotal EVA duration (hours): 4.00\n"
            "Average EVA duration (hours): 2.00\n"
            "\nRussia\nTotal number of EVAs: 1\nTotal EVA duration (hours): 1.00\n"
            "Average EVA duration (hours): 1.00\n"
            "\nGreater total EVA duration: USA\n"
        ))

    def test_comparison_can_prompt_for_all_inputs(self):
        with patch("builtins.input", side_effect=[str(self.path), "USA", "Russia", "2000", "2002"]):
            status, text = self.run_command(["compare"])
        self.assertEqual(status, 0)
        self.assertIn("Total EVA duration (hours): 4.00", text)

    def test_empty_results_display_zero_unavailable_and_tie(self):
        status, text = self.run_command(self.args("2025", "2025"))
        self.assertEqual(status, 0)
        self.assertEqual(text.count("Total number of EVAs: 0"), 2)
        self.assertEqual(text.count("Total EVA duration (hours): 0.00"), 2)
        self.assertEqual(text.count("Average EVA duration (hours): unavailable"), 2)
        self.assertIn("Tie: both countries have equal total EVA duration.", text)

    def test_invalid_range_and_unknown_country_are_friendly_errors(self):
        for args, message in (
            (self.args("2002", "2000"), "Start year must not be after end year."),
            (self.args(country_b="Atlantis"), "Unknown country: Atlantis"),
        ):
            with self.subTest(args=args):
                status, text = self.run_command(args)
                self.assertEqual(status, 1)
                self.assertIn("Error: " + message, text)
                self.assertNotIn("Traceback", text)

    def test_non_numeric_interactive_year(self):
        with patch("builtins.input", side_effect=[str(self.path), "USA", "Russia", "oops"]):
            status, text = self.run_command(["compare"])
        self.assertEqual(status, 1)
        self.assertIn("Years must be whole numbers", text)

    def test_non_numeric_argument_has_usage_error(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as result:
            main(self.args("oops"))
        self.assertEqual(result.exception.code, 2)
        self.assertIn("invalid int value", stderr.getvalue())

    def test_missing_file_and_malformed_data_do_not_raise_tracebacks(self):
        self.path.unlink()
        status, text = self.run_command(self.args())
        self.assertEqual(status, 1)
        self.assertTrue(text.startswith("Error:"))
        for raw in ("not JSON", "{}", '[{"date": "bad", "duration": "1:00", "country": "USA"}]'):
            self.path.write_text(raw, encoding="utf-8")
            with self.subTest(raw=raw):
                status, text = self.run_command(self.args())
                self.assertEqual(status, 1)
                self.assertTrue(text.startswith("Error:"))
                self.assertNotIn("Traceback", text)

    def test_cancelled_input_is_handled(self):
        with patch("builtins.input", side_effect=EOFError):
            status, text = self.run_command(["compare"])
        self.assertEqual(status, 1)
        self.assertEqual(text, "Error: Input cancelled.\n")

    def test_legacy_country_matching_ignores_case_and_spaces(self):
        for country in ("USA", "usa", "UsA", " usa "):
            with self.subTest(country=country), \
                    patch("builtins.input", side_effect=[str(self.path), country]), \
                    patch("eva.application.plot_cumulative") as plot:
                status, _ = self.run_command([])
                self.assertEqual(status, 0)
                self.assertEqual(plot.call_count, 2)
                self.assertEqual(plot.call_args_list[1].args[1], [1.5, 4.0])

    def test_legacy_missing_file_is_handled(self):
        with patch("builtins.input", return_value=str(self.path.parent / "missing.json")):
            status, text = self.run_command([])
        self.assertEqual(status, 1)
        self.assertTrue(text.startswith("Error:"))


if __name__ == "__main__":
    unittest.main()
