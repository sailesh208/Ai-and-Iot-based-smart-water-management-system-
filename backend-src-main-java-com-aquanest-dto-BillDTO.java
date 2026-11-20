package com.aquanest.dto;

import jakarta.validation.constraints.NotBlank;

public class BillDTO {
    public static class GenerateRequest {
        @NotBlank(message = "Billing period (e.g. 2026-09) is required")
        private String billingPeriod;
        private String dueDate;
        private String houseId; // Optional: specific house or null for all

        public String getBillingPeriod() { return billingPeriod; }
        public void setBillingPeriod(String billingPeriod) { this.billingPeriod = billingPeriod; }

        public String getDueDate() { return dueDate; }
        public void setDueDate(String dueDate) { this.dueDate = dueDate; }

        public String getHouseId() { return houseId; }
        public void setHouseId(String houseId) { this.houseId = houseId; }
    }

    public static class PaymentUpdate {
        private String paymentStatus; // "PAID", "PENDING"
        private String reference;

        public String getPaymentStatus() { return paymentStatus; }
        public void setPaymentStatus(String paymentStatus) { this.paymentStatus = paymentStatus; }

        public String getReference() { return reference; }
        public void setReference(String reference) { this.reference = reference; }
    }
}
