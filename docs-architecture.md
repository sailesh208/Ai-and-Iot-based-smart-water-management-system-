# AquaNest Architecture Specification

## 1. System Overview

AquaNest is an enterprise-grade AI + IoT smart water-management system designed for multi-unit apartment complexes. It eliminates common apartment water challenges:
- Undetected overhead tank overflow and dry-running pump failures
- Silent toilet flapper leaks and concealed pipe distribution bursts
- Inequitable flat-rate water billing disputes
- Unplanned water shortages during weekend peak consumption surges

```
 ┌─────────────────────────────────────────────────────────┐
 │               IoT Telemetry & Sensing Layer             │
 │   JSN-SR04T (Overhead Tank) • YF Flow Meters (Houses)   │
 │        Piezoresistive Pressure Transducer (Line)        │
 └────────────────────────────┬────────────────────────────┘
                              │
                      [ GPIO Interrupts / ADC ]
                              │
 ┌────────────────────────────▼────────────────────────────┐
 │               Edge Processing Layer (ESP32)             │
 │    Volumetric Integration • Autonomous Hysteresis FSM   │
 │         Hardware Contactor Watchdog (45 min cut)        │
 └────────────────────────────┬────────────────────────────┘
                              │
                        [ Wi-Fi / MQTT ]
                              │
 ┌────────────────────────────▼────────────────────────────┐
 │             Central Messaging (MQTT Broker)             │
 │  Topics: aquanest/tank/*, aquanest/house/+/flow, etc.   │
 └────────────────────────────┬────────────────────────────┘
                              │
                       [ Paho MQTT Client ]
                              │
 ┌────────────────────────────▼────────────────────────────┐
 │          Java Spring Boot 3 Central Business Core       │
 │   • Consumption Aggregator (Interval/Hourly/Monthly)    │
 │   • Hysteresis State Machine (20% ON, 90% OFF)          │
 │   • Tank Seepage & Pipe Distribution Leakage Engines    │
 │   • Smart Billing Engine (Immutable Tariff Snapshots)   │
 │   • Role-Based Security Guard (Admin vs Resident)       │
 └─────────────┬─────────────────────────────┬─────────────┘
               │                             │
    [ Firebase Admin SDK ]          [ REST API JSON ]
               │                             │
 ┌─────────────▼─────────────┐ ┌─────────────▼─────────────┐
 │  Firebase Cloud Firestore │ │  Python Streamlit UI/UX   │
 │  • Users, Houses, Sensors │ │  • Dark Blue Theme        │
 │  • Telemetry, Bills, Logs │ │  • Admin / Resident Hub   │
 └─────────────┬─────────────┘ │  • 4–5 Plotly Graphs/Page │
               │               └───────────────────────────┘
               │
 ┌─────────────▼─────────────┐
 │      Python AI Engine     │
 │  • Isolation Forest (ML)  │
 │  • Ridge Demand Forecast  │
 │  • Actionable Tips Engine │
 └───────────────────────────┘
```

---

## 2. Core Subsystems

### 2.1 IoT Edge & Sensing Layer (ESP32)
- **Overhead Tank Sensor:** JSN-SR04T waterproof ultrasonic transducer mounted at the top of the 4,000 L overhead tank ($200\text{ cm}$ effective height, $20\text{ cm}$ blind-zone offset).
- **Submersible Water Pump:** Driven via an optocoupled electromagnetic contactor with snubber network and hardware safety watchdog (45-minute continuous run cut-off).
- **Water Flow Meters:** Digital pulse hall-effect flow meters with hardware interrupts calibrated at $450\text{ pulses/litre}$.
- **Distribution Pressure Sensor:** 0–5V pressure transducer scaled to 0–3.3V ADC for burst detection.

### 2.2 Messaging (MQTT)
- Uses Eclipse Paho MQTT client over port 1883.
- Topics:
  - `aquanest/tank/readings` (Tank level %, Litres, Pump State)
  - `aquanest/pump/status` & `aquanest/pump/control`
  - `aquanest/house/{houseId}/flow` (Pulse count, instantaneous flow rate, cumulative litres)
  - `aquanest/pressure/readings` (Distribution line bar)

### 2.3 Java Spring Boot Business Core
- **Consumption Engine:** Handles sensor resets, non-monotonic readings, and aggregates intervals into hourly, daily, weekly, and monthly totals.
- **Leakage Engine:**
  - *Tank Leakage:* Evaluated when pump is OFF, total house flow is zero, and tank level steadily declines.
  - *Pipe Leakage:* Evaluated when main distribution flow exceeds sum of active house flows by more than tolerance ($5\%$), or line pressure drops below $1.8\text{ bar}$.
- **Smart Billing Engine:** Applies transparent formula $\text{Final Bill} = (\text{Monthly Litres} \times \text{Tariff}) + \text{Fixed Maintenance Charge}$. Tariffs are captured immutably at generation time.
- **Security Guard:** Strictly limits residents to their own apartment's telemetry and invoices.

### 2.4 Machine Learning Services
- **Anomaly Detection:** Scikit-Learn `IsolationForest` (100 estimators, 3% contamination) combined with rule-based heuristics for nocturnal continuous leaks.
- **Demand Forecasting:** Time-series Ridge regression providing 7-day demand projections with 95% confidence intervals and morning peak surge windows.
