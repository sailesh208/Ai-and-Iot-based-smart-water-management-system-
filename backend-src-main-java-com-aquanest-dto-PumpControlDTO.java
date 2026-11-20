package com.aquanest.dto;

public class PumpControlDTO {
    private String command; // "START", "STOP"
    private String mode;    // "AUTO", "MANUAL"
    private String requestedBy; // userId

    public PumpControlDTO() {}

    public PumpControlDTO(String command, String mode) {
        this.command = command;
        this.mode = mode;
    }

    public String getCommand() { return command; }
    public void setCommand(String command) { this.command = command; }

    public String getMode() { return mode; }
    public void setMode(String mode) { this.mode = mode; }

    public String getRequestedBy() { return requestedBy; }
    public void setRequestedBy(String requestedBy) { this.requestedBy = requestedBy; }
}
