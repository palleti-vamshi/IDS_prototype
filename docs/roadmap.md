# LightX-IDS — Project Roadmap

## 1. Overview

The LightX-IDS roadmap defines the planned progression of the project from industrial environment simulation through dataset generation, machine learning, real-time intrusion detection, dashboard integration, and deployment.

The roadmap is based on the currently implemented project structure and the defined project phases.

## 2. Completed / Implemented Work

### Phase 0 — Project Planning
- Project objectives and scope defined.
- Project phases established.
- Documentation structure created.

### Phase 1 — Industrial Environment
- Industrial IoT factory simulation implemented.
- MQTT-based communication implemented.
- Sensor simulation implemented.
- Temperature and pressure sensor data generated.

### Phase 2 — Attack Framework
- Attack framework implemented.
- DoS attack implemented.
- Replay attack implemented.
- Injection attack implemented.
- Spoofing attack implemented.
- Attack management and execution implemented.
- Dynamic attack runner implemented.

### Phase 3 — Dataset Generation
- MQTT traffic collector implemented.
- Message parser implemented.
- Attack-aware labeling implemented.
- Dataset writer implemented.
- CSV exporter implemented.
- Dataset manager implemented.
- Dataset pipeline implemented.
- Automatic dataset generation implemented.
- Normal traffic, attacks, and cooldown periods are dynamically controlled.
- Generated datasets are available in 1K, 10K, and 100K record versions.

### Dataset Engineering
- TON-IoT datasets collected for:
  - Modbus
  - Thermostat
  - Weather
  - Network
- Dataset profiling implemented.
- Dataset cleaning implemented.
- Dataset standardization implemented.
- Standardized datasets combined into a common dataset.

### Phase 7 — Frontend
- React frontend implemented.
- Vite project configured.
- Tailwind CSS integrated.
- React Router configured.
- Dashboard implemented.
- Sensors page implemented.
- Attack Monitoring page implemented.
- IDS Prediction page implemented.
- Dataset Analytics page implemented.
- System Logs page implemented.
- Settings page implemented.
- Login page implemented.
- Production build successfully generated.

## 3. Current / Next Development Stages

### Phase 4 — Machine Learning

The machine-learning implementation has not yet been provided in the current project contents.

Planned work based on the existing project phases:

- Prepare generated and standardized datasets for model training.
- Train intrusion-detection models.
- Evaluate trained models.
- Compare model performance.
- Integrate the selected model with the IDS prediction workflow.

Detailed model names, algorithms, training configuration, and evaluation results cannot be specified until the corresponding implementation is available.

### Phase 5 — Reducing False Positives

The project phase plan includes reducing false positives after the initial machine-learning implementation.

This stage will focus on improving the reliability of IDS predictions.

Specific techniques and implementation details cannot currently be filled because they have not been provided.

### Phase 6 — Explainability

The project phase plan includes adding explainability to IDS predictions.

The purpose of this stage is to provide information explaining why a prediction was produced.

Specific explainability methods cannot currently be filled because they have not been provided.

### Phase 7 — Real-Time Detection

The project phase plan includes integrating the trained IDS model with the live Industrial IoT environment.

The intended progression is:

```text
Industrial IoT Traffic
        ↓
MQTT Collection
        ↓
Preprocessing
        ↓
Feature Processing
        ↓
Trained IDS Model
        ↓
Prediction
        ↓
Dashboard