package com.aquanest.controller;

import com.aquanest.model.Alert;
import com.aquanest.service.AlertService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/alerts")
@CrossOrigin(origins = "*")
public class AlertController {

    private final AlertService alertService;

    public AlertController(AlertService alertService) {
        this.alertService = alertService;
    }

    @GetMapping
    public ResponseEntity<List<Alert>> getAlerts(
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        if ("RESIDENT".equalsIgnoreCase(role) && userHouseId != null) {
            return ResponseEntity.ok(alertService.getAlertsForHouse(userHouseId));
        }
        return ResponseEntity.ok(alertService.getAllAlerts());
    }

    @PutMapping("/{id}/read")
    public ResponseEntity<Alert> markAsRead(@PathVariable(name = "id") String id) {
        return ResponseEntity.ok(alertService.markAsRead(id));
    }

    @PutMapping("/{id}/resolve")
    public ResponseEntity<Alert> resolveAlert(@PathVariable(name = "id") String id) {
        return ResponseEntity.ok(alertService.resolveAlert(id));
    }
}
