#ifndef AQUANEST_CONFIG_H
#define AQUANEST_CONFIG_H

// ============================================================
// AQUANEST ESP32 HARDWARE CONFIGURATION & PINOUT
// ============================================================

// Wi-Fi Credentials
#define WIFI_SSID "AquaNest_AP"
#define WIFI_PASSWORD "AquaNest@Secure2026"

// MQTT Configuration
#define MQTT_BROKER "broker.hivemq.com"
#define MQTT_PORT 1883
#define MQTT_CLIENT_ID "ESP32_AQUANEST_001"
#define MQTT_USER ""
#define MQTT_PASS ""

// MQTT Topics
#define TOPIC_TANK_READINGS "aquanest/tank/readings"
#define TOPIC_PUMP_STATUS "aquanest/pump/status"
#define TOPIC_PUMP_CONTROL "aquanest/pump/control"
#define TOPIC_PRESSURE_READINGS "aquanest/pressure/readings"
#define TOPIC_ALERTS "aquanest/alerts"

// Hardware GPIO Pin Definitions
#define PIN_TRIG 5           // JSN-SR04T Ultrasonic Trigger
#define PIN_ECHO 18          // JSN-SR04T Ultrasonic Echo
#define PIN_PUMP_RELAY 23    // Optocoupled Pump Relay Control
#define PIN_BUZZER 19        // High/Low Level Alert Buzzer
#define PIN_PRESSURE_ADC 34  // Pressure Sensor (0-5V scaled to 0-3.3V ADC)

// Pulse Flow Meter Pins (Interrupt-capable GPIOs)
#define PIN_FLOW_MAIN 21     // Main Distribution Flow Meter (YF-B5 / YF-S201)
#define PIN_FLOW_H101 22     // Flat 101 Flow Meter
#define PIN_FLOW_H102 25     // Flat 102 Flow Meter
#define PIN_FLOW_H103 26     // Flat 103 Flow Meter
#define PIN_FLOW_H104 27     // Flat 104 Flow Meter
#define PIN_FLOW_H105 32     // Flat 105 Flow Meter
#define PIN_FLOW_H106 33     // Flat 106 Flow Meter

// Calibration Factors (Pulses per Litre)
#define CALIBRATION_FACTOR 450.0f

// Physical Tank Geometry (in centimeters)
#define TANK_TOTAL_HEIGHT_CM 200.0f
#define TANK_SENSOR_OFFSET_CM 20.0f
#define TANK_CAPACITY_LITRES 4000.0f

// Electrical Safety Constraints
// IMPORTANT: NEVER drive an AC pump directly from GPIO!
// Active LOW relay with optical isolation
#define RELAY_ACTIVE_LEVEL LOW
#define RELAY_INACTIVE_LEVEL HIGH
#define PUMP_MAX_RUN_TIME_MS (45 * 60 * 1000L) // 45-minute continuous run watchdog

#endif // AQUANEST_CONFIG_H
