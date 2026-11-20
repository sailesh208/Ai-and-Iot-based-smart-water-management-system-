package com.aquanest.service;

import com.aquanest.model.Alert;
import com.aquanest.model.PumpLog;
import com.aquanest.model.SystemSettings;
import com.aquanest.model.TankReading;
import com.aquanest.repository.DataStore;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.*;

@Service
public class TankService {

    private final DataStore dataStore;

    public TankService(DataStore dataStore) {
        this.dataStore = dataStore;
    }

    public TankReading getCurrentTankReading() {
        return dataStore.getCurrentTankReading();
    }

    public List<TankReading> getTankHistory() {
        return dataStore.getTankReadings();
    }

    /**
     * Process new tank distance or level measurement from ESP32 / JSN-SR04T.
     * Implements automatic pump control hysteresis.
     */
    public synchronized TankReading processTankReading(double levelPercent, String sensorId) {
        SystemSettings settings = dataStore.getSettings();
        double capacity = settings.getTankCapacityLitres();

        // Bound percent between 0 and 100
        double boundedPercent = Math.max(0.0, Math.min(100.0, Math.round(levelPercent * 10.0) / 10.0));
        double waterLitres = Math.round((boundedPercent / 100.0) * capacity * 10.0) / 10.0;

        TankReading previous = dataStore.getCurrentTankReading();
        String pumpStatus = (previous != null) ? previous.getPumpStatus() : "OFF";
        String pumpMode = (previous != null) ? previous.getPumpMode() : "AUTO";

        double lowThreshold = settings.getLowThresholdPercent();
        double fullThreshold = settings.getFullThresholdPercent();

        // Automatic Hysteresis Pump Logic
        if ("AUTO".equalsIgnoreCase(pumpMode)) {
            if (boundedPercent <= lowThreshold && "OFF".equalsIgnoreCase(pumpStatus)) {
                pumpStatus = "ON";
                recordPumpEvent("ON", "AUTO", boundedPercent, "LOW_LEVEL_AUTO");
                dataStore.addAlert(new Alert("ALT_PUMP_ON_" + System.currentTimeMillis(), "LOW_TANK", "WARNING", "MAIN",
                        "Overhead tank low (" + boundedPercent + "% <= " + lowThreshold + "%). Pump automatically activated."));
            } else if (boundedPercent >= fullThreshold && "ON".equalsIgnoreCase(pumpStatus)) {
                pumpStatus = "OFF";
                recordPumpEvent("OFF", "AUTO", boundedPercent, "FULL_LEVEL_AUTO");
                dataStore.addAlert(new Alert("ALT_PUMP_OFF_" + System.currentTimeMillis(), "FULL_TANK", "INFO", "MAIN",
                        "Overhead tank full (" + boundedPercent + "% >= " + fullThreshold + "%). Pump automatically stopped."));
            }
        }

        // Fill and Empty Rates estimation
        double fillRate = 0.0;
        double emptyRate = 0.0;
        double timeToFull = 0.0;
        double timeToEmpty = 0.0;

        if (previous != null && previous.getWaterLitres() > 0) {
            double deltaLitres = waterLitres - previous.getWaterLitres();
            if (deltaLitres > 0) {
                fillRate = Math.round(deltaLitres * 2.0 * 10.0) / 10.0; // normalised
                double litresNeeded = Math.max(0.0, (fullThreshold / 100.0 * capacity) - waterLitres);
                timeToFull = (fillRate > 0) ? Math.round(litresNeeded / fillRate) : 0.0;
            } else if (deltaLitres < 0) {
                emptyRate = Math.round(Math.abs(deltaLitres) * 2.0 * 10.0) / 10.0;
                double litresAvailable = Math.max(0.0, waterLitres - (lowThreshold / 100.0 * capacity));
                timeToEmpty = (emptyRate > 0) ? Math.round(litresAvailable / emptyRate) : 0.0;
            }
        }

        TankReading reading = new TankReading("TR_" + System.currentTimeMillis(), boundedPercent, waterLitres, capacity, pumpStatus);
        reading.setPumpMode(pumpMode);
        reading.setSensorId(sensorId);
        reading.setFillRateLpm(fillRate);
        reading.setEmptyRateLpm(emptyRate);
        reading.setEstimatedTimeToFullMinutes(timeToFull);
        reading.setEstimatedTimeToEmptyMinutes(timeToEmpty);

        dataStore.setCurrentTankReading(reading);
        return reading;
    }

    private void recordPumpEvent(String status, String mode, double tankLevel, String trigger) {
        PumpLog log = new PumpLog("PL_" + System.currentTimeMillis(), status, mode, tankLevel, Instant.now(), trigger);
        dataStore.addPumpLog(log);
    }

    public Map<String, Object> getTankStatistics() {
        TankReading current = dataStore.getCurrentTankReading();
        SystemSettings settings = dataStore.getSettings();

        Map<String, Object> stats = new HashMap<>();
        stats.put("currentLevelPercent", current != null ? current.getLevelPercent() : 0.0);
        stats.put("currentLitres", current != null ? current.getWaterLitres() : 0.0);
        stats.put("capacityLitres", settings.getTankCapacityLitres());
        stats.put("lowThresholdPercent", settings.getLowThresholdPercent());
        stats.put("fullThresholdPercent", settings.getFullThresholdPercent());
        stats.put("pumpStatus", current != null ? current.getPumpStatus() : "OFF");
        stats.put("pumpMode", current != null ? current.getPumpMode() : "AUTO");
        stats.put("estimatedTimeToFullMinutes", current != null ? current.getEstimatedTimeToFullMinutes() : 0.0);
        stats.put("estimatedTimeToEmptyMinutes", current != null ? current.getEstimatedTimeToEmptyMinutes() : 0.0);
        stats.put("tankStatus", determineTankStatus(current != null ? current.getLevelPercent() : 0.0, settings));

        return stats;
    }

    private String determineTankStatus(double level, SystemSettings settings) {
        if (level <= settings.getLowThresholdPercent()) return "LOW";
        if (level >= settings.getFullThresholdPercent()) return "FULL";
        if (level < 35.0) return "RESERVE";
        return "OPTIMAL";
    }
}
