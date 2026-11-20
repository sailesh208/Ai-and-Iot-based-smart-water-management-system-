package com.aquanest.controller;

import com.aquanest.dto.ConsumptionDTO;
import com.aquanest.security.SecurityGuard;
import com.aquanest.service.ConsumptionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/consumption")
@CrossOrigin(origins = "*")
public class ConsumptionController {

    private final ConsumptionService consumptionService;
    private final SecurityGuard securityGuard;

    public ConsumptionController(ConsumptionService consumptionService, SecurityGuard securityGuard) {
        this.consumptionService = consumptionService;
        this.securityGuard = securityGuard;
    }

    @GetMapping("/summary")
    public ResponseEntity<ConsumptionDTO.Summary> getSummary() {
        return ResponseEntity.ok(consumptionService.getConsumptionSummary());
    }

    @GetMapping("/hourly")
    public ResponseEntity<List<ConsumptionDTO.TimeSeriesPoint>> getHourly(
            @RequestParam(name = "houseId", required = false, defaultValue = "ALL") String houseId,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        if ("RESIDENT".equalsIgnoreCase(role)) {
            houseId = userHouseId;
        }
        return ResponseEntity.ok(consumptionService.getHourlyConsumption(houseId));
    }

    @GetMapping("/daily")
    public ResponseEntity<List<ConsumptionDTO.TimeSeriesPoint>> getDaily(
            @RequestParam(name = "days", defaultValue = "14") int days,
            @RequestParam(name = "houseId", required = false, defaultValue = "ALL") String houseId,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        if ("RESIDENT".equalsIgnoreCase(role)) {
            houseId = userHouseId;
        }
        return ResponseEntity.ok(consumptionService.getDailyConsumption(days, houseId));
    }

    @GetMapping("/weekly")
    public ResponseEntity<List<ConsumptionDTO.TimeSeriesPoint>> getWeekly(
            @RequestParam(name = "houseId", required = false, defaultValue = "ALL") String houseId,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        if ("RESIDENT".equalsIgnoreCase(role)) {
            houseId = userHouseId;
        }
        return ResponseEntity.ok(consumptionService.getWeeklyConsumption(houseId));
    }

    @GetMapping("/monthly")
    public ResponseEntity<List<ConsumptionDTO.TimeSeriesPoint>> getMonthly(
            @RequestParam(name = "houseId", required = false, defaultValue = "ALL") String houseId,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        if ("RESIDENT".equalsIgnoreCase(role)) {
            houseId = userHouseId;
        }
        return ResponseEntity.ok(consumptionService.getMonthlyConsumption(houseId));
    }

    @GetMapping("/house/{houseId}")
    public ResponseEntity<Map<String, Object>> getHouseDetails(
            @PathVariable(name = "houseId") String houseId,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        securityGuard.validateHouseAccess(role, userHouseId, houseId);
        return ResponseEntity.ok(consumptionService.getHouseConsumptionDetails(houseId));
    }
}
