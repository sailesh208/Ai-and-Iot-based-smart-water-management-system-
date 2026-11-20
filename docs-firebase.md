# AquaNest Firebase Cloud Firestore & Authentication Guide

## 1. Firebase Authentication
- **Provider:** Email & Password authentication.
- **Role Enforcement:** User roles (`ADMIN` or `RESIDENT`) are mapped in the `users/{userId}` Firestore document.
- **Security Rule:** Public registration strictly maps new accounts to `RESIDENT`. Only administrative workflows can grant `ADMIN` role.

---

## 2. Cloud Firestore Schema

### Collection: `users/{userId}`
```json
{
  "userId": "USR_RES_1",
  "name": "Rajesh Sharma",
  "email": "rajesh@aquanest.io",
  "phone": "+91 98765 00001",
  "role": "RESIDENT",
  "houseId": "H101",
  "status": "ACTIVE",
  "createdAt": "2026-09-01T00:00:00Z"
}
```

### Collection: `houses/{houseId}`
```json
{
  "houseId": "H101",
  "houseNumber": "101",
  "floor": 1,
  "residentId": "USR_RES_1",
  "residentName": "Rajesh Sharma",
  "meterId": "METER_H101",
  "status": "ACTIVE",
  "currentUsageLitres": 2.1,
  "todayUsageLitres": 280.0,
  "monthlyUsageLitres": 7200.0,
  "averageDailyLitres": 290.0,
  "peakUsageLitres": 65.0,
  "anomalyStatus": "NORMAL",
  "lastUpdated": "2026-09-18T12:00:00Z"
}
```

### Collection: `tank_readings/{readingId}`
```json
{
  "timestamp": "2026-09-18T12:00:00Z",
  "levelPercent": 72.5,
  "waterLitres": 2900.0,
  "capacityLitres": 4000.0,
  "sensorId": "JSN_SR04T_01",
  "pumpStatus": "OFF",
  "pumpMode": "AUTO"
}
```

### Collection: `bills/{billId}`
```json
{
  "id": "BILL_202609_H101",
  "houseId": "H101",
  "billingPeriod": "2026-09",
  "consumptionLitres": 7200.0,
  "waterRate": 0.10,
  "waterCharge": 720.0,
  "fixedCharge": 200.0,
  "totalAmount": 920.0,
  "generatedAt": "2026-09-18T12:00:00Z",
  "dueDate": "2026-10-10",
  "paymentStatus": "PAID"
}
```

### Collection: `pump_logs/{logId}`
```json
{
  "id": "PL_1",
  "status": "ON",
  "mode": "AUTO",
  "tankLevel": 19.5,
  "startTime": "2026-09-18T04:00:00Z",
  "endTime": "2026-09-18T04:40:00Z",
  "durationSeconds": 2400,
  "trigger": "LOW_LEVEL_AUTO"
}
```

### Collection: `leakage_alerts/{alertId}`
```json
{
  "id": "LKG_PIPE_01",
  "type": "PIPE_LEAKAGE",
  "zone": "Main Distribution Pipe - Wing B",
  "estimatedLossLitres": 380.0,
  "severity": "POSSIBLE_LEAK",
  "evidence": "Main flow (18.5 L/min) exceeded house sum (11.2 L/min) with 0.6 bar pressure drop.",
  "status": "NEW"
}
```

---

## 3. Autonomous Simulation Mode
When running in local evaluation mode (`DATA_MODE=SIMULATION`), the Java backend uses a thread-safe in-memory adapter that exactly mirrors this Firestore collection structure and persists states during runtime without requiring third-party credentials.
