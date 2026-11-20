package com.aquanest.dto;

import java.time.Instant;

public class DashboardSummaryDTO {
    private double tankLevelPercent;
    private double tankLitres;
    private double tankCapacityLitres;
    private String tankStatus;       // "OPTIMAL", "LOW", "CRITICAL", "FILLING"
    private String pumpStatus;       // "ON", "OFF"
    private String pumpMode;         // "AUTO", "MANUAL"
    private double todayConsumptionLitres;
    private int totalHouses;
    private int activeAlertsCount;
    private double monthlyConsumptionLitres;
    private double unexplainedLossLitres;
    private double mainSuppliedLitres;
    private double distributionMismatchPercent;
    private double currentPressureBar;
    private String systemHealth;     // "HEALTHY", "WARNING", "DEGRADED"
    private Instant lastUpdated;

    public DashboardSummaryDTO() {
        this.lastUpdated = Instant.now();
        this.systemHealth = "HEALTHY";
    }

    // Getters and Setters
    public double getTankLevelPercent() { return tankLevelPercent; }
    public void setTankLevelPercent(double tankLevelPercent) { this.tankLevelPercent = tankLevelPercent; }

    public double getTankLitres() { return tankLitres; }
    public void setTankLitres(double tankLitres) { this.tankLitres = tankLitres; }

    public double getTankCapacityLitres() { return tankCapacityLitres; }
    public void setTankCapacityLitres(double tankCapacityLitres) { this.tankCapacityLitres = tankCapacityLitres; }

    public String getTankStatus() { return tankStatus; }
    public void setTankStatus(String tankStatus) { this.tankStatus = tankStatus; }

    public String getPumpStatus() { return pumpStatus; }
    public void setPumpStatus(String pumpStatus) { this.pumpStatus = pumpStatus; }

    public String getPumpMode() { return pumpMode; }
    public void setPumpMode(String pumpMode) { this.pumpMode = pumpMode; }

    public double getTodayConsumptionLitres() { return todayConsumptionLitres; }
    public void setTodayConsumptionLitres(double todayConsumptionLitres) { this.todayConsumptionLitres = todayConsumptionLitres; }

    public int getTotalHouses() { return totalHouses; }
    public void setTotalHouses(int totalHouses) { this.totalHouses = totalHouses; }

    public int getActiveAlertsCount() { return activeAlertsCount; }
    public void setActiveAlertsCount(int activeAlertsCount) { this.activeAlertsCount = activeAlertsCount; }

    public double getMonthlyConsumptionLitres() { return monthlyConsumptionLitres; }
    public void setMonthlyConsumptionLitres(double monthlyConsumptionLitres) { this.monthlyConsumptionLitres = monthlyConsumptionLitres; }

    public double getUnexplainedLossLitres() { return unexplainedLossLitres; }
    public void setUnexplainedLossLitres(double unexplainedLossLitres) { this.unexplainedLossLitres = unexplainedLossLitres; }

    public double getMainSuppliedLitres() { return mainSuppliedLitres; }
    public void setMainSuppliedLitres(double mainSuppliedLitres) { this.mainSuppliedLitres = mainSuppliedLitres; }

    public double getDistributionMismatchPercent() { return distributionMismatchPercent; }
    public void setDistributionMismatchPercent(double distributionMismatchPercent) { this.distributionMismatchPercent = distributionMismatchPercent; }

    public double getCurrentPressureBar() { return currentPressureBar; }
    public void setCurrentPressureBar(double currentPressureBar) { this.currentPressureBar = currentPressureBar; }

    public String getSystemHealth() { return systemHealth; }
    public void setSystemHealth(String systemHealth) { this.systemHealth = systemHealth; }

    public Instant getLastUpdated() { return lastUpdated; }
    public void setLastUpdated(Instant lastUpdated) { this.lastUpdated = lastUpdated; }
}
