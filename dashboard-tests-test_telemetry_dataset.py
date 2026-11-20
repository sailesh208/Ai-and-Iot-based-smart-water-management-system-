import tempfile
import unittest
from pathlib import Path

import pandas as pd

from dashboard.services.telemetry_dataset import (
    DATASET_COLUMNS,
    append_records,
    generate_synthetic_records,
    load_dataset,
    validate_records,
)


class TelemetryDatasetTests(unittest.TestCase):
    def test_manual_records_validate_and_append(self):
        record = {
            "timestamp": "2026-11-18 10:00:00",
            "house_id": "h101",
            "litres": 12.5,
            "rolling_mean_24h": 14.0,
            "continuous_night_hours": 0,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.csv"
            added, saved = append_records([record], path=path)

            self.assertEqual(added, 1)
            self.assertEqual(saved.loc[0, "house_id"], "H101")
            self.assertEqual(saved.loc[0, "source"], "manual")
            self.assertEqual(list(load_dataset(path).columns), DATASET_COLUMNS)

    def test_validation_rejects_unknown_apartment(self):
        record = {
            "timestamp": "2026-11-18 10:00:00",
            "house_id": "H999",
            "litres": 12.5,
            "rolling_mean_24h": 14.0,
            "continuous_night_hours": 0,
        }
        with self.assertRaisesRegex(ValueError, "house_id"):
            validate_records([record])

    def test_synthetic_dataset_covers_all_flats_and_expected_hours(self):
        records = generate_synthetic_records(days=1, seed=1)

        self.assertEqual(len(records), 20 * 24)
        self.assertEqual(set(records["house_id"]), {f"H{number}" for number in range(101, 121)})
        self.assertEqual(set(records["source"]), {"synthetic"})
        self.assertTrue(pd.api.types.is_numeric_dtype(records["litres"]))
        totals = records.groupby("house_id")["litres"].sum()
        self.assertEqual(totals.nunique(), 20)
        self.assertGreater(totals["H104"], totals["H101"])


if __name__ == "__main__":
    unittest.main()
