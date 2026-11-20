#ifndef AQUANEST_ULTRASONIC_H
#define AQUANEST_ULTRASONIC_H

#include <Arduino.h>
#include "src/config.h"

class UltrasonicSensor {
public:
    void begin() {
        pinMode(PIN_TRIG, OUTPUT);
        pinMode(PIN_ECHO, INPUT);
        digitalWrite(PIN_TRIG, LOW);
    }

    float measureDistanceCm() {
        // Trigger 10 microsecond pulse
        digitalWrite(PIN_TRIG, LOW);
        delayMicroseconds(2);
        digitalWrite(PIN_TRIG, HIGH);
        delayMicroseconds(10);
        digitalWrite(PIN_TRIG, LOW);

        // Read echo pulse duration (timeout 30ms ~ 5 meters)
        long duration = pulseIn(PIN_ECHO, HIGH, 30000);
        if (duration <= 0) {
            return -1.0f; // Sensor fault or out of range
        }

        // Speed of sound: 343 m/s = 0.0343 cm/us
        float distance = (duration * 0.0343f) / 2.0f;
        return distance;
    }

    float calculateLevelPercent(float distanceCm) {
        if (distanceCm < 0) return -1.0f;

        // Effective water depth = total height - (measured distance - sensor offset)
        float waterHeightCm = TANK_TOTAL_HEIGHT_CM - (distanceCm - TANK_SENSOR_OFFSET_CM);
        if (waterHeightCm < 0) waterHeightCm = 0;
        if (waterHeightCm > TANK_TOTAL_HEIGHT_CM) waterHeightCm = TANK_TOTAL_HEIGHT_CM;

        return (waterHeightCm / TANK_TOTAL_HEIGHT_CM) * 100.0f;
    }

    float calculateWaterLitres(float levelPercent) {
        if (levelPercent < 0) return 0.0f;
        return (levelPercent / 100.0f) * TANK_CAPACITY_LITRES;
    }
};

#endif // AQUANEST_ULTRASONIC_H
