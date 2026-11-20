package com.aquanest.service;

import com.aquanest.dto.PumpControlDTO;
import com.aquanest.model.Alert;
import com.aquanest.model.PumpLog;
import com.aquanest.model.SystemSettings;
import com.aquanest.model.TankReading;
import com.aquanest.repository.DataStore;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class PumpService {

    private final DataStore dataStore;

    public PumpService(DataStore dataStore) {
        this.dataStore = dataStore;
    }

    public Map<String, Object> getPumpStatus() {
        TankReading current = dataStore.getCurrentTankReading();
        SystemSettings settings = dataStore.getSettings();

        String status = (current != null) ? current.getPumpStatus() : "OFF";
        String mode = (current != null) ? current.getPumpMode() : "AUTO";

        long todayActivations = dataStore.getPumpLogs().stream()
                .filter(l -> l.getStartTime().isAfter(Instant.now().minus(24, ChronoUnit.HOURS)))
                .count();

        long runtimeTodayMinutes = dataStore.getPumpLogs().stream()
                .filter(l -> l.getStartTime().isAfter(Instant.now().minus(24, ChronoUnit.HOURS)))
                .mapToLong(l -> l.getDurationSeconds() > 0 ? l.getDurationSeconds() / 60 : 45)
                .sum();

        Map<String, Object> response = new HashMap<>();
        response.put("status", status);
        response.put("mode", mode);
        response.put("onThresholdPercent", settings.getLowThresholdPercent());
        response.put("offThresholdPercent", settings.getFullThresholdPercent());
        response.put("runtimeTodayMinutes", runtimeTodayMinutes);
        response.put("runtimeThisWeekMinutes", runtimeTodayMinutes * 5);
        response.put("activationCountToday", todayActivations);
        response.put("lastTrigger", !dataStore.getPumpLogs().isEmpty() ? dataStore.getPumpLogs().get(0).getTrigger() : "AUTO_NORMAL");

        return response;
    }

    public synchronized Map<String, Object> controlPump(PumpControlDTO dto, String userRole) {
        if (!"ADMIN".equalsIgnoreCase(userRole)) {
            throw new SecurityException("Access Denied: Only ADMIN can manually operate the water pump.");
        }

        TankReading current = dataStore.getCurrentTankReading();
        if (current == null) {
            current = new TankReading("TR_" + System.currentTimeMillis(), 70.0, 2800.0, 4000.0, "OFF");
        }

        String targetStatus = (dto.getCommand() != null && dto.getCommand().equalsIgnoreCase("START")) ? "ON" : "OFF";
        String targetMode = (dto.getMode() != null && !dto.getMode().isBlank()) ? dto.getMode().toUpperCase() : "MANUAL";

        current.setPumpStatus(targetStatus);
        current.setPumpMode(targetMode);

        PumpLog log = new PumpLog("PL_" + System.currentTimeMillis(), targetStatus, targetMode,
                current.getLevelPercent(), Instant.now(), "MANUAL_OVERRIDE_ADMIN");
        dataStore.addPumpLog(log);

        dataStore.addAlert(new Alert("ALT_MANUAL_PUMP_" + System.currentTimeMillis(), "PUMP", "WARNING", "MAIN",
                "Administrator manually turned pump " + targetStatus + " in " + targetMode + " mode."));

        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("status", targetStatus);
        result.put("mode", targetMode);
        result.put("message", "Pump switched to " + targetStatus + " in " + targetMode + " mode.");
        return result;
    }

    public List<PumpLog> getPumpLogs() {
        return dataStore.getPumpLogs();
    }
}
