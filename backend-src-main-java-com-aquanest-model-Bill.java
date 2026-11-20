package com.aquanest.model;

import java.time.Instant;

public class Bill {
    private String id;
    private String houseId;
    private String houseNumber;
    private String residentName;
    private String billingPeriod;   // e.g. "2026-09"
    private double consumptionLitres;
    private double waterRate;       // Tariff applied at generation, e.g. 0.10
    private double waterCharge;     // consumptionLitres * waterRate
    private double fixedCharge;     // e.g. 200.0
    private double totalAmount;     // waterCharge + fixedCharge
    private Instant generatedAt;
    private String dueDate;         // e.g. "2026-10-10"
    private String paymentStatus;   // "PENDING", "PAID", "OVERDUE"
    private Instant paidAt;

    public Bill() {
        this.generatedAt = Instant.now();
        this.paymentStatus = "PENDING";
    }

    public Bill(String id, String houseId, String houseNumber, String residentName, String billingPeriod,
                double consumptionLitres, double waterRate, double fixedCharge, String dueDate) {
        this.id = id;
        this.houseId = houseId;
        this.houseNumber = houseNumber;
        this.residentName = residentName;
        this.billingPeriod = billingPeriod;
        this.consumptionLitres = consumptionLitres;
        this.waterRate = waterRate;
        this.fixedCharge = fixedCharge;
        this.waterCharge = Math.round(consumptionLitres * waterRate * 100.0) / 100.0;
        this.totalAmount = Math.round((this.waterCharge + this.fixedCharge) * 100.0) / 100.0;
        this.generatedAt = Instant.now();
        this.dueDate = dueDate;
        this.paymentStatus = "PENDING";
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getHouseId() { return houseId; }
    public void setHouseId(String houseId) { this.houseId = houseId; }

    public String getHouseNumber() { return houseNumber; }
    public void setHouseNumber(String houseNumber) { this.houseNumber = houseNumber; }

    public String getResidentName() { return residentName; }
    public void setResidentName(String residentName) { this.residentName = residentName; }

    public String getBillingPeriod() { return billingPeriod; }
    public void setBillingPeriod(String billingPeriod) { this.billingPeriod = billingPeriod; }

    public double getConsumptionLitres() { return consumptionLitres; }
    public void setConsumptionLitres(double consumptionLitres) { this.consumptionLitres = consumptionLitres; }

    public double getWaterRate() { return waterRate; }
    public void setWaterRate(double waterRate) { this.waterRate = waterRate; }

    public double getWaterCharge() { return waterCharge; }
    public void setWaterCharge(double waterCharge) { this.waterCharge = waterCharge; }

    public double getFixedCharge() { return fixedCharge; }
    public void setFixedCharge(double fixedCharge) { this.fixedCharge = fixedCharge; }

    public double getTotalAmount() { return totalAmount; }
    public void setTotalAmount(double totalAmount) { this.totalAmount = totalAmount; }

    public Instant getGeneratedAt() { return generatedAt; }
    public void setGeneratedAt(Instant generatedAt) { this.generatedAt = generatedAt; }

    public String getDueDate() { return dueDate; }
    public void setDueDate(String dueDate) { this.dueDate = dueDate; }

    public String getPaymentStatus() { return paymentStatus; }
    public void setPaymentStatus(String paymentStatus) { this.paymentStatus = paymentStatus; }

    public Instant getPaidAt() { return paidAt; }
    public void setPaidAt(Instant paidAt) { this.paidAt = paidAt; }
}
