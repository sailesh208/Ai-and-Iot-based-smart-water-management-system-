package com.aquanest.model;

public class SystemSettings {
    private double tankCapacityLitres;
    private double lowThresholdPercent;
    private double fullThresholdPercent;
    private double waterTariffPerLitre;
    private double fixedMonthlyCharge;
    private String billingCycle;           // e.g. "MONTHLY"
    private int billingDueDays;            // e.g. 10
    private double flowCalibrationFactor;  // e.g. 450.0 pulses/litre
    private double pressureThresholdBar;   // e.g. 1.8 bar
    private double leakageTolerancePercent; // e.g. 5.0%
    private double abnormalUsageThreshold; // e.g. 1.7x rolling average
    private boolean demoMode;
    private String notificationEmail;

    public SystemSettings() {
        this.tankCapacityLitres = 4000.0;
        this.lowThresholdPercent = 20.0;
        this.fullThresholdPercent = 90.0;
        this.waterTariffPerLitre = 0.10;
        this.fixedMonthlyCharge = 200.0;
        this.billingCycle = "MONTHLY";
        this.billingDueDays = 10;
        this.flowCalibrationFactor = 450.0;
        this.pressureThresholdBar = 1.8;
        this.leakageTolerancePercent = 5.0;
        this.abnormalUsageThreshold = 1.7;
        this.demoMode = true;
        this.notificationEmail = "admin@aquanest.io";
    }

    // Getters and Setters
    public double getTankCapacityLitres() { return tankCapacityLitres; }
    public void setTankCapacityLitres(double tankCapacityLitres) { this.tankCapacityLitres = tankCapacityLitres; }

    public double getLowThresholdPercent() { return lowThresholdPercent; }
    public void setLowThresholdPercent(double lowThresholdPercent) { this.lowThresholdPercent = lowThresholdPercent; }

    public double getFullThresholdPercent() { return fullThresholdPercent; }
    public void setFullThresholdPercent(double fullThresholdPercent) { this.fullThresholdPercent = fullThresholdPercent; }

    public double getWaterTariffPerLitre() { return waterTariffPerLitre; }
    public void setWaterTariffPerLitre(double waterTariffPerLitre) { this.waterTariffPerLitre = waterTariffPerLitre; }

    public double getFixedMonthlyCharge() { return fixedMonthlyCharge; }
    public void setFixedMonthlyCharge(double fixedMonthlyCharge) { this.fixedMonthlyCharge = fixedMonthlyCharge; }

    public String getBillingCycle() { return billingCycle; }
    public void setBillingCycle(String billingCycle) { this.billingCycle = billingCycle; }

    public int getBillingDueDays() { return billingDueDays; }
    public void setBillingDueDays(int billingDueDays) { this.billingDueDays = billingDueDays; }

    public double getFlowCalibrationFactor() { return flowCalibrationFactor; }
    public void setFlowCalibrationFactor(double flowCalibrationFactor) { this.flowCalibrationFactor = flowCalibrationFactor; }

    public double getPressureThresholdBar() { return pressureThresholdBar; }
    public void setPressureBarThreshold(double pressureThresholdBar) { this.pressureThresholdBar = pressureThresholdBar; }

    public double getLeakageTolerancePercent() { return leakageTolerancePercent; }
    public void setLeakageTolerancePercent(double leakageTolerancePercent) { this.leakageTolerancePercent = leakageTolerancePercent; }

    public double getAbnormalUsageThreshold() { return abnormalUsageThreshold; }
    public void setAbnormalUsageThreshold(double abnormalUsageThreshold) { this.abnormalUsageThreshold = abnormalUsageThreshold; }

    public boolean isDemoMode() { return demoMode; }
    public void setDemoMode(boolean demoMode) { this.demoMode = demoMode; }

    public String getNotificationEmail() { return notificationEmail; }
    public void setNotificationEmail(String notificationEmail) { this.notificationEmail = notificationEmail; }
}
