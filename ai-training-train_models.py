"""
Model Training Script for AquaNest AI
Generates synthetic multi-week telemetry, trains Isolation Forest & Forecaster, and exports model artifacts.
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import Ridge


def generate_training_data(days=60):
    np.random.seed(42)
    records = []
    base_time = pd.Timestamp("2026-07-01 00:00:00")

    for hour_idx in range(days * 24):
        t = base_time + pd.Timedelta(hours=hour_idx)
        h = t.hour
        dow = t.dayofweek

        # Diurnal pattern
        if 6 <= h <= 9 or 18 <= h <= 21:
            base_litres = np.random.normal(32.0, 5.0)
        elif 0 <= h <= 5:
            base_litres = np.random.normal(2.5, 1.0)
        else:
            base_litres = np.random.normal(16.0, 3.5)

        if dow >= 5:  # weekend boost
            base_litres *= 1.25

        litres = max(0.5, base_litres)

        # Inject periodic synthetic anomalies
        if hour_idx in [120, 240, 480]:
            litres += 180.0  # acute burst spike

        records.append({
            "timestamp": t,
            "litres": litres
        })

    return pd.DataFrame(records)


def train_and_export():
    os.makedirs("models", exist_ok=True)
    df = generate_training_data(days=90)

    # Feature extraction
    features = pd.DataFrame()
    features["hour"] = df["timestamp"].dt.hour
    features["day_of_week"] = df["timestamp"].dt.dayofweek
    features["hourly_litres"] = df["litres"]
    rolling = df["litres"].rolling(window=24, min_periods=1).mean()
    features["rolling_mean_24h"] = rolling
    features["ratio_to_baseline"] = df["litres"] / (rolling + 1.0)
    features["is_night"] = features["hour"].apply(lambda h: 1 if 0 <= h <= 5 else 0)

    # Train Isolation Forest
    iso_forest = IsolationForest(n_estimators=100, contamination=0.03, random_state=42)
    iso_forest.fit(features)
    joblib.dump(iso_forest, os.path.join("models", "isolation_forest.joblib"))
    print("Exported: models/isolation_forest.joblib")

    # Train Ridge Forecaster
    # Create lag features
    features["lag_24"] = df["litres"].shift(24).fillna(df["litres"].mean())
    y = df["litres"]
    ridge = Ridge(alpha=1.0)
    ridge.fit(features, y)
    joblib.dump(ridge, os.path.join("models", "demand_forecaster.joblib"))
    print("Exported: models/demand_forecaster.joblib")


if __name__ == "__main__":
    train_and_export()
