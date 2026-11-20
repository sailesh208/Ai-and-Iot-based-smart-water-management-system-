package com.aquanest.service;

import com.aquanest.dto.BillDTO;
import com.aquanest.model.Bill;
import com.aquanest.model.House;
import com.aquanest.model.SystemSettings;
import com.aquanest.repository.DataStore;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class BillingService {

    private final DataStore dataStore;

    public BillingService(DataStore dataStore) {
        this.dataStore = dataStore;
    }

    public List<Bill> getAllBills() {
        return new ArrayList<>(dataStore.getBills().values());
    }

    public Bill getBillById(String billId) {
        Bill bill = dataStore.getBills().get(billId);
        if (bill == null) {
            throw new NoSuchElementException("Bill with ID " + billId + " was not found.");
        }
        return bill;
    }

    public List<Bill> getBillsByHouseId(String houseId) {
        return dataStore.getBills().values().stream()
                .filter(b -> b.getHouseId().equalsIgnoreCase(houseId))
                .sorted(Comparator.comparing(Bill::getBillingPeriod).reversed())
                .collect(Collectors.toList());
    }

    public List<Bill> getBillsByMonth(String month) {
        return dataStore.getBills().values().stream()
                .filter(b -> b.getBillingPeriod().equalsIgnoreCase(month))
                .collect(Collectors.toList());
    }

    /**
     * Generates house-wise monthly water bills using immutable tariff snapshot.
     */
    public synchronized List<Bill> generateBills(BillDTO.GenerateRequest request) {
        SystemSettings settings = dataStore.getSettings();
        double currentWaterRate = settings.getWaterTariffPerLitre();
        double currentFixedCharge = settings.getFixedMonthlyCharge();

        String period = (request.getBillingPeriod() != null && !request.getBillingPeriod().isBlank())
                ? request.getBillingPeriod()
                : LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM"));

        String dueDate = (request.getDueDate() != null && !request.getDueDate().isBlank())
                ? request.getDueDate()
                : LocalDate.now().plusDays(settings.getBillingDueDays()).toString();

        List<Bill> generated = new ArrayList<>();
        Collection<House> targetHouses;

        if (request.getHouseId() != null && !request.getHouseId().isBlank()) {
            House single = dataStore.getHouseById(request.getHouseId());
            targetHouses = (single != null) ? List.of(single) : Collections.emptyList();
        } else {
            targetHouses = dataStore.getHouses().values();
        }

        for (House h : targetHouses) {
            String billId = "BILL_" + period.replace("-", "") + "_" + h.getHouseId();
            double consumption = Math.round(h.getMonthlyUsageLitres());

            // Create bill with immutable tariff snapshot
            Bill bill = new Bill(billId, h.getHouseId(), h.getHouseNumber(), h.getResidentName(),
                    period, consumption, currentWaterRate, currentFixedCharge, dueDate);

            dataStore.saveBill(bill);
            generated.add(bill);
        }

        return generated;
    }

    public Bill updatePaymentStatus(String billId, String paymentStatus) {
        Bill bill = getBillById(billId);
        bill.setPaymentStatus(paymentStatus.toUpperCase());
        if ("PAID".equalsIgnoreCase(paymentStatus)) {
            bill.setPaidAt(java.time.Instant.now());
        }
        return bill;
    }

    public Map<String, Object> getBillingStatistics() {
        double totalBilled = dataStore.getBills().values().stream().mapToDouble(Bill::getTotalAmount).sum();
        double totalCollected = dataStore.getBills().values().stream()
                .filter(b -> "PAID".equalsIgnoreCase(b.getPaymentStatus()))
                .mapToDouble(Bill::getTotalAmount).sum();
        double totalPending = totalBilled - totalCollected;
        double totalConsumptionLitres = dataStore.getBills().values().stream().mapToDouble(Bill::getConsumptionLitres).sum();

        Map<String, Object> stats = new HashMap<>();
        stats.put("totalBilledAmount", Math.round(totalBilled * 100.0) / 100.0);
        stats.put("totalCollectedAmount", Math.round(totalCollected * 100.0) / 100.0);
        stats.put("totalPendingAmount", Math.round(totalPending * 100.0) / 100.0);
        stats.put("totalBilledConsumptionLitres", Math.round(totalConsumptionLitres));
        stats.put("currentTariffPerLitre", dataStore.getSettings().getWaterTariffPerLitre());
        stats.put("currentFixedMonthlyCharge", dataStore.getSettings().getFixedMonthlyCharge());
        stats.put("billingCycle", dataStore.getSettings().getBillingCycle());

        return stats;
    }
}
