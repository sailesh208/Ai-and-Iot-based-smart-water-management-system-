package com.aquanest.controller;

import com.aquanest.model.House;
import com.aquanest.security.SecurityGuard;
import com.aquanest.service.HouseService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/houses")
@CrossOrigin(origins = "*")
public class HouseController {

    private final HouseService houseService;
    private final SecurityGuard securityGuard;

    public HouseController(HouseService houseService, SecurityGuard securityGuard) {
        this.houseService = houseService;
        this.securityGuard = securityGuard;
    }

    @GetMapping
    public ResponseEntity<List<House>> getAllHouses(
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        if ("RESIDENT".equalsIgnoreCase(role) && userHouseId != null) {
            // Strictly confine resident to their own house
            House h = houseService.getHouseById(userHouseId);
            return ResponseEntity.ok(List.of(h));
        }
        return ResponseEntity.ok(houseService.getAllHouses());
    }

    @GetMapping("/{id}")
    public ResponseEntity<House> getHouseById(
            @PathVariable(name = "id") String id,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        securityGuard.validateHouseAccess(role, userHouseId, id);
        return ResponseEntity.ok(houseService.getHouseById(id));
    }

    @PostMapping
    public ResponseEntity<House> createHouse(
            @RequestBody House house,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        return new ResponseEntity<>(houseService.createHouse(house), HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    public ResponseEntity<House> updateHouse(
            @PathVariable(name = "id") String id,
            @RequestBody House house,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        return ResponseEntity.ok(houseService.updateHouse(id, house));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteHouse(
            @PathVariable(name = "id") String id,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        houseService.deactivateHouse(id);
        return ResponseEntity.noContent().build();
    }
}
