package com.aquanest.model;

import java.time.Instant;

public class Alert {
    private String id;
    private String type;         // "LOW_TANK", "FULL_TANK", "PUMP", "TANK_LEAKAGE", "PIPE_LEAKAGE", "ABNORMAL_CONSUMPTION", "SENSOR_FAULT", "PRESSURE_ABNORMALITY", "SYSTEM_CONNECTION"
    private String severity;     // "INFO", "WARNING", "CRITICAL"
    private String houseId;      // "ALL" or specific house e.g. "H101"
    private String message;
    private Instant timestamp;
    private String status;       // "NEW", "ACKNOWLEDGED", "RESOLVED"

    public Alert() {
        this.timestamp = Instant.now();
        this.status = "NEW";
    }

    public Alert(String id, String type, String severity, String houseId, String message) {
        this.id = id;
        this.type = type;
        this.severity = severity;
        this.houseId = houseId;
        this.message = message;
        this.timestamp = Instant.now();
        this.status = "NEW";
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getSeverity() { return severity; }
    public void setSeverity(String severity) { this.severity = severity; }

    public String getHouseId() { return houseId; }
    public void setHouseId(String houseId) { this.houseId = houseId; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public Instant getTimestamp() { return timestamp; }
    public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
