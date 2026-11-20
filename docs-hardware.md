# AquaNest Hardware Connection & Electrical Safety Guide

## 1. Electrical Safety Rules (CRITICAL)

> [!CAUTION]
> **NEVER drive an AC motor/pump directly from an ESP32 GPIO pin.**
> 1. An ESP32 GPIO can supply only 3.3V at ~12mA, whereas AC pumps draw high inrush starting currents (up to 15A inductive load).
> 2. Always use an **optocoupled relay board** (or 230V AC contactor) with optical isolation to protect the microcontroller from back-EMF spikes.
> 3. Connect a flyback diode / RC snubber across the inductive coil to suppress voltage transients.
> 4. The firmware implements a 45-minute continuous run safety watchdog to shut off the relay if a float switch fails.

---

## 2. Hardware Component List
| Component | Function | Interface |
|---|---|---|
| **ESP32 NodeMCU-32S** | Central IoT edge microcontroller | Wi-Fi 802.11 b/g/n, 2.4GHz |
| **JSN-SR04T** | Waterproof ultrasonic water level sensor | Trigger (GPIO 5), Echo (GPIO 18) |
| **YF-B5 / YF-S201** | Hall-effect pulse flow meters | Digital Interrupt pins (GPIO 21, 22, 25, etc.) |
| **Piezoresistive Transducer** | Pipe line pressure sensor (0–10 bar) | Analog ADC (GPIO 34 with resistor divider) |
| **Optocoupled Relay Module** | Pump motor contactor actuation | Active LOW (GPIO 23) |
| **Active Piezo Buzzer** | Local threshold alert alarm | Digital (GPIO 19) |

---

## 3. Wiring Pinout Diagram

```
ESP32 Pinout:
  [GPIO 5]  ───> JSN-SR04T Trig
  [GPIO 18] <─── JSN-SR04T Echo
  [GPIO 21] <─── Main Distribution Flow Meter (Pulse Interrupt)
  [GPIO 22] <─── House 101 Flow Meter (Pulse Interrupt)
  [GPIO 25] <─── House 102 Flow Meter (Pulse Interrupt)
  [GPIO 26] <─── House 103 Flow Meter (Pulse Interrupt)
  [GPIO 27] <─── House 104 Flow Meter (Pulse Interrupt)
  [GPIO 34] <─── Line Pressure Transducer (ADC 0-3.3V)
  [GPIO 23] ───> Optocoupled Relay IN1 (Active LOW)
  [GPIO 19] ───> Alert Buzzer
  [VIN]     ───> External 5V 2A Regulated Power Supply
  [GND]     ───> Common Ground
```

---

## 4. Flow Meter Calibration
- Pulse formula:
  $$Q (\text{L/min}) = \frac{f (\text{Hz})}{K}$$
  where $K = 7.5$ for YF-S201 ($450\text{ pulses per litre}$).
- Accumulation:
  $$\text{Interval Litres} = \frac{\text{Pulses Recorded}}{450.0}$$
