# AquaNest – Smart Apartment Water Management System

AquaNest is a complete, production-grade AI + IoT smart water-management platform built specifically for apartment complexes. It integrates edge sensing, MQTT communication, a central Java Spring Boot 3 business engine, Firebase Cloud Firestore, Scikit-Learn machine learning, and an interactive Python Streamlit dashboard.

---

## 🌟 Key Highlights & Capabilities

1. **Smart Overhead Tank Monitoring:** Continuous depth sensing with waterproof JSN-SR04T ultrasonic sensor, volumetric litre conversion, fill/empty rate velocity, and estimated minutes to full/empty.
2. **Automatic Hysteresis Pump Control:** Prevents contactor chatter with dual-threshold hysteresis (LOW $\le 20\%$ turns pump ON, FULL $\ge 90\%$ turns pump OFF). Includes manual override with strict Admin authorization.
3. **Multi-tier Leakage Detection:**
   - *Tank Leakage:* Detected when pump is idle and house meters read zero, yet tank level steadily drops.
   - *Pipe Distribution Leakage:* Detected via main supply vs house meter volume mismatch ($> 5\%$ tolerance) and distribution line pressure drops.
4. **House-Wise Volumetric Metering:** Digital hall-effect pulse meters measuring hourly, daily, weekly, and monthly consumption for every flat.
5. **AI Anomaly Detection:** Scikit-Learn `IsolationForest` detecting nocturnal continuous toilet flapper leaks, sudden spikes, and atypical usage profiles with human-readable explanations.
6. **Time-Series Demand Prediction:** Forward-looking regression model projecting 7-day demand with 95% confidence bands and morning surge peak periods.
7. **Transparent Smart Billing:** Formula-based invoicing:
   $$\text{Final Bill} = (\text{Monthly Litres} \times \text{Water Rate}) + \text{Fixed Maintenance Charge}$$
   Tariff snapshots are immutable at generation time.
8. **Role-Based Access Control:**
   - **Admin:** Full apartment oversight, manual pump controls, tariff configuration, all bills, system settings.
   - **Resident:** Strictly isolated to their own flat's telemetry, current invoice, and water-saving advice.
9. **Modern AquaNest Visual Theme:** Dark blue sidebar (`#0A2540`), water accents (`#00A8E8`), rounded cards, status badges, and 4–5 Plotly graphs on every major analytics page.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend / Dashboard** | Python 3.12, Streamlit 1.51, Plotly 6.4 |
| **Backend Business Engine** | Java 17, Spring Boot 3.2.3, Maven, REST API |
| **Messaging & IoT Protocol** | Eclipse Paho MQTT v3.1.1 (HiveMQ / Mosquitto) |
| **Database & Auth** | Firebase Cloud Firestore & Firebase Authentication |
| **AI / Machine Learning** | Python, Pandas, NumPy, Scikit-Learn (`IsolationForest`, Ridge Regression) |
| **IoT Hardware Firmware** | ESP32, Arduino C++, JSN-SR04T, Flow Meters, Contactor Relay |

---

## 📁 Project Structure

```
aquanest/
├── backend/                  # Java Spring Boot 3 Business Core
│   ├── pom.xml               # Maven dependencies & plugins
│   ├── src/main/java/com/aquanest/
│   │   ├── AquaNestApplication.java
│   │   ├── controller/       # REST API Controllers (13 endpoints)
│   │   ├── service/          # Flow, Pump, Tank, Leakage, Billing engines
│   │   ├── model/            # User, House, Sensor, Bill, TankReading, etc.
│   │   ├── dto/              # Request/Response data transfer objects
│   │   ├── repository/       # DataStore & Firestore adapters
│   │   ├── security/         # Role-based authorization & resident isolation
│   │   └── mqtt/             # Paho MQTT subscriber/publisher
│   └── src/test/java/        # JUnit 5 test suite
│
├── dashboard/                # Python Streamlit Frontend
│   ├── app.py                # Main application & routing router
│   ├── views/                # 15 views (Home, Dashboard, Tank, Pump, etc.)
│   ├── components/           # Plotly chart builders & KPI cards
│   ├── services/             # REST API client with fallback
│   ├── utils/                # Theme CSS injection & Plotly styling
│   └── requirements.txt
│
├── ai/                       # Machine Learning Pipeline
│   ├── anomaly/              # Isolation Forest anomaly detector
│   ├── forecasting/          # Time-series demand forecaster
│   ├── recommendations/      # Actionable water-saving tips engine
│   ├── training/             # Synthetic telemetry generator & model exporter
│   ├── models/               # Serialized .joblib model files
│   └── test_ai.py            # Pytest test suite
│
├── esp32/                    # Microcontroller Firmware & Simulator
│   ├── src/                  # main.cpp, config.h
│   ├── sensors/              # JSN-SR04T ultrasonic & pulse flow drivers
│   ├── pump/                 # Optocoupled relay controller with watchdog
│   └── simulation/           # Python telemetry simulator script
│
├── docs/                     # Technical Documentation
│   ├── architecture.md
│   ├── api.md
│   ├── mqtt.md
│   ├── firebase.md
│   ├── hardware.md
│   └── deployment.md
│
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Open and Run This Project Later

The project files and generated telemetry dataset are saved under:
`C:\Users\vikra\Downloads\nest\nest\jr\aquanest`

Open that **aquanest** folder in VS Code. The dashboard and backend are separate processes, so open two terminals at the project root.

### Start the Java backend (Terminal 1)
```powershell
Set-Location .\backend
& ..\..\tools\apache-maven-3.9.6\bin\mvn.cmd spring-boot:run
```

### Start the Python dashboard (Terminal 2)
```powershell
Set-Location .\dashboard
python -m streamlit run app.py
```

Open `http://localhost:8501`. If Python reports a missing package on a new setup, install dashboard dependencies once:
```powershell
python -m pip install -r requirements.txt
```
The project requires Python 3.12 and Java 17.

### Run the tests
From the project root, run the Python tests:
```powershell
python -m unittest discover -s dashboard\tests -v
```

For the Java tests:
```powershell
Set-Location .\backend
& ..\..\tools\apache-maven-3.9.6\bin\mvn.cmd test
```
The Java tests cover pump hysteresis, consumption, leakage, billing, security isolation, and all 20 apartment profiles.

Pump status is shared across the Admin Dashboard, Pump Control, and Tank Monitoring pages. If the REST backend is unavailable, pump actions update a clearly labeled local demo state for the current Streamlit session only; physical hardware requires a running backend and connected controller.

Water-consumption demo charts use separate, repeatable hourly, daily, weekly, and monthly profiles for all 20 apartments (H101–H120). Resident views are restricted to the signed-in apartment, while administrators can compare apartments or view the building total. Use the resident demo selector to open each apartment profile; the demo readings are synthetic.

### Collect or Enter Telemetry Data
Administrators can open **Administration → Data Collection** to enter readings in an editable table, import a CSV, or generate 7-, 30-, or 90-day synthetic apartment telemetry. Records are validated and saved to `exports/aquanest_telemetry_dataset.csv`. The included 30-day sample has 14,400 synthetic readings for apartments H101–H120. The dataset columns are `timestamp`, `house_id`, `litres`, `rolling_mean_24h`, `continuous_night_hours`, and `source`.

---

## 🔐 Evaluation Login Profiles

- **Administrator demo:** Click *"👑 Admin Portal"*.
- **Resident demos:** On the Login page, choose any of the 20 apartments from the **Demo Resident** selector.
- **Firebase accounts:** Email/password sign-in requires Firebase Authentication and a matching AquaNest Firestore profile. The demo selector works without Firebase credentials.
- **Resident with Leak:** Choose Sneha Patel (Flat 104) to demonstrate the synthetic high-use/leak profile.
