package com.aquanest.model;

import java.time.Instant;

public class Recommendation {
    private String id;
    private String target;       // "ALL", "ADMIN", "RESIDENT"
    private String houseId;      // specific house or "ALL"
    private String title;
    private String message;
    private String category;     // "WATER_SAVING", "LEAK_PREVENTION", "PRESSURE_EFFICIENCY", "BILLING_OPTIMIZATION"
    private String priority;     // "HIGH", "MEDIUM", "LOW"
    private Instant createdAt;

    public Recommendation() {
        this.createdAt = Instant.now();
        this.priority = "MEDIUM";
    }

    public Recommendation(String id, String target, String houseId, String title, String message, String category, String priority) {
        this.id = id;
        this.target = target;
        this.houseId = houseId;
        this.title = title;
        this.message = message;
        this.category = category;
        this.priority = priority;
        this.createdAt = Instant.now();
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getTarget() { return target; }
    public void setTarget(String target) { this.target = target; }

    public String getHouseId() { return houseId; }
    public void setHouseId(String houseId) { this.houseId = houseId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getPriority() { return priority; }
    public void setPriority(String priority) { this.priority = priority; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}
