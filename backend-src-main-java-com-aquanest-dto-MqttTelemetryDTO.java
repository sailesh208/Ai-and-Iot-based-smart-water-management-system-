package com.aquanest.dto;

public class MqttTelemetryDTO {
    private String deviceId;
    private String timestamp;
    private String houseId;
    private Double tankLevelPercent;
    private Double tankLitres;
    private String pumpStatus;
    private Double flowRate;
    private Long pulseCount;
    private Double cumulativeLitres;
    private Double pressureBar;

    public MqttTelemetryDTO() {}

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public String getHouseId() { return houseId; }
    public void setHouseId(String houseId) { this.houseId = houseId; }

    public Double getTankLevelPercent() { return tankLevelPercent; }
    public void setTankLevelPercent(Double tankLevelPercent) { this.tankLevelPercent = tankLevelPercent; }

    public Double getTankLitres() { return tankLitres; }
    public void setTankLitres(Double tankLitres) { this.tankLitres = tankLitres; }

    public String getPumpStatus() { return pumpStatus; }
    public void setPumpStatus(String pumpStatus) { this.pumpStatus = pumpStatus; }

    public Double getFlowRate() { return flowRate; }
    public void setFlowRate(Double flowRate) { this.flowRate = flowRate; }

    public Long getPulseCount() { return pulseCount; }
    public void setPulseCount(Long pulseCount) { this.pulseCount = pulseCount; }

    public Double getCumulativeLitres() { return cumulativeLitres; }
    public void setCumulativeLitres(Double cumulativeLitres) { this.cumulativeLitres = cumulativeLitres; }

    public Double getPressureBar() { return pressureBar; }
    public void setPressureBar(Double pressureBar) { this.pressureBar = pressureBar; }
}
