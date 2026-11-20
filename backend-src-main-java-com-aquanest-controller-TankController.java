package com.aquanest.controller;

import com.aquanest.model.TankReading;
import com.aquanest.service.TankService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/tank")
@CrossOrigin(origins = "*")
public class TankController {

    private final TankService tankService;

    public TankController(TankService tankService) {
        this.tankService = tankService;
    }

    @GetMapping("/current")
    public ResponseEntity<TankReading> getCurrentTankReading() {
        return ResponseEntity.ok(tankService.getCurrentTankReading());
    }

    @GetMapping("/history")
    public ResponseEntity<List<TankReading>> getTankHistory() {
        return ResponseEntity.ok(tankService.getTankHistory());
    }

    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getTankStatistics() {
        return ResponseEntity.ok(tankService.getTankStatistics());
    }
}
