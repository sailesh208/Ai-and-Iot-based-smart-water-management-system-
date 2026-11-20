package com.aquanest.model;

import java.time.Instant;

public class PumpLog {
    private String id;
    private String status;        // "ON" or "OFF"
    private String mode;          // "AUTO" or "MANUAL"
    private double tankLevel;     // percentage at event time
    private Instant startTime;
    private Instant endTime;
    private long durationSeconds;
    private String trigger;       // "LOW_LEVEL_AUTO", "FULL_LEVEL_AUTO", "MANUAL_OVERRIDE_ADMIN", "SAFETY_CUTOFF"

    public PumpLog() {}

    public PumpLog(String id, String status, String mode, double tankLevel, Instant startTime, String trigger) {
        this.id = id;
        this.status = status;
        this.mode = mode;
        this.tankLevel = tankLevel;
        this.startTime = startTime;
        this.trigger = trigger;
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getMode() { return mode; }
    public void setMode(String mode) { this.mode = mode; }

    public double getTankLevel() { return tankLevel; }
    public void setTankLevel(double tankLevel) { this.tankLevel = tankLevel; }

    public Instant getStartTime() { return startTime; }
    public void setStartTime(Instant startTime) { this.startTime = startTime; }

    public Instant getEndTime() { return endTime; }
    public void setEndTime(Instant endTime) { this.endTime = endTime; }

    public long getDurationSeconds() { return durationSeconds; }
    public void setDurationSeconds(long durationSeconds) { this.durationSeconds = durationSeconds; }

    public String getTrigger() { return trigger; }
    public void setTrigger(String trigger) { this.trigger = trigger; }
}
