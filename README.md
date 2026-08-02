# 🛡️ LightX-IDS
### Lightweight Explainable Real-Time Intrusion Detection System for Industrial IoT Networks

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-green.svg)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange.svg)
![Status](https://img.shields.io/badge/Status-Phase%201%20Completed-success.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

---

# 📖 Overview

**LightX-IDS** is a modular Industrial Internet of Things (IIoT) Intrusion Detection System designed to provide **lightweight, explainable, and real-time cyberattack detection** for industrial environments.

Instead of depending on expensive industrial hardware, LightX-IDS first builds a complete **Industrial Digital Twin**, capable of simulating industrial machines, sensors, factory behavior, and MQTT communication. This simulated environment is then used for cyberattack simulation, dataset generation, machine learning model training, explainable AI, and real-time intrusion detection.

The project follows a modular architecture where each phase builds upon the previous one, enabling scalable development and future industrial deployment.

---

# 🚀 Project Roadmap

```text
Phase 0
Planning & Research
        │
        ▼
Phase 1 ✅
Industrial IoT Environment Simulation
        │
        ▼
Phase 2
Cyber Attack Simulation
        │
        ▼
Phase 3
Dataset Generation
        │
        ▼
Phase 4
Machine Learning IDS
        │
        ▼
Phase 5
False Positive Reduction
        │
        ▼
Phase 6
Explainable AI (XAI)
        │
        ▼
Phase 7
Real-Time Intrusion Detection
        │
        ▼
Phase 8
Professional Dashboard
```

---

# ✨ Current Features

## 🏭 Industrial Digital Twin

- Factory Architecture
- Factory Builder
- Factory Manager
- Production Line
- Continuous Factory Simulator
- Industrial Behavior Engine
- Simulation Clock

---

## ⚙️ Industrial Machines

- Motor
- Pump
- Tank
- Conveyor
- Valve
- Compressor

---

## 📡 Industrial Sensors

- Temperature
- Pressure
- Current
- Voltage
- RPM
- Flow
- Level
- Vibration
- Proximity
- Humidity

---

## 📨 MQTT Communication

- Mosquitto Broker
- MQTT Publisher
- Standardized Sensor Packets
- Continuous Telemetry Streaming

---

## 🤖 Machine Learning (Implemented)

- Dataset Loader
- Feature Engineering
- Feature Selection
- Model Factory
- Random Forest
- Decision Tree
- Logistic Regression
- XGBoost
- Model Evaluation
- Benchmark Generation
- Model Serialization

---

# 🏗️ System Architecture

```text
                    Factory Simulator
                           │
                   Simulation Clock
                           │
                    Behavior Engine
                           │
                 Industrial Machines
                           │
                Attached Industrial Sensors
                           │
                     MQTT Publisher
                           │
                      MQTT Broker
                           │
                   Dataset Generation
                           │
                   Machine Learning IDS
                           │
                    Explainable AI
                           │
                 Real-Time Detection
                           │
                     Web Dashboard
```

---

# 📂 Project Structure

```text
IDS_prototype/
│
├── backend/
│   ├── core/
│   ├── industrial/
│   │   ├── behavior/
│   │   ├── factory/
│   │   ├── machines/
│   │   ├── mqtt/
│   │   ├── sensors/
│   │   ├── simulator/
│   │   └── registry/
│   │
│   ├── preprocessing/
│   ├── ml/
│   ├── models/
│   ├── services/
│   └── utils/
│
├── frontend/
├── docs/
├── dataset/
├── README.md
└── requirements.txt
```

---

# 📊 Phase 1 Progress

| Milestone | Status |
|-----------|--------|
| Factory Architecture | ✅ |
| Machine Framework | ✅ |
| Sensor Framework | ✅ |
| Machine–Sensor Integration | ✅ |
| Industrial Behavior Engine | ✅ |
| Factory Simulator V2 | ✅ |
| Full Phase 1 Integration | ✅ |
| Documentation & GitHub | 🚧 |

---

# ⚙️ Technologies Used

- Python
- MQTT (Mosquitto)
- Paho MQTT
- Scikit-Learn
- XGBoost
- NumPy
- Pandas
- FastAPI *(Planned)*
- React *(Planned)*

---

# 🚀 Getting Started

### Clone Repository

```bash
git clone https://github.com/palleti-vamshi/IDS_prototype.git
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Mosquitto Broker

```bash
brew services start mosquitto
```

### Run Factory Simulator

```bash
python -m backend.industrial.simulator.factory_simulator
```

---

# 📌 Future Development

- Cyber Attack Simulation
- Dataset Generation
- Machine Learning Optimization
- Explainable AI (SHAP)
- Real-Time MQTT Detection
- FastAPI Backend
- React Dashboard
- Docker Deployment

---

# 👨‍💻 Team

### Vamshi Palleti

- System Architecture
- Backend Development
- Industrial Digital Twin
- Machine Learning
- Model Evaluation

### Srinidhi

- Frontend Development
- Dashboard UI
- Dataset Preparation
- Frontend Integration

---

# 🎓 Academic Project

**LightX-IDS**

Lightweight Explainable Real-Time Intrusion Detection System for Industrial IoT Networks

Developed as a **Final Year B.Tech Project**.

---

# 📄 License

This project is released under the **MIT License**.
