package com.aquanest.model;

import java.time.Instant;

public class LeakageAlert {
    private String id;
    private String type;              // "TANK_LEAKAGE" or "PIPE_LEAKAGE"
    private String houseId;           // "MAIN", "DISTRIBUTION", or specific house "H102"
    private String zone;              // "Overhead Tank Zone", "Main Distribution Pipe", "Flat H104 Internal"
    private double estimatedLossLitres;
    private String severity;          // "NORMAL", "WARNING", "POSSIBLE_LEAK", "CRITICAL"
    private Instant detectedAt;
    private long durationMinutes;
    private String evidence;          // Descriptive telemetry basis
    private double pressureBar;       // Observed pipe pressure
    private double flowMismatchLpm;   // Observed delta between main and sum(house)
    private String status;            // "NEW", "INVESTIGATING", "RESOLVED"

    public LeakageAlert() {
        this.detectedAt = Instant.now();
        this.status = "NEW";
    }

    public LeakageAlert(String id, String type, String houseId, String zone, double estimatedLossLitres,
                        String severity, String evidence, double pressureBar, double flowMismatchLpm) {
        this.id = id;
        this.type = type;
        this.houseId = houseId;
        this.zone = zone;
        this.estimatedLossLitres = estimatedLossLitres;
        this.severity = severity;
        this.evidence = evidence;
        this.pressureBar = pressureBar;
        this.flowMismatchLpm = flowMismatchLpm;
        this.detectedAt = Instant.now();
        this.durationMinutes = 15;
        this.status = "NEW";
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getHouseId() { return houseId; }
    public void setHouseId(String houseId) { this.houseId = houseId; }

    public String getZone() { return zone; }
    public void setZone(String zone) { this.zone = zone; }

    public double getEstimatedLossLitres() { return estimatedLossLitres; }
    public void setEstimatedLossLitres(double estimatedLossLitres) { this.estimatedLossLitres = estimatedLossLitres; }

    public String getSeverity() { return severity; }
    public void setSeverity(String severity) { this.severity = severity; }

    public Instant getDetectedAt() { return detectedAt; }
    public void setDetectedAt(Instant detectedAt) { this.detectedAt = detectedAt; }

    public long getDurationMinutes() { return durationMinutes; }
    public void setDurationMinutes(long durationMinutes) { this.durationMinutes = durationMinutes; }

    public String getEvidence() { return evidence; }
    public void setEvidence(String evidence) { this.evidence = evidence; }

    public double getPressureBar() { return pressureBar; }
    public void setPressureBar(double pressureBar) { this.pressureBar = pressureBar; }

    public double getFlowMismatchLpm() { return flowMismatchLpm; }
    public void setFlowMismatchLpm(double flowMismatchLpm) { this.flowMismatchLpm = flowMismatchLpm; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
