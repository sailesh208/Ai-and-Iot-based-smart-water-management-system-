package com.aquanest.controller;

import com.aquanest.security.SecurityGuard;
import com.aquanest.service.ReportService;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/reports")
@CrossOrigin(origins = "*")
public class ReportController {

    private final ReportService reportService;
    private final SecurityGuard securityGuard;

    public ReportController(ReportService reportService, SecurityGuard securityGuard) {
        this.reportService = reportService;
        this.securityGuard = securityGuard;
    }

    @GetMapping("/consumption")
    public ResponseEntity<List<Map<String, Object>>> getConsumptionReport(
            @RequestParam(name = "period", required = false, defaultValue = "MONTHLY") String period,
            @RequestParam(name = "houseId", required = false, defaultValue = "ALL") String houseId,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        return ResponseEntity.ok(reportService.generateConsumptionReport(period, houseId));
    }

    @GetMapping(value = "/consumption/csv", produces = "text/csv; charset=UTF-8")
    public ResponseEntity<String> getConsumptionReportCsv(
            @RequestParam(name = "period", required = false, defaultValue = "MONTHLY") String period,
            @RequestParam(name = "houseId", required = false, defaultValue = "ALL") String houseId,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        String csv = reportService.generateConsumptionReportCsv(period, houseId);
        String filename = "aquanest_consumption_" + LocalDate.now() + ".csv";
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .body("\ufeff" + csv);
    }

    @GetMapping("/billing")
    public ResponseEntity<List<Map<String, Object>>> getBillingReport(
            @RequestParam(name = "month", required = false, defaultValue = "") String month,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        return ResponseEntity.ok(reportService.generateBillingReport(month));
    }

    @GetMapping(value = "/billing/csv", produces = "text/csv; charset=UTF-8")
    public ResponseEntity<String> getBillingReportCsv(
            @RequestParam(name = "month", required = false, defaultValue = "") String month,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        String csv = reportService.generateBillingReportCsv(month);
        String filename = "aquanest_billing_" + LocalDate.now() + ".csv";
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .body("\ufeff" + csv);
    }

    @GetMapping("/leakage")
    public ResponseEntity<List<Map<String, Object>>> getLeakageReport(
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        return ResponseEntity.ok(reportService.generateLeakageReport());
    }

    @GetMapping(value = "/leakage/csv", produces = "text/csv; charset=UTF-8")
    public ResponseEntity<String> getLeakageReportCsv(
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        String csv = reportService.generateLeakageReportCsv();
        String filename = "aquanest_leakage_" + LocalDate.now() + ".csv";
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .body("\ufeff" + csv);
    }

    @GetMapping(value = "/anomalies/csv", produces = "text/csv; charset=UTF-8")
    public ResponseEntity<String> getAnomaliesReportCsv(
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        String csv = reportService.generateAnomaliesReportCsv();
        String filename = "aquanest_anomalies_" + LocalDate.now() + ".csv";
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .body("\ufeff" + csv);
    }

    @GetMapping(value = "/pumplogs/csv", produces = "text/csv; charset=UTF-8")
    public ResponseEntity<String> getPumpLogsReportCsv(
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        String csv = reportService.generatePumpLogsReportCsv();
        String filename = "aquanest_pumplogs_" + LocalDate.now() + ".csv";
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .body("\ufeff" + csv);
    }

    @GetMapping(value = "/all/csv", produces = "text/csv; charset=UTF-8")
    public ResponseEntity<String> getAllReportsBundleCsv(
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        String csv = reportService.generateAllReportsBundleCsv();
        String filename = "aquanest_master_water_audit_" + LocalDate.now() + ".csv";
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + filename + "\"")
                .body("\ufeff" + csv);
    }
}

