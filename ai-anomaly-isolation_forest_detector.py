"""
Isolation Forest and Rule-Based Anomaly Detection for AquaNest
Detects sudden usage spikes, nocturnal continuous flow, and pattern deviations.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os


class WaterAnomalyDetector:
    def __init__(self, contamination=0.04, random_state=42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=random_state,
            max_samples="auto"
        )
        self.is_fitted = False

    def extract_features(self, df):
        """
        Extract behavioral telemetry features:
        - hour: 0-23
        - day_of_week: 0-6
        - hourly_litres
        - rolling_mean_24h
        - ratio_to_baseline
        - is_night: 1 if hour in [0, 5], else 0
        """
        feats = pd.DataFrame()
        feats["hour"] = df["timestamp"].dt.hour
        feats["day_of_week"] = df["timestamp"].dt.dayofweek
        feats["hourly_litres"] = df["litres"]

        rolling_mean = df["litres"].rolling(window=24, min_periods=1).mean()
        feats["rolling_mean_24h"] = rolling_mean
        feats["ratio_to_baseline"] = df["litres"] / (rolling_mean + 1.0)
        feats["is_night"] = feats["hour"].apply(lambda h: 1 if 0 <= h <= 5 else 0)

        return feats.fillna(0.0)

    def fit(self, historical_df):
        features = self.extract_features(historical_df)
        self.model.fit(features)
        self.is_fitted = True
        return self

    def detect(self, current_reading):
        """
        Evaluate a reading:
        current_reading dict: {
            'house_id': 'H104',
            'timestamp': pd.Timestamp,
            'litres': float,
            'rolling_mean_24h': float,
            'continuous_night_hours': int
        }
        Returns: (is_anomaly: bool, anomaly_score: float, reason: str, recommendation: str)
        """
        hour = current_reading["timestamp"].hour
        litres = current_reading["litres"]
        baseline = max(1.0, current_reading.get("rolling_mean_24h", 15.0))
        night_hours = current_reading.get("continuous_night_hours", 0)

        # Rule 1: High nocturnal continuous flow (e.g. leaking toilet/flapper)
        if 0 <= hour <= 5 and litres > 35.0 and night_hours >= 3:
            return (
                True,
                0.92,
                f"Continuous nocturnal flow ({litres:.1f} L/h) detected across {night_hours} consecutive hours without pause.",
                "Inspect internal toilet flapper valves, overflow pipes, and concealed fixtures."
            )

        # Rule 2: Sudden acute surge exceeding 3.5x baseline
        if litres > (baseline * 3.5) and litres > 150.0:
            return (
                True,
                0.85,
                f"Acute consumption spike ({litres:.1f} L/h) exceeding 3.5x typical baseline ({baseline:.1f} L/h).",
                "Check for unattended open taps, appliance fill hose failures, or external wash activity."
            )

        # Statistical / Isolation Forest scoring
        if self.is_fitted:
            features_df = pd.DataFrame([{
                "hour": hour,
                "day_of_week": current_reading["timestamp"].dayofweek,
                "hourly_litres": litres,
                "rolling_mean_24h": baseline,
                "ratio_to_baseline": litres / baseline,
                "is_night": 1 if 0 <= hour <= 5 else 0
            }])
            raw_score = self.model.decision_function(features_df)[0]
            # Normalise score to 0.0 (normal) - 1.0 (anomalous)
            anomaly_score = float(np.clip(0.5 - (raw_score * 2.5), 0.0, 1.0))
            is_anomaly = anomaly_score > 0.65
            reason = "Statistically improbable deviation from learned apartment profile." if is_anomaly else "Normal"
            recommendation = "Review recent appliance usage logs." if is_anomaly else "No action needed."
            return (is_anomaly, round(anomaly_score, 2), reason, recommendation)

        return (False, 0.15, "Normal consumption profile", "None required.")


if __name__ == "__main__":
    detector = WaterAnomalyDetector()
    sample_normal = {
        "house_id": "H101",
        "timestamp": pd.Timestamp("2026-09-18 08:30:00"),
        "litres": 22.5,
        "rolling_mean_24h": 18.0,
        "continuous_night_hours": 0
    }
    sample_anomaly = {
        "house_id": "H104",
        "timestamp": pd.Timestamp("2026-09-18 03:00:00"),
        "litres": 55.0,
        "rolling_mean_24h": 12.0,
        "continuous_night_hours": 4
    }

    print("Normal test:", detector.detect(sample_normal))
    print("Anomaly test:", detector.detect(sample_anomaly))
