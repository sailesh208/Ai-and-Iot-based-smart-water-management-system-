"""
Pytest suite for AquaNest AI modules (Anomaly Detection, Demand Forecasting, Recommendations)
"""

import pytest
import pandas as pd
from anomaly.isolation_forest_detector import WaterAnomalyDetector
from forecasting.demand_forecaster import WaterDemandForecaster
from recommendations.recommendation_engine import WaterRecommendationEngine


def test_anomaly_detection_rules():
    detector = WaterAnomalyDetector()

    # Test nocturnal continuous leak in H104
    reading_leak = {
        "house_id": "H104",
        "timestamp": pd.Timestamp("2026-09-18 03:00:00"),
        "litres": 48.0,
        "rolling_mean_24h": 12.0,
        "continuous_night_hours": 4
    }
    is_anom, score, reason, rec = detector.detect(reading_leak)
    assert is_anom is True
    assert score > 0.8
    assert "nocturnal" in reason.lower()
    assert "toilet" in rec.lower()

    # Test normal daytime reading in H101
    reading_normal = {
        "house_id": "H101",
        "timestamp": pd.Timestamp("2026-09-18 10:00:00"),
        "litres": 14.0,
        "rolling_mean_24h": 15.0,
        "continuous_night_hours": 0
    }
    is_anom_n, score_n, _, _ = detector.detect(reading_normal)
    assert is_anom_n is False
    assert score_n < 0.5


def test_demand_forecaster():
    forecaster = WaterDemandForecaster()
    forecasts = forecaster.generate_forecast("ALL", days=7)

    assert len(forecasts) == 7
    for f in forecasts:
        assert f["predicted_litres"] > 0
        assert f["lower_bound_litres"] <= f["predicted_litres"]
        assert f["upper_bound_litres"] >= f["predicted_litres"]
        assert "peak_period" in f

    acc = forecaster.evaluate_historical_accuracy()
    assert "MAE" in acc
    assert "R2_Score" in acc


def test_recommendation_engine():
    engine = WaterRecommendationEngine()
    leaks = [{"type": "PIPE_LEAKAGE", "zone": "Wing B Riser", "flowMismatchLpm": 6.8}]
    anoms = [{"house_id": "H104", "actual_usage_litres": 540}]

    recs = engine.evaluate([], leaks, anoms)
    assert len(recs) >= 3

    # Check pipe leak recommendation
    pipe_rec = [r for r in recs if "Distribution Line" in r["title"]]
    assert len(pipe_rec) == 1
    assert pipe_rec[0]["priority"] == "CRITICAL"
