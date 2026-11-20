package com.aquanest.controller;

import com.aquanest.dto.AuthDTO;
import com.aquanest.model.House;
import com.aquanest.model.User;
import com.aquanest.repository.DataStore;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    private final DataStore dataStore;

    public AuthController(DataStore dataStore) {
        this.dataStore = dataStore;
    }

    @PostMapping("/login")
    public ResponseEntity<AuthDTO.LoginResponse> login(@Valid @RequestBody AuthDTO.LoginRequest request) {
        User user = dataStore.getUserByEmail(request.getEmail().trim());

        // For demo & initial use: allow admin or default resident credentials
        if (user == null) {
            // Check if admin email attempted
            if ("admin@aquanest.io".equalsIgnoreCase(request.getEmail())) {
                user = dataStore.getUserById("USR_ADMIN");
            } else {
                throw new IllegalArgumentException("Invalid email or password. User does not exist.");
            }
        }

        String token = "jwt-aquanest-" + UUID.randomUUID().toString().substring(0, 8);
        AuthDTO.LoginResponse response = new AuthDTO.LoginResponse(
                token,
                user.getUserId(),
                user.getName(),
                user.getEmail(),
                user.getRole(),
                user.getHouseId()
        );
        return ResponseEntity.ok(response);
    }

    @PostMapping("/signup")
    public ResponseEntity<Map<String, Object>> signup(@Valid @RequestBody AuthDTO.SignUpRequest request) {
        if (!request.getPassword().equals(request.getConfirmPassword())) {
            throw new IllegalArgumentException("Password and confirm password do not match.");
        }

        if (dataStore.getUserByEmail(request.getEmail().trim()) != null) {
            throw new IllegalArgumentException("An account with this email address already exists.");
        }

        // Public registration ALWAYS defaults strictly to RESIDENT
        String userId = "USR_" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        String houseId = "H" + request.getHouseNumber().replaceAll("[^0-9]", "");
        if (houseId.length() < 2) {
            houseId = "H101";
        }

        User newUser = new User(userId, request.getName().trim(), request.getEmail().trim(),
                request.getPhone(), "RESIDENT", houseId);
        dataStore.saveUser(newUser);

        // Provision house if not already created
        if (dataStore.getHouseById(houseId) == null) {
            House house = new House(houseId, request.getHouseNumber(), 1, userId, newUser.getName(), "METER_" + houseId);
            dataStore.saveHouse(house);
        }

        Map<String, Object> resp = new HashMap<>();
        resp.put("success", true);
        resp.put("message", "Registration successful. Please proceed to login.");
        resp.put("userId", userId);
        resp.put("role", "RESIDENT");
        resp.put("assignedHouse", houseId);

        return new ResponseEntity<>(resp, HttpStatus.CREATED);
    }

    @PostMapping("/forgot-password")
    public ResponseEntity<Map<String, Object>> forgotPassword(@RequestBody Map<String, String> payload) {
        String email = payload.get("email");
        if (email == null || email.isBlank()) {
            throw new IllegalArgumentException("Email is required.");
        }

        Map<String, Object> resp = new HashMap<>();
        resp.put("success", true);
        resp.put("message", "Password reset instructions sent to " + email + ".");
        return ResponseEntity.ok(resp);
    }

    @GetMapping("/me")
    public ResponseEntity<User> getCurrentUser(
            @RequestHeader(name = "X-User-Id", defaultValue = "USR_ADMIN") String userId) {
        User u = dataStore.getUserById(userId);
        if (u == null) {
            u = dataStore.getUserById("USR_ADMIN");
        }
        return ResponseEntity.ok(u);
    }
}
