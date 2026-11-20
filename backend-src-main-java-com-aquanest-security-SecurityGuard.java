package com.aquanest.security;

import org.springframework.stereotype.Component;

@Component
public class SecurityGuard {

    public void requireAdmin(String role) {
        if (!"ADMIN".equalsIgnoreCase(role)) {
            throw new SecurityException("Access Denied: Administrative privileges required.");
        }
    }

    public void validateHouseAccess(String role, String userHouseId, String requestedHouseId) {
        if ("ADMIN".equalsIgnoreCase(role)) {
            return; // Admin can access any house
        }
        if (requestedHouseId == null || !requestedHouseId.equalsIgnoreCase(userHouseId)) {
            throw new SecurityException("Access Denied: Resident is restricted to their assigned apartment (" + userHouseId + ").");
        }
    }
}
