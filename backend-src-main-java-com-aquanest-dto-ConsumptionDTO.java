package com.aquanest.dto;

import java.util.Map;

public class ConsumptionDTO {

    public static class Summary {
        private double totalSuppliedLitres;
        private double totalConsumedLitres;
        private double unexplainedLossLitres;
        private double lossPercentage;
        private String toleranceStatus; // "NORMAL", "SUSPICIOUS_LEAK"
        private Map<String, Double> houseConsumption; // houseId -> litres

        public Summary() {}

        public Summary(double totalSuppliedLitres, double totalConsumedLitres, double unexplainedLossLitres,
                       double lossPercentage, String toleranceStatus, Map<String, Double> houseConsumption) {
            this.totalSuppliedLitres = totalSuppliedLitres;
            this.totalConsumedLitres = totalConsumedLitres;
            this.unexplainedLossLitres = unexplainedLossLitres;
            this.lossPercentage = lossPercentage;
            this.toleranceStatus = toleranceStatus;
            this.houseConsumption = houseConsumption;
        }

        public double getTotalSuppliedLitres() { return totalSuppliedLitres; }
        public void setTotalSuppliedLitres(double totalSuppliedLitres) { this.totalSuppliedLitres = totalSuppliedLitres; }

        public double getTotalConsumedLitres() { return totalConsumedLitres; }
        public void setTotalConsumedLitres(double totalConsumedLitres) { this.totalConsumedLitres = totalConsumedLitres; }

        public double getUnexplainedLossLitres() { return unexplainedLossLitres; }
        public void setUnexplainedLossLitres(double unexplainedLossLitres) { this.unexplainedLossLitres = unexplainedLossLitres; }

        public double getLossPercentage() { return lossPercentage; }
        public void setLossPercentage(double lossPercentage) { this.lossPercentage = lossPercentage; }

        public String getToleranceStatus() { return toleranceStatus; }
        public void setToleranceStatus(String toleranceStatus) { this.toleranceStatus = toleranceStatus; }

        public Map<String, Double> getHouseConsumption() { return houseConsumption; }
        public void setHouseConsumption(Map<String, Double> houseConsumption) { this.houseConsumption = houseConsumption; }
    }

    public static class TimeSeriesPoint {
        private String timestamp;
        private double litres;
        private String label;

        public TimeSeriesPoint() {}

        public TimeSeriesPoint(String timestamp, double litres, String label) {
            this.timestamp = timestamp;
            this.litres = litres;
            this.label = label;
        }

        public String getTimestamp() { return timestamp; }
        public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

        public double getLitres() { return litres; }
        public void setLitres(double litres) { this.litres = litres; }

        public String getLabel() { return label; }
        public void setLabel(String label) { this.label = label; }
    }
}
