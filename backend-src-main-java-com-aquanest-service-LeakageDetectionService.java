package com.aquanest.service;

import com.aquanest.model.*;
import com.aquanest.repository.DataStore;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class LeakageDetectionService {

    private final DataStore dataStore;

    public LeakageDetectionService(DataStore dataStore) {
        this.dataStore = dataStore;
    }

    public List<LeakageAlert> getAllLeakageAlerts() {
        return dataStore.getLeakageAlerts();
    }

    public List<LeakageAlert> getTankLeakageAlerts() {
        return dataStore.getLeakageAlerts().stream()
                .filter(a -> "TANK_LEAKAGE".equalsIgnoreCase(a.getType()))
                .collect(Collectors.toList());
    }

    public List<LeakageAlert> getPipeLeakageAlerts() {
        return dataStore.getLeakageAlerts().stream()
                .filter(a -> "PIPE_LEAKAGE".equalsIgnoreCase(a.getType()))
                .collect(Collectors.toList());
    }

    /**
     * Evaluates live telemetry for possible tank leakage.
     * Condition: Pump OFF && House outlet flow <= threshold && tank level drops continuously.
     */
    public synchronized Optional<LeakageAlert> evaluateTankLeakage(double levelBefore, double levelAfter, double totalHouseFlowLpm, long durationMinutes) {
        TankReading reading = dataStore.getCurrentTankReading();
        String pumpStatus = (reading != null) ? reading.getPumpStatus() : "OFF";

        // Tank leak check: Pump is OFF, house consumption is virtually zero, but level dropped
        if ("OFF".equalsIgnoreCase(pumpStatus) && totalHouseFlowLpm < 0.5 && (levelBefore - levelAfter) > 1.5) {
            double capacity = dataStore.getSettings().getTankCapacityLitres();
            double lossLitres = ((levelBefore - levelAfter) / 100.0) * capacity;

            String evidence = String.format("Pump OFF and sum of house flow was %.1f L/min, yet tank level dropped from %.1f%% to %.1f%% over %d minutes.",
                    totalHouseFlowLpm, levelBefore, levelAfter, durationMinutes);

            LeakageAlert alert = new LeakageAlert(
                    "LKG_TANK_" + System.currentTimeMillis(),
                    "TANK_LEAKAGE",
                    "MAIN",
                    "Overhead Storage Tank",
                    Math.round(lossLitres * 10.0) / 10.0,
                    (lossLitres > 200.0) ? "CRITICAL" : "POSSIBLE_LEAK",
                    evidence,
                    dataStore.getCurrentPressureBar(),
                    0.0
            );
            alert.setDurationMinutes(durationMinutes);
            dataStore.addLeakageAlert(alert);

            dataStore.addAlert(new Alert("ALT_TL_" + System.currentTimeMillis(), "TANK_LEAKAGE",
                    alert.getSeverity(), "MAIN", "Possible tank leakage detected: " + Math.round(lossLitres) + " L unexplained loss."));

            return Optional.of(alert);
        }
        return Optional.empty();
    }

    /**
     * Evaluates distribution pipe leakage.
     * Condition: Main flow meter significantly exceeds sum of individual house flow meters OR pressure drops below threshold.
     */
    public synchronized Optional<LeakageAlert> evaluatePipeLeakage(double mainFlowLpm, double sumHouseFlowLpm, double pressureBar) {
        SystemSettings settings = dataStore.getSettings();
        double mismatch = mainFlowLpm - sumHouseFlowLpm;
        double mismatchPercent = (mainFlowLpm > 0) ? (mismatch / mainFlowLpm) * 100.0 : 0.0;
        dataStore.setCurrentPressureBar(pressureBar);

        boolean flowMismatchSevere = mismatchPercent > (settings.getLeakageTolerancePercent() * 2.5) && mismatch > 2.0;
        boolean pressureCritical = pressureBar < settings.getPressureThresholdBar();

        if (flowMismatchSevere || pressureCritical) {
            String severity = (pressureCritical && flowMismatchSevere) ? "CRITICAL" : "POSSIBLE_LEAK";
            double estimatedLoss = Math.round(mismatch * 60.0 * 10.0) / 10.0; // loss per hour

            String evidence = String.format("Main distribution flow (%.1f L/min) exceeded total apartment flow (%.1f L/min) by %.1f%%. Line pressure: %.2f bar (Threshold: %.2f bar).",
                    mainFlowLpm, sumHouseFlowLpm, mismatchPercent, pressureBar, settings.getPressureThresholdBar());

            LeakageAlert alert = new LeakageAlert(
                    "LKG_PIPE_" + System.currentTimeMillis(),
                    "PIPE_LEAKAGE",
                    "DISTRIBUTION",
                    "Main Apartment Distribution Riser",
                    estimatedLoss,
                    severity,
                    evidence,
                    pressureBar,
                    Math.round(mismatch * 10.0) / 10.0
            );
            dataStore.addLeakageAlert(alert);

            dataStore.addAlert(new Alert("ALT_PL_" + System.currentTimeMillis(), "PIPE_LEAKAGE",
                    severity, "DISTRIBUTION", "Possible pipe leakage detected: " + Math.round(mismatch) + " L/min flow mismatch."));

            return Optional.of(alert);
        }
        return Optional.empty();
    }

    public Map<String, Object> getLeakageStatistics() {
        long activeCount = dataStore.getLeakageAlerts().stream()
                .filter(a -> !"RESOLVED".equalsIgnoreCase(a.getStatus()))
                .count();

        double totalLossLitres = dataStore.getLeakageAlerts().stream()
                .filter(a -> !"RESOLVED".equalsIgnoreCase(a.getStatus()))
                .mapToDouble(LeakageAlert::getEstimatedLossLitres)
                .sum();

        Map<String, Object> stats = new HashMap<>();
        stats.put("activeLeaksCount", activeCount);
        stats.put("totalEstimatedLossLitres", Math.round(totalLossLitres * 10.0) / 10.0);
        stats.put("currentPressureBar", dataStore.getCurrentPressureBar());
        stats.put("nominalPressureBar", 2.8);
        stats.put("status", activeCount == 0 ? "NORMAL" : (activeCount > 1 ? "CRITICAL" : "WARNING"));
        stats.put("latestTankLeakage", getTankLeakageAlerts().isEmpty() ? null : getTankLeakageAlerts().get(0));
        stats.put("latestPipeLeakage", getPipeLeakageAlerts().isEmpty() ? null : getPipeLeakageAlerts().get(0));

        return stats;
    }
}
