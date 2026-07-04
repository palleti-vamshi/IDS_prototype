# Phase 1 – Industrial Environment Simulation

## Status
🟡 In Progress

---

## Objective

Develop a software-only Industrial IoT environment that simulates a real factory. This environment will generate realistic industrial communication using MQTT and serve as the foundation for attack simulation, dataset generation, and intrusion detection.

---

## Research Goal

Create a lightweight, modular, and extensible Industrial IoT simulation without requiring physical hardware such as Arduino or Raspberry Pi.

---

## Modules

### Industrial Components

- Temperature Sensor
- Pressure Sensor
- MQTT Broker (Mosquitto)
- PLC Controller
- SCADA Dashboard
- Factory Simulator

---

## Technologies Used

- Python 3.12
- Mosquitto MQTT Broker
- Paho MQTT
- Logging Module

---

## System Architecture

Temperature Sensor
        ↓
MQTT Publisher
        ↓
Mosquitto Broker
        ↓
MQTT Subscriber
        ↓
PLC Controller
        ↓
SCADA Dashboard

---

## Folder Structure

```text
backend/
└── industrial/
    ├── config/
    ├── mqtt/
    ├── plc/
    ├── scada/
    ├── sensors/
    └── simulator/
```

---

## Phase Deliverables

- Simulated Temperature Sensor
- Simulated Pressure Sensor
- MQTT Communication
- PLC Data Processing
- SCADA Monitoring
- Normal Industrial Traffic Generation

---

## Progress Checklist

- [x] Industrial Architecture Designed
- [x] Folder Structure Created
- [x] Mosquitto Installed
- [x] MQTT Configuration Module
- [x] Logging Module
- [ ] MQTT Publisher
- [ ] MQTT Subscriber
- [ ] MQTT Communication Test
- [ ] Temperature Sensor
- [ ] Pressure Sensor
- [ ] PLC Controller
- [ ] SCADA Dashboard
- [ ] Factory Simulator

---

## Expected Output

A fully functional virtual industrial environment capable of generating normal industrial communication that will be used in later phases for attack simulation and IDS model development.

---

## Next Phase

Phase 2 – Attack Simulation

The completed industrial environment will be used to simulate cyber attacks such as DoS, Spoofing, Replay, and Data Injection for dataset generation.