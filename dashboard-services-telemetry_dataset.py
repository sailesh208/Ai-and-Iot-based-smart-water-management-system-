"""Local telemetry dataset storage and AquaNest-shaped sample generation."""

import os
import random
import tempfile
from pathlib import Path

import pandas as pd

from .resident_profiles import RESIDENT_PROFILES

DATASET_COLUMNS = [
    "timestamp",
    "house_id",
    "litres",
    "rolling_mean_24h",
    "continuous_night_hours",
    "source",
]
HOUSE_IDS = [profile["houseId"] for profile in RESIDENT_PROFILES]
MANUAL_ENTRY_COLUMNS = DATASET_COLUMNS[:-1]
DATASET_PATH = Path(__file__).resolve().parents[2] / "exports" / "aquanest_telemetry_dataset.csv"


def validate_records(records, source="manual"):
    """Validate and normalize rows to the AquaNest anomaly-detection input schema."""
    data = records.copy() if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
    if data.empty:
        raise ValueError("Enter or upload at least one telemetry record.")

    missing_columns = [column for column in MANUAL_ENTRY_COLUMNS if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing_columns)}")

    data = data.loc[:, MANUAL_ENTRY_COLUMNS].copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce", format="mixed")
    invalid_timestamps = data["timestamp"].isna()
    if invalid_timestamps.any():
        rows = ", ".join(str(index + 1) for index in data.index[invalid_timestamps])
        raise ValueError(f"Invalid or missing timestamp on dataset row(s): {rows}.")
    data["timestamp"] = data["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    data["house_id"] = data["house_id"].astype("string").str.strip().str.upper()
    invalid_houses = ~data["house_id"].isin(HOUSE_IDS)
    if invalid_houses.any():
        rows = ", ".join(str(index + 1) for index in data.index[invalid_houses])
        raise ValueError(f"Use one of {', '.join(HOUSE_IDS)} for house_id (row(s): {rows}).")

    for column in ("litres", "rolling_mean_24h", "continuous_night_hours"):
        data[column] = pd.to_numeric(data[column], errors="coerce")
        invalid_values = data[column].isna()
        if invalid_values.any():
            rows = ", ".join(str(index + 1) for index in data.index[invalid_values])
            raise ValueError(f"Invalid or missing {column} value on dataset row(s): {rows}.")

    if (data["litres"] < 0).any():
        raise ValueError("litres must be zero or greater.")
    if (data["rolling_mean_24h"] < 0).any():
        raise ValueError("rolling_mean_24h must be zero or greater.")
    night_hours = data["continuous_night_hours"]
    if ((night_hours < 0) | (night_hours > 6) | (night_hours % 1 != 0)).any():
        raise ValueError("continuous_night_hours must be a whole number from 0 to 6.")

    data["source"] = source
    return data.loc[:, DATASET_COLUMNS].reset_index(drop=True)


def load_dataset(path=DATASET_PATH):
    """Load saved telemetry rows, returning an empty dataset when none is saved yet."""
    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=DATASET_COLUMNS)

    data = pd.read_csv(path)
    missing_columns = [column for column in DATASET_COLUMNS if column not in data.columns]
    if missing_columns:
        raise ValueError(f"Saved dataset is missing columns: {', '.join(missing_columns)}")
    return data.loc[:, DATASET_COLUMNS]


def append_records(records, source="manual", path=DATASET_PATH):
    """Validate rows and append them to the project exports dataset."""
    path = Path(path)
    new_data = validate_records(records, source=source)
    existing_data = load_dataset(path)
    combined = pd.concat([existing_data, new_data], ignore_index=True)

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8-sig",
        newline="",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    ) as temporary_file:
        temporary_path = Path(temporary_file.name)

    try:
        combined.to_csv(temporary_path, index=False, encoding="utf-8-sig")
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return len(new_data), combined


def generate_synthetic_records(days=30, seed=42):
    """Generate hourly apartment water readings with normal patterns and sample anomalies."""
    if not isinstance(days, int) or days < 1:
        raise ValueError("days must be a positive whole number.")

    rng = random.Random(seed)
    end_time = pd.Timestamp.now().floor("h")
    start_time = end_time - pd.Timedelta(days=days)
    records = []

    for profile in RESIDENT_PROFILES:
        house_id = profile["houseId"]
        usage_scale = profile["baseDailyUsageLitres"] / 350.0
        history = []
        continuous_night_hours = 0
        for hour_index in range(days * 24):
            timestamp = start_time + pd.Timedelta(hours=hour_index)
            hour = timestamp.hour
            day_index = hour_index // 24

            if 6 <= hour <= 9 or 18 <= hour <= 21:
                litres = rng.gauss(32.0, 5.0) * usage_scale
            elif hour <= 5:
                litres = rng.gauss(2.5, 1.0) * usage_scale
            else:
                litres = rng.gauss(16.0, 3.5) * usage_scale
            if timestamp.day_of_week >= 5:
                litres *= 1.25

            if day_index % 14 == 0 and 1 <= hour <= 3:
                litres = (48.0 + rng.random() * 5.0) * usage_scale
            elif day_index > 0 and (day_index + 1) % 30 == 0 and hour == 14:
                litres = (180.0 + rng.random() * 30.0) * usage_scale

            litres = round(max(0.5, litres), 2)
            if hour <= 5 and litres > 35.0:
                continuous_night_hours += 1
            else:
                continuous_night_hours = 0

            baseline_values = history[-24:]
            rolling_mean = round(
                sum(baseline_values) / len(baseline_values) if baseline_values else 15.0,
                2,
            )
            records.append({
                "timestamp": timestamp,
                "house_id": house_id,
                "litres": litres,
                "rolling_mean_24h": rolling_mean,
                "continuous_night_hours": continuous_night_hours,
            })
            history.append(litres)

    return validate_records(records, source="synthetic")
