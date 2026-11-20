package com.aquanest.model;

import java.time.Instant;

public class ConsumptionRecord {
    private String id;
    private String houseId;
    private String period; // "HOURLY", "DAILY", "WEEKLY", "MONTHLY", "INTERVAL"
    private double litres;
    private Instant startTime;
    private Instant endTime;
    private String calculationStatus; // "VALID", "ESTIMATED", "ADJUSTED"

    public ConsumptionRecord() {
        this.calculationStatus = "VALID";
    }

    public ConsumptionRecord(String id, String houseId, String period, double litres, Instant startTime, Instant endTime) {
        this.id = id;
        this.houseId = houseId;
        this.period = period;
        this.litres = litres;
        this.startTime = startTime;
        this.endTime = endTime;
        this.calculationStatus = "VALID";
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getHouseId() { return houseId; }
    public void setHouseId(String houseId) { this.houseId = houseId; }

    public String getPeriod() { return period; }
    public void setPeriod(String period) { this.period = period; }

    public double getLitres() { return litres; }
    public void setLitres(double litres) { this.litres = litres; }

    public Instant getStartTime() { return startTime; }
    public void setStartTime(Instant startTime) { this.startTime = startTime; }

    public Instant getEndTime() { return endTime; }
    public void setEndTime(Instant endTime) { this.endTime = endTime; }

    public String getCalculationStatus() { return calculationStatus; }
    public void setCalculationStatus(String calculationStatus) { this.calculationStatus = calculationStatus; }
}
