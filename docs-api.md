# AquaNest REST API Reference

Base Endpoint: `http://localhost:8080/api`

All endpoints accept and return `application/json`.
Role-based headers:
- `X-User-Role`: `ADMIN` or `RESIDENT`
- `X-User-HouseId`: e.g. `H101`
- `X-User-Id`: e.g. `USR_ADMIN` or `USR_RES_1`

---

## 1. Authentication (`/api/auth`)

### `POST /api/auth/login`
Authenticates a user via email and password.
```json
// Request
{
  "email": "admin@aquanest.io",
  "password": "Password123!"
}
// Response
{
  "token": "jwt-aquanest-a1b2c3d4",
  "userId": "USR_ADMIN",
  "name": "Property Admin",
  "email": "admin@aquanest.io",
  "role": "ADMIN",
  "houseId": "ALL",
  "message": "Login successful"
}
```

### `POST /api/auth/signup`
Registers a new resident account. Defaults role strictly to `RESIDENT`.
```json
// Request
{
  "name": "Rajesh Sharma",
  "email": "rajesh@aquanest.io",
  "phone": "+91 98765 00001",
  "password": "SecurePassword123!",
  "confirmPassword": "SecurePassword123!",
  "houseNumber": "101"
}
```

---

## 2. Dashboard (`/api/dashboard`)

### `GET /api/dashboard/summary`
Returns system-wide KPI summary metrics for the Admin dashboard.
```json
{
  "tankLevelPercent": 72.5,
  "tankLitres": 2900.0,
  "tankCapacityLitres": 4000.0,
  "tankStatus": "OPTIMAL",
  "pumpStatus": "OFF",
  "pumpMode": "AUTO",
  "todayConsumptionLitres": 1850.0,
  "totalHouses": 6,
  "activeAlertsCount": 2,
  "monthlyConsumptionLitres": 45600.0,
  "unexplainedLossLitres": 98.0,
  "mainSuppliedLitres": 1948.0,
  "distributionMismatchPercent": 5.0,
  "currentPressureBar": 2.74,
  "systemHealth": "HEALTHY",
  "lastUpdated": "2026-09-18T12:00:00Z"
}
```

---

## 3. Overhead Tank (`/api/tank`)

- `GET /api/tank/current`: Latest level %, stored litres, and fill/empty rates.
- `GET /api/tank/history`: Past 24-hour time-series depth readings.
- `GET /api/tank/statistics`: Capacity, thresholds, and estimated minutes to full/empty.

---

## 4. Water Pump Automation (`/api/pump`)

- `GET /api/pump/status`: Current state, mode, thresholds, runtime today/week, and activations.
- `POST /api/pump/control`: Trigger manual pump override (Admin role required).
  ```json
  // Request
  {
    "command": "START",
    "mode": "MANUAL"
  }
  ```
- `GET /api/pump/logs`: Full historical audit log of pump activations.

---

## 5. Apartments & Consumption (`/api/houses` & `/api/consumption`)

- `GET /api/houses`: List all active apartment units (Residents strictly isolated to own unit).
- `POST /api/houses`: Provision a new apartment unit with digital meter (Admin only).
- `GET /api/consumption/summary`: Aggregate balance of main supply vs house consumption.
- `GET /api/consumption/hourly?houseId={id}`: 24-hour diurnal usage profile.
- `GET /api/consumption/daily?days=14&houseId={id}`: Daily usage history.
- `GET /api/consumption/weekly?houseId={id}`: Weekly volume aggregation.
- `GET /api/consumption/monthly?houseId={id}`: 6-month historical volume.

---

## 6. Leakage Diagnostics (`/api/leakage`)

- `GET /api/leakage`: All active and historical leakage alerts.
- `GET /api/leakage/tank`: Filtered tank seepage alerts.
- `GET /api/leakage/pipe`: Filtered distribution pipe mismatch alerts.
- `GET /api/leakage/statistics`: Active leak count, total loss volume, and line pressure.

---

## 7. AI Anomaly Detection & Forecasts (`/api/ai`)

- `GET /api/ai/anomalies`: Isolation Forest scored anomalies with explanations and recommendations.
- `GET /api/ai/forecast?houseId=ALL`: 7-day demand predictions with 95% confidence bounds.
- `GET /api/ai/recommendations`: Contextual, actionable water conservation advice.

---

## 8. Smart Billing (`/api/bills`)

- `GET /api/bills`: List all monthly water bills.
- `GET /api/bills/house/{houseId}`: Invoices for a specific apartment.
- `POST /api/bills/generate`: Batch generate invoices with immutable tariff snapshot.
- `PUT /api/bills/{id}/payment`: Update payment settlement status (`PAID`).
