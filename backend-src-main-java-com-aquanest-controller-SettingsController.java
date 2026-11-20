package com.aquanest.controller;

import com.aquanest.model.SystemSettings;
import com.aquanest.repository.DataStore;
import com.aquanest.security.SecurityGuard;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/settings")
@CrossOrigin(origins = "*")
public class SettingsController {

    private final DataStore dataStore;
    private final SecurityGuard securityGuard;

    public SettingsController(DataStore dataStore, SecurityGuard securityGuard) {
        this.dataStore = dataStore;
        this.securityGuard = securityGuard;
    }

    @GetMapping
    public ResponseEntity<SystemSettings> getSettings() {
        return ResponseEntity.ok(dataStore.getSettings());
    }

    @PutMapping
    public ResponseEntity<SystemSettings> updateSettings(
            @RequestBody SystemSettings settings,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        dataStore.setSettings(settings);
        return ResponseEntity.ok(settings);
    }
}
