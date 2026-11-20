package com.aquanest.service;

import com.aquanest.model.AiAnomaly;
import com.aquanest.model.Bill;
import com.aquanest.model.House;
import com.aquanest.model.PumpLog;
import com.aquanest.repository.DataStore;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.*;

@Service
public class ReportService {

    private final DataStore dataStore;

    public ReportService(DataStore dataStore) {
        this.dataStore = dataStore;
    }

    public List<Map<String, Object>> generateConsumptionReport(String period, String houseId) {
        List<Map<String, Object>> rows = new ArrayList<>();
        Collection<House> houses = (houseId != null && !houseId.equalsIgnoreCase("ALL"))
                ? Collections.singletonList(dataStore.getHouseById(houseId))
                : dataStore.getHouses().values();

        for (House h : houses) {
            if (h == null) continue;
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("houseId", h.getHouseId());
            row.put("houseNumber", h.getHouseNumber());
            row.put("residentName", h.getResidentName());
            row.put("todayUsageLitres", h.getTodayUsageLitres());
            row.put("monthlyUsageLitres", h.getMonthlyUsageLitres());
            row.put("averageDailyLitres", h.getAverageDailyLitres());
            row.put("peakUsageLitres", h.getPeakUsageLitres());
            row.put("status", h.getStatus());
            rows.add(row);
        }
        return rows;
    }

    public String generateConsumptionReportCsv(String period, String houseId) {
        StringBuilder sb = new StringBuilder();
        sb.append("Report Date,Unit ID,Flat Number,Resident Name,Today Usage (Litres),Monthly Usage (Litres),Daily Average (Litres),Peak Usage (Litres),Status\n");
        String todayStr = LocalDate.now().toString();
        List<Map<String, Object>> rows = generateConsumptionReport(period, houseId);
        for (Map<String, Object> r : rows) {
            sb.append(escapeCsv(todayStr)).append(",")
              .append(escapeCsv(r.get("houseId"))).append(",")
              .append(escapeCsv(r.get("houseNumber"))).append(",")
              .append(escapeCsv(r.get("residentName"))).append(",")
              .append(r.get("todayUsageLitres")).append(",")
              .append(r.get("monthlyUsageLitres")).append(",")
              .append(r.get("averageDailyLitres")).append(",")
              .append(r.get("peakUsageLitres")).append(",")
              .append(escapeCsv(r.get("status"))).append("\n");
        }
        return sb.toString();
    }

    public List<Map<String, Object>> generateBillingReport(String month) {
        List<Map<String, Object>> rows = new ArrayList<>();
        for (Bill b : dataStore.getBills().values()) {
            if (month != null && !month.isBlank() && !b.getBillingPeriod().equalsIgnoreCase(month)) {
                continue;
            }
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("billId", b.getId());
            row.put("houseId", b.getHouseId());
            row.put("houseNumber", b.getHouseNumber());
            row.put("residentName", b.getResidentName());
            row.put("billingPeriod", b.getBillingPeriod());
            row.put("consumptionLitres", b.getConsumptionLitres());
            row.put("waterRate", b.getWaterRate());
            row.put("waterCharge", b.getWaterCharge());
            row.put("fixedCharge", b.getFixedCharge());
            row.put("totalAmount", b.getTotalAmount());
            row.put("paymentStatus", b.getPaymentStatus());
            row.put("dueDate", b.getDueDate());
            rows.add(row);
        }
        return rows;
    }

    public String generateBillingReportCsv(String month) {
        StringBuilder sb = new StringBuilder();
        sb.append("Invoice ID,Unit ID,Flat Number,Resident Name,Billing Period,Consumption (Litres),Tariff Rate (INR/L),Water Charge (INR),Fixed Maintenance (INR),Total Amount (INR),Payment Status,Due Date\n");
        List<Map<String, Object>> rows = generateBillingReport(month);
        for (Map<String, Object> r : rows) {
            sb.append(escapeCsv(r.get("billId"))).append(",")
              .append(escapeCsv(r.get("houseId"))).append(",")
              .append(escapeCsv(r.get("houseNumber"))).append(",")
              .append(escapeCsv(r.get("residentName"))).append(",")
              .append(escapeCsv(r.get("billingPeriod"))).append(",")
              .append(r.get("consumptionLitres")).append(",")
              .append(r.get("waterRate")).append(",")
              .append(r.get("waterCharge")).append(",")
              .append(r.get("fixedCharge")).append(",")
              .append(r.get("totalAmount")).append(",")
              .append(escapeCsv(r.get("paymentStatus"))).append(",")
              .append(escapeCsv(r.get("dueDate"))).append("\n");
        }
        return sb.toString();
    }

    public List<Map<String, Object>> generateLeakageReport() {
        List<Map<String, Object>> rows = new ArrayList<>();
        dataStore.getLeakageAlerts().forEach(l -> {
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("alertId", l.getId());
            row.put("type", l.getType());
            row.put("zone", l.getZone());
            row.put("estimatedLossLitres", l.getEstimatedLossLitres());
            row.put("severity", l.getSeverity());
            row.put("pressureBar", l.getPressureBar());
            row.put("status", l.getStatus());
            row.put("detectedAt", l.getDetectedAt().toString());
            rows.add(row);
        });
        return rows;
    }

    public String generateLeakageReportCsv() {
        StringBuilder sb = new StringBuilder();
        sb.append("Incident ID,Leakage Type,Zone,Estimated Loss (Litres),Severity,Pressure (bar),Status,Detected Timestamp\n");
        List<Map<String, Object>> rows = generateLeakageReport();
        for (Map<String, Object> r : rows) {
            sb.append(escapeCsv(r.get("alertId"))).append(",")
              .append(escapeCsv(r.get("type"))).append(",")
              .append(escapeCsv(r.get("zone"))).append(",")
              .append(r.get("estimatedLossLitres")).append(",")
              .append(escapeCsv(r.get("severity"))).append(",")
              .append(r.get("pressureBar")).append(",")
              .append(escapeCsv(r.get("status"))).append(",")
              .append(escapeCsv(r.get("detectedAt"))).append("\n");
        }
        return sb.toString();
    }

    public String generateAnomaliesReportCsv() {
        StringBuilder sb = new StringBuilder();
        sb.append("Anomaly ID,Unit ID,Expected Daily (L),Actual Usage (L),Excess Wasted (L),IsolationForest Score,Status,Reason,Recommendation\n");
        for (AiAnomaly a : dataStore.getAnomalies()) {
            double excess = Math.max(0.0, a.getActualUsageLitres() - a.getExpectedUsageLitres());
            sb.append(escapeCsv(a.getId())).append(",")
              .append(escapeCsv(a.getHouseId())).append(",")
              .append(a.getExpectedUsageLitres()).append(",")
              .append(a.getActualUsageLitres()).append(",")
              .append(excess).append(",")
              .append(a.getAnomalyScore()).append(",")
              .append(escapeCsv(a.getStatus())).append(",")
              .append(escapeCsv(a.getReason())).append(",")
              .append(escapeCsv(a.getRecommendation())).append("\n");
        }
        return sb.toString();
    }

    public String generatePumpLogsReportCsv() {
        StringBuilder sb = new StringBuilder();
        sb.append("Log ID,Pump Status,Operating Mode,Tank Level (%),Start Time,Duration (Seconds),Duration (Minutes),Energy (kWh),Electricity Cost (INR),Trigger\n");
        for (PumpLog p : dataStore.getPumpLogs()) {
            double mins = Math.round((p.getDurationSeconds() / 60.0) * 10.0) / 10.0;
            double kwh = Math.round(((p.getDurationSeconds() / 3600.0) * 1.5) * 100.0) / 100.0;
            double cost = Math.round((kwh * 8.0) * 100.0) / 100.0;
            sb.append(escapeCsv(p.getId())).append(",")
              .append(escapeCsv(p.getStatus())).append(",")
              .append(escapeCsv(p.getMode())).append(",")
              .append(p.getTankLevel()).append(",")
              .append(escapeCsv(p.getStartTime())).append(",")
              .append(p.getDurationSeconds()).append(",")
              .append(mins).append(",")
              .append(kwh).append(",")
              .append(cost).append(",")
              .append(escapeCsv(p.getTrigger())).append("\n");
        }
        return sb.toString();
    }

    public String generateAllReportsBundleCsv() {
        StringBuilder sb = new StringBuilder();
        sb.append("=== AQUANEST ENTERPRISE WATER AUDIT COMPLIANCE BUNDLE ===\n\n");
        sb.append("--- SECTION 1: APARTMENT WATER CONSUMPTION ---\n");
        sb.append(generateConsumptionReportCsv("MONTHLY", "ALL")).append("\n");
        sb.append("--- SECTION 2: WATER BILLING & INVOICES ---\n");
        sb.append(generateBillingReportCsv(null)).append("\n");
        sb.append("--- SECTION 3: LEAKAGE DIAGNOSTICS & LOSS LOG ---\n");
        sb.append(generateLeakageReportCsv()).append("\n");
        sb.append("--- SECTION 4: AI ISOLATIONFOREST ANOMALY DETECTIONS ---\n");
        sb.append(generateAnomaliesReportCsv()).append("\n");
        sb.append("--- SECTION 5: PUMP OPERATING & ENERGY LOGS ---\n");
        sb.append(generatePumpLogsReportCsv()).append("\n");
        return sb.toString();
    }

    private String escapeCsv(Object val) {
        if (val == null) return "";
        String s = val.toString().trim();
        if (s.contains(",") || s.contains("\"") || s.contains("\n")) {
            return "\"" + s.replace("\"", "\"\"") + "\"";
        }
        return s;
    }
}
