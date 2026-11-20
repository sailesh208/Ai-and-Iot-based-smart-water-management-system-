# AquaNest MQTT Messaging Specification

## Broker Overview
- Default Broker: `tcp://broker.hivemq.com:1883` (configurable via `MQTT_BROKER`)
- Protocol: MQTT v3.1.1
- QoS Level: 1 (At least once delivery)
- Root Topic Namespace: `aquanest/#`

---

## Topic Taxonomy & Schemas

### 1. Overhead Tank Telemetry
- **Topic:** `aquanest/tank/readings`
- **Publish Frequency:** Every 3–5 seconds
- **Payload Schema:**
```json
{
  "deviceId": "ESP32_001",
  "timestamp": "2026-09-18T08:30:00Z",
  "tankLevelPercent": 72.5,
  "tankLitres": 2900.0,
  "pumpStatus": "OFF"
}
```

### 2. Apartment Flow Meter Reading
- **Topic:** `aquanest/house/{houseId}/flow` (e.g. `aquanest/house/H101/flow`)
- **Publish Frequency:** Every 3 seconds during active flow; every 30 seconds when idle
- **Payload Schema:**
```json
{
  "deviceId": "ESP32_001",
  "houseId": "H101",
  "flowRate": 2.4,
  "pulseCount": 1080,
  "cumulativeLitres": 1250.5,
  "timestamp": "2026-09-18T08:30:00Z"
}
```

### 3. Distribution Pipe Pressure
- **Topic:** `aquanest/pressure/readings`
- **Payload Schema:**
```json
{
  "deviceId": "ESP32_001",
  "timestamp": "2026-09-18T08:30:00Z",
  "pressureBar": 2.74
}
```

### 4. Pump Remote Control
- **Topic:** `aquanest/pump/control`
- **Direction:** Java Backend / Dashboard ➔ ESP32
- **Payload Schema:**
```json
{
  "command": "START",
  "mode": "MANUAL",
  "timestamp": "2026-09-18T08:30:00Z"
}
```
