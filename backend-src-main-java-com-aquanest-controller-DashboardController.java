package com.aquanest.controller;

import com.aquanest.dto.ConsumptionDTO;
import com.aquanest.dto.DashboardSummaryDTO;
import com.aquanest.model.Alert;
import com.aquanest.model.TankReading;
import com.aquanest.repository.DataStore;
import com.aquanest.service.ConsumptionService;
import com.aquanest.service.TankService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/dashboard")
@CrossOrigin(origins = "*")
public class DashboardController {

    private final DataStore dataStore;
    private final TankService tankService;
    private final ConsumptionService consumptionService;

    public DashboardController(DataStore dataStore, TankService tankService, ConsumptionService consumptionService) {
        this.dataStore = dataStore;
        this.tankService = tankService;
        this.consumptionService = consumptionService;
    }

    @GetMapping("/summary")
    public ResponseEntity<DashboardSummaryDTO> getDashboardSummary() {
        TankReading tank = tankService.getCurrentTankReading();
        ConsumptionDTO.Summary consumption = consumptionService.getConsumptionSummary();

        long activeAlerts = dataStore.getAlerts().stream()
                .filter(a -> !"RESOLVED".equalsIgnoreCase(a.getStatus()))
                .count();

        DashboardSummaryDTO dto = new DashboardSummaryDTO();
        dto.setTankLevelPercent(tank != null ? tank.getLevelPercent() : 0.0);
        dto.setTankLitres(tank != null ? tank.getWaterLitres() : 0.0);
        dto.setTankCapacityLitres(dataStore.getSettings().getTankCapacityLitres());
        dto.setTankStatus((String) tankService.getTankStatistics().get("tankStatus"));
        dto.setPumpStatus(tank != null ? tank.getPumpStatus() : "OFF");
        dto.setPumpMode(tank != null ? tank.getPumpMode() : "AUTO");
        dto.setTodayConsumptionLitres(consumption.getTotalConsumedLitres());
        dto.setTotalHouses(dataStore.getHouses().size());
        dto.setActiveAlertsCount((int) activeAlerts);
        dto.setMonthlyConsumptionLitres(dataStore.getHouses().values().stream().mapToDouble(h -> h.getMonthlyUsageLitres()).sum());
        dto.setUnexplainedLossLitres(consumption.getUnexplainedLossLitres());
        dto.setMainSuppliedLitres(consumption.getTotalSuppliedLitres());
        dto.setDistributionMismatchPercent(consumption.getLossPercentage());
        dto.setCurrentPressureBar(dataStore.getCurrentPressureBar());
        dto.setSystemHealth(activeAlerts > 2 ? "WARNING" : "HEALTHY");

        return ResponseEntity.ok(dto);
    }

    @GetMapping("/recent-alerts")
    public ResponseEntity<List<Alert>> getRecentAlerts(@RequestParam(name = "limit", defaultValue = "5") int limit) {
        List<Alert> recent = dataStore.getAlerts().stream()
                .limit(limit)
                .collect(Collectors.toList());
        return ResponseEntity.ok(recent);
    }
}
