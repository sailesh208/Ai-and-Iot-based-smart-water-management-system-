package com.aquanest.service;

import com.aquanest.model.AiAnomaly;
import com.aquanest.model.AiForecast;
import com.aquanest.model.Recommendation;
import com.aquanest.repository.DataStore;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class AiIntegrationService {

    private final DataStore dataStore;

    public AiIntegrationService(DataStore dataStore) {
        this.dataStore = dataStore;
    }

    public List<AiAnomaly> getAnomalies(String houseId) {
        if (houseId != null && !houseId.equalsIgnoreCase("ALL")) {
            return dataStore.getAnomalies().stream()
                    .filter(a -> a.getHouseId().equalsIgnoreCase(houseId))
                    .collect(Collectors.toList());
        }
        return dataStore.getAnomalies();
    }

    public List<AiForecast> getForecasts(String houseId) {
        if (houseId != null && !houseId.equalsIgnoreCase("ALL")) {
            return dataStore.getForecasts().stream()
                    .filter(f -> f.getHouseId().equalsIgnoreCase(houseId))
                    .collect(Collectors.toList());
        }
        return dataStore.getForecasts();
    }

    public List<Recommendation> getRecommendations(String target, String houseId) {
        return dataStore.getRecommendations().stream()
                .filter(r -> {
                    if ("ADMIN".equalsIgnoreCase(target)) {
                        return true; // admin sees all recommendations
                    }
                    // resident sees "ALL" or specific to their house
                    return "ALL".equalsIgnoreCase(r.getTarget()) ||
                            ("RESIDENT".equalsIgnoreCase(r.getTarget()) &&
                                    ("ALL".equalsIgnoreCase(r.getHouseId()) || r.getHouseId().equalsIgnoreCase(houseId)));
                })
                .collect(Collectors.toList());
    }

    public Map<String, Object> getAiStatusSummary() {
        long totalAnomalies = dataStore.getAnomalies().size();
        Set<String> affectedHouses = dataStore.getAnomalies().stream()
                .map(AiAnomaly::getHouseId)
                .collect(Collectors.toSet());

        Map<String, Object> summary = new HashMap<>();
        summary.put("modelName", "Isolation Forest + Ridge Time-Series Forecaster");
        summary.put("status", "ACTIVE");
        summary.put("anomalyCount", totalAnomalies);
        summary.put("affectedHousesCount", affectedHouses.size());
        summary.put("affectedHouses", affectedHouses);
        summary.put("normalHousesCount", Math.max(0, dataStore.getHouses().size() - affectedHouses.size()));
        summary.put("confidenceLevel", "94.2%");

        return summary;
    }
}
