package com.aquanest.model;

import java.time.Instant;

public class AiAnomaly {
    private String id;
    private String houseId;
    private Instant timestamp;
    private double expectedUsageLitres;
    private double actualUsageLitres;
    private double anomalyScore;        // 0.0 to 1.0 (Isolation Forest or deviation score)
    private String status;              // "ANOMALOUS", "RESOLVED"
    private String reason;              // e.g. "Continuous 4-hour nocturnal flow detected"
    private String recommendation;        // e.g. "Inspect toilet flapper and fixture seals"

    public AiAnomaly() {
        this.timestamp = Instant.now();
        this.status = "ANOMALOUS";
    }

    public AiAnomaly(String id, String houseId, double expectedUsageLitres, double actualUsageLitres,
                     double anomalyScore, String reason, String recommendation) {
        this.id = id;
        this.houseId = houseId;
        this.timestamp = Instant.now();
        this.expectedUsageLitres = expectedUsageLitres;
        this.actualUsageLitres = actualUsageLitres;
        this.anomalyScore = anomalyScore;
        this.status = "ANOMALOUS";
        this.reason = reason;
        this.recommendation = recommendation;
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getHouseId() { return houseId; }
    public void setHouseId(String houseId) { this.houseId = houseId; }

    public Instant getTimestamp() { return timestamp; }
    public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }

    public double getExpectedUsageLitres() { return expectedUsageLitres; }
    public void setExpectedUsageLitres(double expectedUsageLitres) { this.expectedUsageLitres = expectedUsageLitres; }

    public double getActualUsageLitres() { return actualUsageLitres; }
    public void setActualUsageLitres(double actualUsageLitres) { this.actualUsageLitres = actualUsageLitres; }

    public double getAnomalyScore() { return anomalyScore; }
    public void setAnomalyScore(double anomalyScore) { this.anomalyScore = anomalyScore; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getReason() { return reason; }
    public void setReason(String reason) { this.reason = reason; }

    public String getRecommendation() { return recommendation; }
    public void setRecommendation(String recommendation) { this.recommendation = recommendation; }
}
