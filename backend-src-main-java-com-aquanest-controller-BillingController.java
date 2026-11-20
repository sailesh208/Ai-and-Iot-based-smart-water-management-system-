package com.aquanest.controller;

import com.aquanest.dto.BillDTO;
import com.aquanest.model.Bill;
import com.aquanest.security.SecurityGuard;
import com.aquanest.service.BillingService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/bills")
@CrossOrigin(origins = "*")
public class BillingController {

    private final BillingService billingService;
    private final SecurityGuard securityGuard;

    public BillingController(BillingService billingService, SecurityGuard securityGuard) {
        this.billingService = billingService;
        this.securityGuard = securityGuard;
    }

    @GetMapping
    public ResponseEntity<List<Bill>> getAllBills(
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        if ("RESIDENT".equalsIgnoreCase(role) && userHouseId != null) {
            return ResponseEntity.ok(billingService.getBillsByHouseId(userHouseId));
        }
        return ResponseEntity.ok(billingService.getAllBills());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Bill> getBillById(
            @PathVariable(name = "id") String id,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        Bill bill = billingService.getBillById(id);
        securityGuard.validateHouseAccess(role, userHouseId, bill.getHouseId());
        return ResponseEntity.ok(bill);
    }

    @GetMapping("/house/{houseId}")
    public ResponseEntity<List<Bill>> getBillsByHouse(
            @PathVariable(name = "houseId") String houseId,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role,
            @RequestHeader(name = "X-User-HouseId", required = false) String userHouseId) {
        securityGuard.validateHouseAccess(role, userHouseId, houseId);
        return ResponseEntity.ok(billingService.getBillsByHouseId(houseId));
    }

    @GetMapping("/month/{month}")
    public ResponseEntity<List<Bill>> getBillsByMonth(
            @PathVariable(name = "month") String month,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        return ResponseEntity.ok(billingService.getBillsByMonth(month));
    }

    @PostMapping("/generate")
    public ResponseEntity<List<Bill>> generateBills(
            @Valid @RequestBody BillDTO.GenerateRequest request,
            @RequestHeader(name = "X-User-Role", defaultValue = "ADMIN") String role) {
        securityGuard.requireAdmin(role);
        return new ResponseEntity<>(billingService.generateBills(request), HttpStatus.CREATED);
    }

    @PutMapping("/{id}/payment")
    public ResponseEntity<Bill> updatePayment(
            @PathVariable(name = "id") String id,
            @RequestBody BillDTO.PaymentUpdate update) {
        String status = (update.getPaymentStatus() != null) ? update.getPaymentStatus() : "PAID";
        return ResponseEntity.ok(billingService.updatePaymentStatus(id, status));
    }

    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getStatistics() {
        return ResponseEntity.ok(billingService.getBillingStatistics());
    }
}
