package com.aquanest.controller;

import com.aquanest.dto.PumpControlDTO;
import com.aquanest.model.PumpLog;
import com.aquanest.service.PumpService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/pump")
@CrossOrigin(origins = "*")
public class PumpController {

    private final PumpService pumpService;

    public PumpController(PumpService pumpService) {
        this.pumpService = pumpService;
    }

    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getPumpStatus() {
        return ResponseEntity.ok(pumpService.getPumpStatus());
    }

    @PostMapping("/control")
    public ResponseEntity<Map<String, Object>> controlPump(
            @RequestBody PumpControlDTO request,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        Map<String, Object> result = pumpService.controlPump(request, role);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/logs")
    public ResponseEntity<List<PumpLog>> getPumpLogs() {
        return ResponseEntity.ok(pumpService.getPumpLogs());
    }
}
