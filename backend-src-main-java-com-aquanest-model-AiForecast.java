package com.aquanest.model;

import java.time.LocalDate;

public class AiForecast {
    private String id;
    private String houseId;            // "ALL" or specific house
    private LocalDate forecastDate;
    private double predictedLitres;
    private double actualLitres;       // populated when date passes
    private double lowerBoundLitres;
    private double upperBoundLitres;
    private String peakPeriod;         // e.g. "07:00 - 09:00"
    private double confidenceScore;

    public AiForecast() {}

    public AiForecast(String id, String houseId, LocalDate forecastDate, double predictedLitres,
                      double lowerBoundLitres, double upperBoundLitres, String peakPeriod) {
        this.id = id;
        this.houseId = houseId;
        this.forecastDate = forecastDate;
        this.predictedLitres = predictedLitres;
        this.lowerBoundLitres = lowerBoundLitres;
        this.upperBoundLitres = upperBoundLitres;
        this.peakPeriod = peakPeriod;
        this.confidenceScore = 0.92;
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getHouseId() { return houseId; }
    public void setHouseId(String houseId) { this.houseId = houseId; }

    public LocalDate getForecastDate() { return forecastDate; }
    public void setForecastDate(LocalDate forecastDate) { this.forecastDate = forecastDate; }

    public double getPredictedLitres() { return predictedLitres; }
    public void setPredictedLitres(double predictedLitres) { this.predictedLitres = predictedLitres; }

    public double getActualLitres() { return actualLitres; }
    public void setActualLitres(double actualLitres) { this.actualLitres = actualLitres; }

    public double getLowerBoundLitres() { return lowerBoundLitres; }
    public void setLowerBoundLitres(double lowerBoundLitres) { this.lowerBoundLitres = lowerBoundLitres; }

    public double getUpperBoundLitres() { return upperBoundLitres; }
    public void setUpperBoundLitres(double upperBoundLitres) { this.upperBoundLitres = upperBoundLitres; }

    public String getPeakPeriod() { return peakPeriod; }
    public void setPeakPeriod(String peakPeriod) { this.peakPeriod = peakPeriod; }

    public double getConfidenceScore() { return confidenceScore; }
    public void setConfidenceScore(double confidenceScore) { this.confidenceScore = confidenceScore; }
}
