"""
AquaNest IoT Telemetry Simulator (Demo & Evaluation Mode)
Generates real-time telemetry for Overhead Tank, Pump, Pressure, and 6 Apartments (H101 - H106).
Can stream to HiveMQ / local MQTT broker or directly to Spring Boot backend.
"""

import time
import json
import random
import math
import requests

try:
    import paho.mqtt.client as mqtt
    PAHO_AVAILABLE = True
except ImportError:
    PAHO_AVAILABLE = False

BACKEND_URL = "http://localhost:8080"
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

HOUSES = ["H101", "H102", "H103", "H104", "H105", "H106"]


class AquaNestSimulator:
    def __init__(self, mode="HYBRID"):
        self.mode = mode
        self.tank_level_pct = 72.0
        self.tank_capacity = 4000.0
        self.pump_status = "OFF"
        self.pressure_bar = 2.75
        self.cumulative = {h: 1200.0 + (i * 150.0) for i, h in enumerate(HOUSES)}
        self.main_cumulative = 8500.0
        self.mqtt_client = None

        if PAHO_AVAILABLE and mode in ["MQTT", "HYBRID"]:
            try:
                try:
                    self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="AquaNest_Simulator_" + str(int(time.time())))
                except AttributeError:
                    self.mqtt_client = mqtt.Client(client_id="AquaNest_Simulator_" + str(int(time.time())))
                self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
                self.mqtt_client.loop_start()
                print(f"[Simulator] Connected to MQTT broker: {MQTT_BROKER}")
            except Exception as e:
                print(f"[Simulator] MQTT connection warning: {e}. Falling back to REST.")

    def step(self):
        # 1. Calculate active consumption across 6 houses
        step_house_flow = {}
        for h in HOUSES:
            base_rate = random.uniform(0.8, 3.2)
            if h == "H104":
                # Flat 104 has persistent leak (4.5 L/min)
                base_rate += 4.5
            step_house_flow[h] = round(base_rate, 2)
            self.cumulative[h] += round(base_rate * (3.0 / 60.0), 2)

        total_house_rate = sum(step_house_flow.values())
        main_rate = total_house_rate * 1.05  # +5% nominal distribution delta
        self.main_cumulative += round(main_rate * (3.0 / 60.0), 2)

        # 2. Update tank level
        if self.pump_status == "ON":
            # Pump replenishes at 45 L/min
            net_inflow = 45.0 - total_house_rate
            delta_litres = net_inflow * (3.0 / 60.0)
            self.tank_level_pct += (delta_litres / self.tank_capacity) * 100.0
            if self.tank_level_pct >= 90.0:
                self.pump_status = "OFF"
                print(f"[Simulator] Tank full ({self.tank_level_pct:.1f}%). Pump turned OFF.")
        else:
            # Empties at current consumption
            delta_litres = total_house_rate * (3.0 / 60.0)
            self.tank_level_pct -= (delta_litres / self.tank_capacity) * 100.0
            if self.tank_level_pct <= 20.0:
                self.pump_status = "ON"
                print(f"[Simulator] Tank low ({self.tank_level_pct:.1f}%). Pump turned ON.")

        self.tank_level_pct = max(5.0, min(100.0, round(self.tank_level_pct, 1)))
        tank_litres = round((self.tank_level_pct / 100.0) * self.tank_capacity, 1)

        # 3. Pressure fluctuates around 2.75 bar
        self.pressure_bar = round(2.75 + random.uniform(-0.08, 0.08), 2)

        # 4. Dispatch Telemetry
        payload_tank = {
            "deviceId": "ESP32_SIM_001",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tankLevelPercent": self.tank_level_pct,
            "tankLitres": tank_litres,
            "pumpStatus": self.pump_status
        }

        payload_pressure = {
            "deviceId": "ESP32_SIM_001",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pressureBar": self.pressure_bar
        }

        # Send via MQTT
        if self.mqtt_client:
            self.mqtt_client.publish("aquanest/tank/readings", json.dumps(payload_tank))
            self.mqtt_client.publish("aquanest/pressure/readings", json.dumps(payload_pressure))
            for h in HOUSES:
                flow_payload = {
                    "deviceId": "ESP32_SIM_001",
                    "houseId": h,
                    "flowRate": step_house_flow[h],
                    "pulseCount": int(self.cumulative[h] * 450),
                    "cumulativeLitres": round(self.cumulative[h], 1),
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                self.mqtt_client.publish(f"aquanest/house/{h}/flow", json.dumps(flow_payload))

        print(f"[Telemetry] Tank: {self.tank_level_pct}% ({tank_litres}L) | Pump: {self.pump_status} | Pressure: {self.pressure_bar} bar | Flat Flow: {total_house_rate:.1f} L/min")


def run_simulator(iterations=10, delay_seconds=0.0):
    sim = AquaNestSimulator(mode="HYBRID")
    for _ in range(iterations):
        sim.step()
        if delay_seconds > 0:
            time.sleep(delay_seconds)


if __name__ == "__main__":
    print("Starting AquaNest Telemetry Simulator...")
    run_simulator(iterations=5, delay_seconds=0.0)
