#ifndef AQUANEST_FLOW_METER_H
#define AQUANEST_FLOW_METER_H

#include <Arduino.h>
#include "src/config.h"

class FlowMeter {
private:
    uint8_t _pin;
    float _calibrationFactor;
    volatile unsigned long _pulseCount;
    unsigned long _lastCalcTime;
    float _cumulativeLitres;
    float _flowRateLpm;

public:
    FlowMeter(uint8_t pin, float calibrationFactor = CALIBRATION_FACTOR)
        : _pin(pin), _calibrationFactor(calibrationFactor), _pulseCount(0),
          _lastCalcTime(0), _cumulativeLitres(0.0f), _flowRateLpm(0.0f) {}

    void IRAM_ATTR countPulse() {
        _pulseCount++;
    }

    void begin(void (*isr)()) {
        pinMode(_pin, INPUT_PULLUP);
        attachInterrupt(digitalPinToInterrupt(_pin), isr, RISING);
        _lastCalcTime = millis();
    }

    void update() {
        unsigned long now = millis();
        unsigned long elapsedMs = now - _lastCalcTime;

        if (elapsedMs >= 1000) { // Update every 1 second
            noInterrupts();
            unsigned long pulses = _pulseCount;
            _pulseCount = 0;
            interrupts();

            // Frequency (Hz) = pulses / (elapsedMs / 1000)
            float freqHz = (float)pulses / (elapsedMs / 1000.0f);

            // Flow rate in L/min = (Freq / CalibrationFactor) * 60
            _flowRateLpm = (freqHz / _calibrationFactor) * 60.0f;

            // Volume passed in interval (L) = pulses / CalibrationFactor
            float intervalLitres = (float)pulses / _calibrationFactor;
            _cumulativeLitres += intervalLitres;

            _lastCalcTime = now;
        }
    }

    float getFlowRateLpm() const { return _flowRateLpm; }
    float getCumulativeLitres() const { return _cumulativeLitres; }
};

#endif // AQUANEST_FLOW_METER_H
