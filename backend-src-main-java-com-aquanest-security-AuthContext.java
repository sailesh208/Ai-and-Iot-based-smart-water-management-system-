package com.aquanest.security;

public class AuthContext {
    private static final ThreadLocal<UserPrincipal> CURRENT_USER = new ThreadLocal<>();

    public static void setCurrentUser(UserPrincipal principal) {
        CURRENT_USER.set(principal);
    }

    public static UserPrincipal getCurrentUser() {
        return CURRENT_USER.get();
    }

    public static void clear() {
        CURRENT_USER.remove();
    }

    public static class UserPrincipal {
        private final String userId;
        private final String role;
        private final String houseId;

        public UserPrincipal(String userId, String role, String houseId) {
            this.userId = userId;
            this.role = role;
            this.houseId = houseId;
        }

        public String getUserId() { return userId; }
        public String getRole() { return role; }
        public String getHouseId() { return houseId; }
        public boolean isAdmin() { return "ADMIN".equalsIgnoreCase(role); }
    }
}
