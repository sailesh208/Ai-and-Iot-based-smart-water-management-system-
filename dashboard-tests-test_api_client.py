import unittest
from unittest.mock import Mock, patch

import requests

from dashboard.services.api_client import AquaNestApiClient


class AquaNestApiClientTests(unittest.TestCase):
    def test_set_pump_state_maps_off_to_stop(self):
        client = AquaNestApiClient()
        with patch.object(
            client,
            "control_pump",
            return_value={"success": True, "message": "Pump switched OFF."},
        ) as control_pump:
            ok, message = client.set_pump_state("OFF")

        self.assertTrue(ok)
        self.assertEqual(message, "Pump switched OFF.")
        control_pump.assert_called_once_with("STOP", mode="MANUAL", role="ADMIN")

    def test_set_pump_mode_preserves_current_pump_state(self):
        client = AquaNestApiClient()
        with patch.object(client, "get_pump_status", return_value={"status": "ON"}):
            with patch.object(
                client,
                "control_pump",
                return_value={"success": True, "message": "Mode set to AUTO."},
            ) as control_pump:
                ok, message = client.set_pump_mode("AUTO")

        self.assertTrue(ok)
        self.assertEqual(message, "Mode set to AUTO.")
        control_pump.assert_called_once_with("START", mode="AUTO", role="ADMIN")

    def test_set_pump_state_rejects_invalid_state(self):
        client = AquaNestApiClient()
        with patch.object(client, "control_pump") as control_pump:
            ok, message = client.set_pump_state("PAUSED")

        self.assertFalse(ok)
        self.assertIn("Invalid pump state", message)
        control_pump.assert_not_called()

    def test_offline_pump_control_state_is_shared_by_all_status_readers(self):
        client = AquaNestApiClient()
        with patch.object(client, "_request", side_effect=requests.ConnectionError):
            result = client.control_pump("START", mode="MANUAL")
            summary, summary_is_live = client.get_summary()
            tank, tank_is_live = client.get_tank_current()
            pump = client.get_pump_status()
            history = client.get_tank_history()
            logs = client.get_pump_logs()

        self.assertTrue(result["success"])
        self.assertFalse(result["_is_live"])
        self.assertIn("hardware was not actuated", result["message"])
        self.assertFalse(summary_is_live)
        self.assertFalse(tank_is_live)
        self.assertEqual((summary["pumpStatus"], summary["pumpMode"]), ("ON", "MANUAL"))
        self.assertEqual((tank["pumpStatus"], tank["pumpMode"]), ("ON", "MANUAL"))
        self.assertEqual((pump["status"], pump["mode"]), ("ON", "MANUAL"))
        self.assertEqual(history[-1]["pumpStatus"], "ON")
        self.assertEqual(logs[0]["trigger"], "LOCAL_DEMO_CONTROL")

    def test_backend_rejection_does_not_change_demo_state(self):
        client = AquaNestApiClient()
        response = Mock(status_code=403)
        with patch.object(client, "_request", return_value=response):
            result = client.control_pump("START", mode="MANUAL")

        self.assertFalse(result["success"])
        self.assertIn("HTTP 403", result["message"])
        self.assertIsNone(client._pump_state_override)

    def test_consumption_fallback_is_distinct_by_apartment_for_every_period(self):
        client = AquaNestApiClient()
        apartment_ids = tuple(f"H{number}" for number in range(101, 121))
        with patch.object(client, "_request", side_effect=requests.ConnectionError):
            for period in ("hourly", "daily", "weekly", "monthly"):
                with self.subTest(period=period):
                    apartment_series = {
                        house_id: client.get_consumption_time_series(period, house_id)
                        for house_id in apartment_ids
                    }
                    whole_building = client.get_consumption_time_series(period, "ALL")
                    apartment_totals = [
                        sum(point["litres"] for point in series)
                        for series in apartment_series.values()
                    ]
                    self.assertEqual(len(set(apartment_totals)), len(apartment_ids))
                    self.assertGreater(
                        sum(point["litres"] for point in whole_building),
                        max(apartment_totals),
                    )

    def test_resident_house_fallback_preserves_requested_apartment(self):
        client = AquaNestApiClient()
        with patch.object(client, "_request", side_effect=requests.ConnectionError):
            houses = client.get_houses(role="RESIDENT", house_id="H119")

        self.assertEqual([house["houseId"] for house in houses], ["H119"])

    def test_backend_failure_cooldown_skips_requests_then_recovers(self):
        response = Mock(status_code=200)
        response.json.return_value = {"levelPercent": 33.0}
        client = AquaNestApiClient()

        with patch(
            "dashboard.services.api_client.requests.request",
            side_effect=[requests.Timeout(), response],
        ) as request:
            with patch(
                "dashboard.services.api_client.time.monotonic",
                side_effect=[10.0, 10.0, 11.0, 16.0],
            ):
                summary, is_live = client.get_summary()
                tank_current, tank_is_live = client.get_tank_current()
                recovered_tank, recovered_is_live = client.get_tank_current()

        self.assertFalse(is_live)
        self.assertEqual(summary["tankLevelPercent"], 72.5)
        self.assertFalse(tank_is_live)
        self.assertEqual(tank_current["levelPercent"], 72.5)
        self.assertTrue(recovered_is_live)
        self.assertEqual(recovered_tank, {"levelPercent": 33.0})
        self.assertEqual(request.call_count, 2)
