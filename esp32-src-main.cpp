/**
 * AquaNest Smart Apartment Water Management System
 * ESP32 Controller Firmware (Arduino Framework)
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include "config.h"
#include "../sensors/ultrasonic.h"
#include "../sensors/flow_meter.h"
#include "../pump/relay_controller.h"

// Global instances
WiFiClient espClient;
PubSubClient mqttClient(espClient);
UltrasonicSensor ultrasonic;
PumpRelayController pumpController;

// Flow meter instances
FlowMeter flowMain(PIN_FLOW_MAIN);
FlowMeter flowH101(PIN_FLOW_H101);
FlowMeter flowH102(PIN_FLOW_H102);
FlowMeter flowH103(PIN_FLOW_H103);

// Interrupt Service Routines
void IRAM_ATTR isrMain() { flowMain.countPulse(); }
void IRAM_ATTR isrH101() { flowH101.countPulse(); }
void IRAM_ATTR isrH102() { flowH102.countPulse(); }
void IRAM_ATTR isrH103() { flowH103.countPulse(); }

unsigned long lastTelemetryPublish = 0;
const unsigned long TELEMETRY_INTERVAL = 3000; // 3 seconds

void connectWiFi() {
    Serial.print("Connecting to Wi-Fi: ");
    Serial.println(WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWi-Fi Connected. IP: " + WiFi.localIP().toString());
    } else {
        Serial.println("\nWi-Fi timeout. Continuing in offline standalone mode.");
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    char message[length + 1];
    memcpy(message, payload, length);
    message[length] = '\0';
    Serial.printf("MQTT Incoming [%s]: %s\n", topic, message);

    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, message);
    if (!error) {
        if (strcmp(topic, TOPIC_PUMP_CONTROL) == 0) {
            const char* command = doc["command"];
            if (command && strcmp(command, "START") == 0) {
                pumpController.setPumpState(true);
                Serial.println("Pump manually started via MQTT");
            } else if (command && strcmp(command, "STOP") == 0) {
                pumpController.setPumpState(false);
                Serial.println("Pump manually stopped via MQTT");
            }
        }
    }
}

void connectMQTT() {
    if (WiFi.status() != WL_CONNECTED) return;
    if (!mqttClient.connected()) {
        Serial.print("Connecting to MQTT broker...");
        if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASS)) {
            Serial.println("Connected!");
            mqttClient.subscribe(TOPIC_PUMP_CONTROL);
        } else {
            Serial.printf("Failed, rc=%d. Will retry.\n", mqttClient.state());
        }
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("\n--- AquaNest ESP32 Firmware Starting ---");

    ultrasonic.begin();
    pumpController.begin();

    flowMain.begin(isrMain);
    flowH101.begin(isrH101);
    flowH102.begin(isrH102);
    flowH103.begin(isrH103);

    connectWiFi();
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    mqttClient.setCallback(mqttCallback);
}

void loop() {
    if (!mqttClient.connected()) {
        connectMQTT();
    }
    mqttClient.loop();

    // Update flow meters
    flowMain.update();
    flowH101.update();
    flowH102.update();
    flowH103.update();

    // Check safety watchdog
    pumpController.checkSafetyWatchdog();

    unsigned long now = millis();
    if (now - lastTelemetryPublish >= TELEMETRY_INTERVAL) {
        lastTelemetryPublish = now;

        float distanceCm = ultrasonic.measureDistanceCm();
        float levelPercent = ultrasonic.calculateLevelPercent(distanceCm);
        float litres = ultrasonic.calculateWaterLitres(levelPercent);
        bool pumpOn = pumpController.isPumpOn();

        // Automatic hysteresis logic on hardware
        if (levelPercent > 0) {
            if (levelPercent <= 20.0f && !pumpOn) {
                pumpController.setPumpState(true);
            } else if (levelPercent >= 90.0f && pumpOn) {
                pumpController.setPumpState(false);
            }
        }

        // Publish Tank Telemetry
        StaticJsonDocument<256> tankDoc;
        tankDoc["deviceId"] = MQTT_CLIENT_ID;
        tankDoc["tankLevelPercent"] = round(levelPercent * 10.0f) / 10.0f;
        tankDoc["tankLitres"] = round(litres);
        tankDoc["pumpStatus"] = pumpController.isPumpOn() ? "ON" : "OFF";
        char tankBuf[256];
        serializeJson(tankDoc, tankBuf);
        mqttClient.publish(TOPIC_TANK_READINGS, tankBuf);

        // Publish House 101 Flow
        StaticJsonDocument<256> flowDoc;
        flowDoc["deviceId"] = MQTT_CLIENT_ID;
        flowDoc["houseId"] = "H101";
        flowDoc["flowRate"] = flowH101.getFlowRateLpm();
        flowDoc["cumulativeLitres"] = flowH101.getCumulativeLitres();
        char flowBuf[256];
        serializeJson(flowDoc, flowBuf);
        mqttClient.publish("aquanest/house/H101/flow", flowBuf);
    }
}
