package com.aquanest.service;

import com.aquanest.model.Alert;
import com.aquanest.repository.DataStore;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class AlertService {

    private final DataStore dataStore;

    public AlertService(DataStore dataStore) {
        this.dataStore = dataStore;
    }

    public List<Alert> getAllAlerts() {
        return dataStore.getAlerts();
    }

    public List<Alert> getAlertsForHouse(String houseId) {
        return dataStore.getAlerts().stream()
                .filter(a -> "ALL".equalsIgnoreCase(a.getHouseId()) || a.getHouseId().equalsIgnoreCase(houseId))
                .collect(Collectors.toList());
    }

    public synchronized Alert markAsRead(String alertId) {
        Alert alert = findAlert(alertId);
        if (alert != null && "NEW".equalsIgnoreCase(alert.getStatus())) {
            alert.setStatus("ACKNOWLEDGED");
        }
        return alert;
    }

    public synchronized Alert resolveAlert(String alertId) {
        Alert alert = findAlert(alertId);
        if (alert != null) {
            alert.setStatus("RESOLVED");
        }
        return alert;
    }

    private Alert findAlert(String alertId) {
        return dataStore.getAlerts().stream()
                .filter(a -> a.getId().equalsIgnoreCase(alertId))
                .findFirst()
                .orElse(null);
    }
}
