package com.aquanest.controller;

import com.aquanest.model.LeakageAlert;
import com.aquanest.service.LeakageDetectionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/leakage")
@CrossOrigin(origins = "*")
public class LeakageController {

    private final LeakageDetectionService leakageService;

    public LeakageController(LeakageDetectionService leakageService) {
        this.leakageService = leakageService;
    }

    @GetMapping
    public ResponseEntity<List<LeakageAlert>> getAllLeakages() {
        return ResponseEntity.ok(leakageService.getAllLeakageAlerts());
    }

    @GetMapping("/tank")
    public ResponseEntity<List<LeakageAlert>> getTankLeakages() {
        return ResponseEntity.ok(leakageService.getTankLeakageAlerts());
    }

    @GetMapping("/pipe")
    public ResponseEntity<List<LeakageAlert>> getPipeLeakages() {
        return ResponseEntity.ok(leakageService.getPipeLeakageAlerts());
    }

    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getStatistics() {
        return ResponseEntity.ok(leakageService.getLeakageStatistics());
    }
}
