"""Compare the new entry point against the original captured behaviour."""

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

os.environ["MPLBACKEND"] = "Agg"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from eva.loading import load_data
from eva.preparation import prepare_records

ROOT = Path(__file__).resolve().parents[1]


class LegacyRegressionTests(unittest.TestCase):
    def test_original_reports_and_every_plot_value(self):
        baseline = json.loads((ROOT / "tests/fixtures/inherited_baseline.json").read_text())
        self.assertEqual(
            hashlib.sha256((ROOT / "eva-data.json").read_bytes()).hexdigest(),
            baseline["data_sha256"],
        )
        records = prepare_records(load_data(ROOT / "eva-data.json"))
        for country, expected in baseline["runs"].items():
            with self.subTest(country=country), tempfile.TemporaryDirectory() as directory:
                plt.close("all")
                plots = []

                def capture():
                    axes = plt.gca()
                    series = []
                    for line in axes.lines:
                        dates = [d.isoformat() for d in line.get_xdata(orig=True)]
                        hours = [float(h) for h in line.get_ydata(orig=True)]
                        serialised = json.dumps({"dates": dates, "hours": hours}, sort_keys=True)
                        series.append({
                            "count": len(hours),
                            "total_hours": hours[-1] if hours else 0,
                            "sha256": hashlib.sha256(serialised.encode()).hexdigest(),
                        })
                    plots.append({
                        "title": axes.get_title(),
                        "xlabel": axes.get_xlabel(),
                        "ylabel": axes.get_ylabel(),
                        "series": series,
                    })

                stdout = io.StringIO()
                previous = Path.cwd()
                try:
                    os.chdir(directory)
                    with patch("builtins.input", side_effect=[str(ROOT / "eva-data.json"), country]), \
                            patch("sys.argv", [str(ROOT / "evacodev2.py")]), \
                            patch.object(plt, "show", side_effect=capture), \
                            patch.object(plt, "savefig") as save, \
                            contextlib.redirect_stdout(stdout):
                        with self.assertRaises(SystemExit) as exit_result:
                            runpy.run_path(str(ROOT / "evacodev2.py"), run_name="__main__")
                    self.assertEqual(exit_result.exception.code, 0)
                    self.assertEqual(stdout.getvalue(), expected["stdout"])
                    self.assertEqual(plots, expected["plots"])
                    self.assertEqual(len(records), expected["prepared_count"])
                    self.assertEqual(save.call_count, 2)
                    for call in save.call_args_list:
                        self.assertEqual(call.args, (f"cumulative_duration_{country}.png",))
                finally:
                    os.chdir(previous)
                    plt.close("all")


if __name__ == "__main__":
    unittest.main()
