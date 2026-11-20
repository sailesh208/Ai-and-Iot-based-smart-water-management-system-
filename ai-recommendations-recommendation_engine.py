"""
Recommendation Engine for AquaNest
Generates contextual water-saving advice and inspection prompts based on telemetry.
"""


class WaterRecommendationEngine:
    def __init__(self):
        pass

    def evaluate(self, house_stats, active_leaks, anomalies):
        """
        Produces prioritized recommendations:
        - house_stats: list of dicts with house telemetry
        - active_leaks: list of active leakage alert dicts
        - anomalies: list of detected anomalies
        """
        recs = []

        # 1. Evaluate Leakage Alerts
        for leak in active_leaks:
            if leak.get("type") == "TANK_LEAKAGE":
                recs.append({
                    "id": f"REC_TL_{len(recs)+1}",
                    "target": "ADMIN",
                    "house_id": "ALL",
                    "title": "Overhead Tank Ingress/Seepage Inspection",
                    "message": "Continuous loss detected while pump is idle. Check the tank bottom drain valve, float valve seating, and delivery riser joint.",
                    "category": "LEAK_PREVENTION",
                    "priority": "HIGH"
                })
            elif leak.get("type") == "PIPE_LEAKAGE":
                zone = leak.get("zone", "Main Distribution Pipe")
                recs.append({
                    "id": f"REC_PL_{len(recs)+1}",
                    "target": "ADMIN",
                    "house_id": "ALL",
                    "title": f"Distribution Line Pressure Test in {zone}",
                    "message": f"Distribution flow mismatch of {leak.get('flowMismatchLpm', 0)} L/min observed. Perform acoustic leak tracing or isolate Wing valve for pressure drop validation.",
                    "category": "LEAK_PREVENTION",
                    "priority": "CRITICAL"
                })

        # 2. Evaluate House Anomalies
        for anom in anomalies:
            h_id = anom.get("house_id", "")
            recs.append({
                "id": f"REC_ANOM_{len(recs)+1}",
                "target": "RESIDENT",
                "house_id": h_id,
                "title": f"Fixtures Check for Flat {h_id}",
                "message": f"Abnormal flow detected ({anom.get('actual_usage_litres', 0)} L). Common culprit: silent toilet flapper valve leak (wastes 300-600 L/day). Inspect cistern seals.",
                "category": "WATER_SAVING",
                "priority": "HIGH"
            })

        # 3. Baseline Apartment Conservation Advice
        recs.append({
            "id": f"REC_GEN_1",
            "target": "ALL",
            "house_id": "ALL",
            "title": "Aerate High-Flow Taps",
            "message": "Installing 3.5 L/min low-flow aerators on kitchen and bathroom washbasins reduces household consumption by up to 35% without reducing water pressure feel.",
            "category": "WATER_SAVING",
            "priority": "MEDIUM"
        })

        recs.append({
            "id": f"REC_GEN_2",
            "target": "ADMIN",
            "house_id": "ALL",
            "title": "Contactor and Pump Run-Time Balancing",
            "message": "Current daily pump runs are optimized within 38-45 minute cycles. Ensure delivery check valves (non-return valves) are cleaned monthly to prevent backflow churning.",
            "category": "PRESSURE_EFFICIENCY",
            "priority": "LOW"
        })

        return recs


if __name__ == "__main__":
    engine = WaterRecommendationEngine()
    dummy_leaks = [{"type": "TANK_LEAKAGE", "estimated_loss": 140}]
    dummy_anoms = [{"house_id": "H104", "actual_usage_litres": 540}]
    results = engine.evaluate([], dummy_leaks, dummy_anoms)
    for r in results:
        print(f"[{r['priority']}] {r['title']}: {r['message']}")
