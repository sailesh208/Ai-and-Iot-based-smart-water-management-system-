# AquaNest Deployment and Execution Guide

## Quick Local Run

AquaNest is pre-configured with autonomous simulation mode (`DATA_MODE=SIMULATION`), allowing the entire stack to run locally out of the box.

---

### Step 1: Run Backend Tests
Verify Java business logic (hysteresis pump control, consumption calculation, leakage detection, smart billing, and security guard):
```bash
cd c:\jr\aquanest\backend
C:\jr\tools\apache-maven-3.9.6\bin\mvn.cmd test
```

### Step 2: Start Java Spring Boot Backend
```bash
cd c:\jr\aquanest\backend
C:\jr\tools\apache-maven-3.9.6\bin\mvn.cmd spring-boot:run
```
The REST API server will start on `http://localhost:8080`.

### Step 3: Run AI Model Tests & Training
```bash
cd c:\jr\aquanest\ai
python -m pytest test_ai.py -v
python training/train_models.py
```

### Step 4: Launch Python Streamlit Dashboard
```bash
cd c:\jr\aquanest\dashboard
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## Evaluation Profiles

| Role | Email | Password | Access Rights |
|---|---|---|---|
| **Property Administrator** | `admin@aquanest.io` | *Any* | Full access: all units, pump control, tariffs, bills, leakage diagnostics |
| **Resident (Flat 101)** | `rajesh@aquanest.io` | *Any* | Strictly personal: Flat 101 telemetry, current bill, personal water tips |
| **Resident (Flat 104 - Leak)** | `sneha@aquanest.io` | *Any* | Flat 104 with active AI nocturnal leak alert & fixture inspection tip |
