package com.aquanest.controller;

import com.aquanest.model.AiAnomaly;
import com.aquanest.model.AiForecast;
import com.aquanest.model.Recommendation;
import com.aquanest.service.AiIntegrationService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/ai")
@CrossOrigin(origins = "*")
public class AiController {

    private final AiIntegrationService aiService;

    public AiController(AiIntegrationService aiService) {
        this.aiService = aiService;
    }

    @GetMapping("/anomalies")
    public ResponseEntity<List<AiAnomaly>> getAnomalies(
            @RequestParam(name = "houseId", required = false) String houseId,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        if ("RESIDENT".equalsIgnoreCase(role)) {
            houseId = userHouseId;
        }
        return ResponseEntity.ok(aiService.getAnomalies(houseId));
    }

    @GetMapping("/forecast")
    public ResponseEntity<List<AiForecast>> getForecast(
            @RequestParam(name = "houseId", required = false, defaultValue = "ALL") String houseId) {
        return ResponseEntity.ok(aiService.getForecasts(houseId));
    }

    @GetMapping("/recommendations")
    public ResponseEntity<List<Recommendation>> getRecommendations(
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        return ResponseEntity.ok(aiService.getRecommendations(role, userHouseId));
    }

    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getAiStatus() {
        return ResponseEntity.ok(aiService.getAiStatusSummary());
    }
}
