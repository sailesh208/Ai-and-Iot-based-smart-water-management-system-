#ifndef AQUANEST_RELAY_CONTROLLER_H
#define AQUANEST_RELAY_CONTROLLER_H

#include <Arduino.h>
#include "src/config.h"

class PumpRelayController {
private:
    bool _pumpOn;
    unsigned long _pumpStartTime;

public:
    void begin() {
        pinMode(PIN_PUMP_RELAY, OUTPUT);
        digitalWrite(PIN_PUMP_RELAY, RELAY_INACTIVE_LEVEL);
        _pumpOn = false;
        _pumpStartTime = 0;
    }

    void setPumpState(bool turnOn) {
        if (turnOn && !_pumpOn) {
            digitalWrite(PIN_PUMP_RELAY, RELAY_ACTIVE_LEVEL);
            _pumpOn = true;
            _pumpStartTime = millis();
        } else if (!turnOn && _pumpOn) {
            digitalWrite(PIN_PUMP_RELAY, RELAY_INACTIVE_LEVEL);
            _pumpOn = false;
            _pumpStartTime = 0;
        }
    }

    void checkSafetyWatchdog() {
        // Enforce maximum continuous runtime safety watchdog
        if (_pumpOn && (millis() - _pumpStartTime > PUMP_MAX_RUN_TIME_MS)) {
            setPumpState(false);
            // Alert buzzer
            pinMode(PIN_BUZZER, OUTPUT);
            digitalWrite(PIN_BUZZER, HIGH);
        }
    }

    bool isPumpOn() const { return _pumpOn; }
};

#endif // AQUANEST_RELAY_CONTROLLER_H
