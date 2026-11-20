package com.aquanest.repository;

import com.aquanest.model.*;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Thread-safe central data store providing seamless unified access
 * to Firestore-modeled collections with initial realistic demo telemetry.
 */
@Repository
public class DataStore {

    private final Map<String, User> users = new ConcurrentHashMap<>();
    private final Map<String, House> houses = new ConcurrentHashMap<>();
    private final Map<String, Sensor> sensors = new ConcurrentHashMap<>();
    private final List<TankReading> tankReadings = new CopyOnWriteArrayList<>();
    private final List<FlowReading> flowReadings = new CopyOnWriteArrayList<>();
    private final List<ConsumptionRecord> consumptionRecords = new CopyOnWriteArrayList<>();
    private final Map<String, Bill> bills = new ConcurrentHashMap<>();
    private final List<PumpLog> pumpLogs = new CopyOnWriteArrayList<>();
    private final List<LeakageAlert> leakageAlerts = new CopyOnWriteArrayList<>();
    private final List<Alert> alerts = new CopyOnWriteArrayList<>();
    private final List<AiAnomaly> anomalies = new CopyOnWriteArrayList<>();
    private final List<AiForecast> forecasts = new CopyOnWriteArrayList<>();
    private final List<Recommendation> recommendations = new CopyOnWriteArrayList<>();
    private SystemSettings settings = new SystemSettings();

    private TankReading currentTankReading;
    private double currentPressureBar = 2.75;

    public DataStore() {
        seedInitialDemoData();
    }

    private void seedInitialDemoData() {
        // 1. Users
        User admin = new User("USR_ADMIN", "Property Admin", "admin@aquanest.io", "+91 98765 43210", "ADMIN", "ALL");
        users.put(admin.getUserId(), admin);

        String[] residentNames = {
            "Rajesh Sharma", "Priya Venkatesh", "Arun Kumar", "Sneha Patel",
            "Vikram Malhotra", "Ananya Reddy", "Aditi Rao", "Kabir Mehta",
            "Meera Nair", "Rohan Das", "Isha Kapoor", "Neel Shah",
            "Kavya Iyer", "Dev Malhotra", "Tara Menon", "Aarav Gupta",
            "Diya Bose", "Samir Joshi", "Nisha Kulkarni", "Aditya Verma"
        };
        String[] emails = {
            "rajesh@aquanest.io", "priya@aquanest.io", "arun@aquanest.io", "sneha@aquanest.io",
            "vikram@aquanest.io", "ananya@aquanest.io", "resident107@aquanest.test", "resident108@aquanest.test",
            "resident109@aquanest.test", "resident110@aquanest.test", "resident111@aquanest.test", "resident112@aquanest.test",
            "resident113@aquanest.test", "resident114@aquanest.test", "resident115@aquanest.test", "resident116@aquanest.test",
            "resident117@aquanest.test", "resident118@aquanest.test", "resident119@aquanest.test", "resident120@aquanest.test"
        };
        double[] dailyUsageLitres = {
            230.0, 260.0, 290.0, 850.0, 320.0, 350.0, 380.0, 410.0, 440.0, 470.0,
            500.0, 530.0, 560.0, 590.0, 620.0, 650.0, 680.0, 710.0, 740.0, 770.0
        };

        // 2. Houses (H101 - H120)
        for (int i = 1; i <= residentNames.length; i++) {
            String hId = "H" + (100 + i);
            String uId = "USR_RES_" + i;
            User resident = new User(uId, residentNames[i - 1], emails[i - 1], "DEMO-" + i, "RESIDENT", hId);
            users.put(uId, resident);

            int floor = ((i - 1) / 4) + 1;
            House house = new House(hId, String.valueOf(100 + i), floor, uId, residentNames[i - 1], "METER_" + hId);
            double todayBase = dailyUsageLitres[i - 1];
            double monthBase = todayBase * 24.5;
            house.setCurrentUsageLitres(1.2 + (i * 0.3));
            house.setTodayUsageLitres(todayBase);
            house.setMonthlyUsageLitres(monthBase);
            house.setAverageDailyLitres(todayBase * 0.95);
            house.setPeakUsageLitres(todayBase * 0.22);
            if (hId.equals("H104")) {
                house.setAnomalyStatus("ABNORMAL");
            }
            houses.put(hId, house);

            // Flow sensor for house
            Sensor flowSensor = new Sensor("FLOW_" + hId, "FLOW_HOUSE", hId, 450.0, "L/min");
            flowSensor.setLastReading(house.getCurrentUsageLitres());
            sensors.put(flowSensor.getSensorId(), flowSensor);
        }

        // 3. Main Infrastructure Sensors
        Sensor tankSensor = new Sensor("JSN_SR04T_01", "ULTRASONIC", "MAIN_TANK", 1.0, "%");
        tankSensor.setLastReading(72.0);
        sensors.put(tankSensor.getSensorId(), tankSensor);

        Sensor mainFlowSensor = new Sensor("FLOW_MAIN_01", "FLOW_MAIN", "MAIN", 450.0, "L/min");
        mainFlowSensor.setLastReading(12.5);
        sensors.put(mainFlowSensor.getSensorId(), mainFlowSensor);

        Sensor pressureSensor = new Sensor("PRESSURE_01", "PRESSURE", "DISTRIBUTION", 1.0, "bar");
        pressureSensor.setLastReading(2.75);
        sensors.put(pressureSensor.getSensorId(), pressureSensor);

        // 4. Overhead Tank Readings (Current & 24h History)
        Instant now = Instant.now();
        currentTankReading = new TankReading("TR_NOW", 72.5, 2900.0, 4000.0, "OFF");
        currentTankReading.setPumpMode("AUTO");
        currentTankReading.setFillRateLpm(0.0);
        currentTankReading.setEmptyRateLpm(8.4);
        currentTankReading.setEstimatedTimeToFullMinutes(0.0);
        currentTankReading.setEstimatedTimeToEmptyMinutes(250.0);
        currentTankReading.setSensorId("JSN_SR04T_01");

        // Generate past 24 hours tank curve
        for (int h = 24; h >= 0; h--) {
            Instant t = now.minus(h, ChronoUnit.HOURS);
            // Sine-wave pattern representing daily pump on/off cycles
            double pct = 50.0 + 35.0 * Math.sin((24 - h) * 0.35);
            pct = Math.max(18.0, Math.min(92.0, pct));
            double litres = (pct / 100.0) * 4000.0;
            String pStatus = (pct <= 22.0 || (pct < 85.0 && h % 6 < 2)) ? "ON" : "OFF";
            TankReading r = new TankReading("TR_" + h, Math.round(pct * 10.0) / 10.0, Math.round(litres), 4000.0, pStatus);
            r.setTimestamp(t);
            tankReadings.add(r);
        }

        // 5. Pump Logs
        pumpLogs.add(new PumpLog("PL_1", "ON", "AUTO", 19.5, now.minus(18, ChronoUnit.HOURS), "LOW_LEVEL_AUTO"));
        PumpLog pl1 = pumpLogs.get(0);
        pl1.setEndTime(now.minus(17, ChronoUnit.HOURS).minus(15, ChronoUnit.MINUTES));
        pl1.setDurationSeconds(2700);

        pumpLogs.add(new PumpLog("PL_2", "ON", "AUTO", 20.0, now.minus(8, ChronoUnit.HOURS), "LOW_LEVEL_AUTO"));
        PumpLog pl2 = pumpLogs.get(1);
        pl2.setEndTime(now.minus(7, ChronoUnit.HOURS).minus(20, ChronoUnit.MINUTES));
        pl2.setDurationSeconds(2400);

        // 6. Bills for Previous & Current Month
        String[] periods = {"2026-08", "2026-09"};
        for (String period : periods) {
            for (House h : houses.values()) {
                double consumption = period.equals("2026-08") ? (h.getMonthlyUsageLitres() * 0.96) : h.getMonthlyUsageLitres();
                consumption = Math.round(consumption);
                String billId = "BILL_" + period.replace("-", "") + "_" + h.getHouseId();
                String dueDate = period.equals("2026-08") ? "2026-09-10" : "2026-10-10";
                Bill b = new Bill(billId, h.getHouseId(), h.getHouseNumber(), h.getResidentName(),
                        period, consumption, settings.getWaterTariffPerLitre(), settings.getFixedMonthlyCharge(), dueDate);
                if (period.equals("2026-08")) {
                    b.setPaymentStatus("PAID");
                    b.setPaidAt(now.minus(10, ChronoUnit.DAYS));
                } else {
                    b.setPaymentStatus(h.getHouseId().equals("H103") ? "PENDING" : (h.getHouseId().equals("H105") ? "OVERDUE" : "PAID"));
                }
                bills.put(b.getId(), b);
            }
        }

        // 7. Leakage Alerts (1 Tank, 1 Pipe for realistic demonstration)
        LeakageAlert tankLeak = new LeakageAlert(
                "LKG_TANK_01", "TANK_LEAKAGE", "MAIN", "Overhead Tank Zone",
                145.0, "WARNING",
                "Pump OFF and distribution outflow is 0.0 L/min, but tank level reduced by 3.6% over 120 minutes.",
                2.70, 1.2
        );
        tankLeak.setStatus("INVESTIGATING");
        leakageAlerts.add(tankLeak);

        LeakageAlert pipeLeak = new LeakageAlert(
                "LKG_PIPE_01", "PIPE_LEAKAGE", "DISTRIBUTION", "Main Distribution Pipe - Wing B",
                380.0, "POSSIBLE_LEAK",
                "Main flow meter recorded 18.5 L/min while sum of active house meters was 11.2 L/min (Mismatch > 39%), with 0.6 bar drop.",
                2.15, 7.3
        );
        pipeLeak.setStatus("NEW");
        leakageAlerts.add(pipeLeak);

        // 8. Alerts
        alerts.add(new Alert("ALT_1", "PIPE_LEAKAGE", "CRITICAL", "DISTRIBUTION", "Distribution mismatch detected: 7.3 L/min unexplained loss in Wing B."));
        alerts.add(new Alert("ALT_2", "ABNORMAL_CONSUMPTION", "WARNING", "H104", "House 104 abnormal usage: 4.5 hours continuous nocturnal flow detected."));
        alerts.add(new Alert("ALT_3", "TANK_LEAKAGE", "WARNING", "MAIN", "Possible tank leakage detected: Unexplained 145 L drop while pump was idle."));
        alerts.add(new Alert("ALT_4", "PUMP", "INFO", "ALL", "Automatic pump cycle completed. Overhead tank replenished to 88.5%."));

        // 9. AI Anomalies (Demonstrating Isolation Forest outputs)
        anomalies.add(new AiAnomaly("ANOM_1", "H104", 120.0, 540.0, 0.88,
                "Continuous 4-hour nocturnal flow detected between 01:00 and 05:00 without decay.",
                "Inspect master bathroom flush valve, flapper seal, and concealed pipe runs in H104."));
        anomalies.add(new AiAnomaly("ANOM_2", "H102", 310.0, 680.0, 0.74,
                "Sudden peak usage spike exceeding 2.2x the 30-day baseline during afternoon hours.",
                "Confirm if high-capacity appliances (e.g. pressure washer) or open garden tap were operating."));

        // 10. AI Demand Forecasts (7-day forecast)
        LocalDate today = LocalDate.now();
        double baseApartmentDemand = 4200.0;
        for (int d = 0; d < 7; d++) {
            LocalDate fDate = today.plusDays(d);
            double dayFactor = (fDate.getDayOfWeek().getValue() >= 6) ? 1.25 : 0.98; // weekend higher demand
            double pred = Math.round(baseApartmentDemand * dayFactor);
            AiForecast f = new AiForecast("FC_" + d, "ALL", fDate, pred, Math.round(pred * 0.92), Math.round(pred * 1.08), "07:00 - 09:30");
            if (d == 0) {
                f.setActualLitres(4150.0);
            }
            forecasts.add(f);
        }

        // 11. Recommendations
        recommendations.add(new Recommendation("REC_1", "ADMIN", "ALL", "Overhead Tank Inspection",
                "Schedule a physical inspection of overhead tank float seal; slow seepage of ~1.2 L/min observed during idle hours.",
                "LEAK_PREVENTION", "HIGH"));
        recommendations.add(new Recommendation("REC_2", "RESIDENT", "H104", "Check Toilet Fixtures in Flat 104",
                "Your apartment logged 540 L nocturnal consumption. A leaking toilet flapper can waste up to 400 L/day silently.",
                "WATER_SAVING", "HIGH"));
        recommendations.add(new Recommendation("REC_3", "ALL", "ALL", "Weekend Peak Demand Shift",
                "Apartment demand surges by 28% on Saturday mornings. Staggering washing machine cycles helps maintain optimal pipe pressure.",
                "PRESSURE_EFFICIENCY", "MEDIUM"));
        recommendations.add(new Recommendation("REC_4", "ADMIN", "ALL", "Pump Hysteresis Optimization",
                "Adjusting low threshold to 25% during morning hours can prevent pump short-cycling and extend contactor lifespan.",
                "BILLING_OPTIMIZATION", "LOW"));
    }

    // Accessors for Collections
    public Map<String, User> getUsers() { return users; }
    public Map<String, House> getHouses() { return houses; }
    public Map<String, Sensor> getSensors() { return sensors; }
    public List<TankReading> getTankReadings() { return tankReadings; }
    public List<FlowReading> getFlowReadings() { return flowReadings; }
    public List<ConsumptionRecord> getConsumptionRecords() { return consumptionRecords; }
    public Map<String, Bill> getBills() { return bills; }
    public List<PumpLog> getPumpLogs() { return pumpLogs; }
    public List<LeakageAlert> getLeakageAlerts() { return leakageAlerts; }
    public List<Alert> getAlerts() { return alerts; }
    public List<AiAnomaly> getAnomalies() { return anomalies; }
    public List<AiForecast> getForecasts() { return forecasts; }
    public List<Recommendation> getRecommendations() { return recommendations; }

    public SystemSettings getSettings() { return settings; }
    public void setSettings(SystemSettings settings) { this.settings = settings; }

    public TankReading getCurrentTankReading() { return currentTankReading; }
    public void setCurrentTankReading(TankReading currentTankReading) {
        this.currentTankReading = currentTankReading;
        this.tankReadings.add(currentTankReading);
    }

    public double getCurrentPressureBar() { return currentPressureBar; }
    public void setCurrentPressureBar(double currentPressureBar) { this.currentPressureBar = currentPressureBar; }

    public House getHouseById(String houseId) {
        return houses.get(houseId);
    }

    public User getUserByEmail(String email) {
        return users.values().stream()
                .filter(u -> u.getEmail().equalsIgnoreCase(email))
                .findFirst()
                .orElse(null);
    }

    public User getUserById(String userId) {
        return users.get(userId);
    }

    public void saveUser(User user) {
        users.put(user.getUserId(), user);
    }

    public void saveHouse(House house) {
        houses.put(house.getHouseId(), house);
    }

    public void deleteHouse(String houseId) {
        House h = houses.get(houseId);
        if (h != null) {
            h.setStatus("INACTIVE"); // Safe deactivation preserving history
        }
    }

    public void saveBill(Bill bill) {
        bills.put(bill.getId(), bill);
    }

    public void addAlert(Alert alert) {
        alerts.add(0, alert);
    }

    public void addPumpLog(PumpLog log) {
        pumpLogs.add(0, log);
    }

    public void addLeakageAlert(LeakageAlert alert) {
        leakageAlerts.add(0, alert);
    }
}
