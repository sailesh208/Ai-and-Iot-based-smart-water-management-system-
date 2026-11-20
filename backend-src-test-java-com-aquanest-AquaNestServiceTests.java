package com.aquanest;

import com.aquanest.dto.BillDTO;
import com.aquanest.model.House;
import com.aquanest.dto.PumpControlDTO;
import com.aquanest.model.Bill;
import com.aquanest.model.LeakageAlert;
import com.aquanest.model.TankReading;
import com.aquanest.repository.DataStore;
import com.aquanest.security.SecurityGuard;
import com.aquanest.service.BillingService;
import com.aquanest.service.ConsumptionService;
import com.aquanest.service.LeakageDetectionService;
import com.aquanest.service.PumpService;
import com.aquanest.service.TankService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

public class AquaNestServiceTests {

    private DataStore dataStore;
    private TankService tankService;
    private PumpService pumpService;
    private ConsumptionService consumptionService;
    private LeakageDetectionService leakageService;
    private BillingService billingService;
    private SecurityGuard securityGuard;

    @BeforeEach
    public void setup() {
        dataStore = new DataStore();
        tankService = new TankService(dataStore);
        pumpService = new PumpService(dataStore);
        consumptionService = new ConsumptionService(dataStore);
        leakageService = new LeakageDetectionService(dataStore);
        billingService = new BillingService(dataStore);
        securityGuard = new SecurityGuard();
    }

    @Test
    @DisplayName("Test 1: Automatic pump hysteresis turns pump ON when tank <= low threshold")
    public void testPumpHysteresisLowLevel() {
        dataStore.getSettings().setLowThresholdPercent(20.0);
        dataStore.getSettings().setFullThresholdPercent(90.0);

        // Simulate tank level dropping to 19.5%
        TankReading reading = tankService.processTankReading(19.5, "JSN_SR04T");

        assertEquals("ON", reading.getPumpStatus(), "Pump should automatically turn ON when level drops to <= 20%");
        assertEquals(19.5, reading.getLevelPercent());
    }

    @Test
    @DisplayName("Test 2: Automatic pump hysteresis turns pump OFF when tank >= full threshold")
    public void testPumpHysteresisFullLevel() {
        // Set state to ON first
        dataStore.getCurrentTankReading().setPumpStatus("ON");

        // Tank level reaches 91%
        TankReading reading = tankService.processTankReading(91.0, "JSN_SR04T");

        assertEquals("OFF", reading.getPumpStatus(), "Pump should automatically turn OFF when level reaches >= 90%");
    }

    @Test
    @DisplayName("Test 3: Non-admin resident cannot manually override pump control")
    public void testResidentCannotOverridePump() {
        PumpControlDTO dto = new PumpControlDTO("START", "MANUAL");
        assertThrows(SecurityException.class, () -> {
            pumpService.controlPump(dto, "RESIDENT");
        }, "Resident user role should be rejected from manual pump operation");
    }

    @Test
    @DisplayName("Test 4: Consumption calculation handles cumulative delta and sensor resets correctly")
    public void testConsumptionIntervalAndReset() {
        // First reading at 100.0 L
        double interval1 = consumptionService.processFlowReading("H101", 3.0, 1350, 100.0);
        assertTrue(interval1 >= 0.0);

        // Second reading advances to 125.5 L (delta = 25.5 L)
        double interval2 = consumptionService.processFlowReading("H101", 4.2, 1800, 125.5);
        assertEquals(25.5, interval2, 0.01, "Delta should equal current minus previous cumulative");

        // Third reading simulates microcontroller reset (drops to 10.0 L)
        double intervalReset = consumptionService.processFlowReading("H101", 2.0, 450, 10.0);
        assertEquals(10.0, intervalReset, 0.01, "Reset reading should be accepted without negative corruption");
    }

    @Test
    @DisplayName("Test 5: Tank leakage detection flags alert when level drops with zero consumption and pump idle")
    public void testTankLeakageDetection() {
        dataStore.getCurrentTankReading().setPumpStatus("OFF");

        // Drops from 70% to 66% with zero house flow over 60 mins
        Optional<LeakageAlert> alertOpt = leakageService.evaluateTankLeakage(70.0, 66.0, 0.0, 60);

        assertTrue(alertOpt.isPresent(), "Tank leakage alert should be generated");
        assertEquals("TANK_LEAKAGE", alertOpt.get().getType());
        assertEquals(160.0, alertOpt.get().getEstimatedLossLitres(), 0.1);
    }

    @Test
    @DisplayName("Test 6: Pipe distribution mismatch triggers possible pipe leakage alert")
    public void testPipeLeakageDetection() {
        // Main flow = 20 L/min, sum of houses = 12 L/min (mismatch = 8 L/min), pressure drops to 1.6 bar
        Optional<LeakageAlert> alertOpt = leakageService.evaluatePipeLeakage(20.0, 12.0, 1.6);

        assertTrue(alertOpt.isPresent(), "Pipe leakage alert should be triggered on substantial distribution mismatch");
        assertEquals("PIPE_LEAKAGE", alertOpt.get().getType());
    }

    @Test
    @DisplayName("Test 7: Smart billing formula and immutable tariff snapshot verification")
    public void testSmartBillingCalculation() {
        BillDTO.GenerateRequest req = new BillDTO.GenerateRequest();
        req.setBillingPeriod("2026-10");
        req.setHouseId("H101");
        req.setDueDate("2026-11-10");

        dataStore.getHouseById("H101").setMonthlyUsageLitres(8500.0);
        dataStore.getSettings().setWaterTariffPerLitre(0.10);
        dataStore.getSettings().setFixedMonthlyCharge(200.0);

        List<Bill> bills = billingService.generateBills(req);
        assertEquals(1, bills.size());
        Bill b = bills.get(0);

        // Water charge = 8500 * 0.10 = 850.0
        // Total = 850.0 + 200.0 = 1050.0
        assertEquals(850.0, b.getWaterCharge(), 0.01);
        assertEquals(200.0, b.getFixedCharge(), 0.01);
        assertEquals(1050.0, b.getTotalAmount(), 0.01);
        assertEquals(0.10, b.getWaterRate());

        // Now modify global tariff to 0.25; previously generated bill MUST NOT change!
        dataStore.getSettings().setWaterTariffPerLitre(0.25);
        Bill retrieved = billingService.getBillById(b.getId());
        assertEquals(0.10, retrieved.getWaterRate(), "Historical bill tariff must remain immutable");
        assertEquals(1050.0, retrieved.getTotalAmount(), "Historical bill amount must not mutate when tariff changes");
    }

    @Test
    @DisplayName("Test 8: Resident security isolation forbids access to other houses")
    public void testResidentSecurityIsolation() {
        // Resident in H101 attempting to access H102
        assertThrows(SecurityException.class, () -> {
            securityGuard.validateHouseAccess("RESIDENT", "H101", "H102");
        }, "Resident should be forbidden from accessing another house");

        // Resident accessing own house should succeed
        assertDoesNotThrow(() -> {
            securityGuard.validateHouseAccess("RESIDENT", "H101", "H101");
        });

        // Admin accessing any house should succeed
        assertDoesNotThrow(() -> {
            securityGuard.validateHouseAccess("ADMIN", null, "H102");
        });
    }

    @Test
    @DisplayName("Test 9: Seeded apartments have unique profiles and distinct consumption")
    public void testTwentyApartmentsHaveDistinctConsumptionProfiles() {
        assertEquals(20, dataStore.getHouses().size());

        for (int apartment = 101; apartment <= 120; apartment++) {
            String houseId = "H" + apartment;
            House house = dataStore.getHouseById(houseId);
            assertNotNull(house, "Missing seeded apartment " + houseId);
            assertNotNull(dataStore.getUserById(house.getResidentId()), "Missing resident for " + houseId);
            assertEquals(String.valueOf(apartment), house.getHouseNumber());
        }

        double flat101Usage = consumptionService.getDailyConsumption(7, "H101").stream()
                .mapToDouble(point -> point.getLitres())
                .sum();
        double flat104Usage = consumptionService.getDailyConsumption(7, "H104").stream()
                .mapToDouble(point -> point.getLitres())
                .sum();
        double flat120Usage = consumptionService.getDailyConsumption(7, "H120").stream()
                .mapToDouble(point -> point.getLitres())
                .sum();

        assertNotEquals(flat101Usage, flat104Usage);
        assertNotEquals(flat101Usage, flat120Usage);
        assertEquals("ABNORMAL", dataStore.getHouseById("H104").getAnomalyStatus());
    }
}
