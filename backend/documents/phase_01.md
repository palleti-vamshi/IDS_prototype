# Phase 1 – Industrial IoT Environment Simulation

**Project:** LightX-IDS

**Status:** ✅ Completed

---

# Overview

Phase 1 establishes the Industrial Digital Twin of LightX-IDS by implementing a modular Industrial IoT environment capable of generating realistic machine telemetry through MQTT communication.

---

# Milestones

| No | Milestone | Status |
|----|-----------|--------|
| 1 | Factory Architecture | ✅ |
| 2 | Machine Framework | ✅ |
| 3 | Sensor Framework | ✅ |
| 4 | Machine–Sensor Integration | ✅ |
| 5 | Industrial Behavior Engine | ✅ |
| 6 | Factory Simulator V2 | ✅ |
| 7 | Full Phase 1 Integration | ✅ |
| 8 | Documentation & GitHub | 🚧 |

---

# Overall Architecture

```text
                Factory Simulator
                       │
               Simulation Clock
                       │
               Behavior Engine
                       │
             Industrial Machines
                       │
            Industrial Sensors
                       │
                MQTT Publisher
                       │
                 MQTT Broker
```

---

# Milestone 1 – Factory Architecture

### Objective

Build a scalable industrial factory hierarchy.

### Components

| Component | Purpose |
|-----------|---------|
| Factory | Root container |
| Production Line | Groups machines |
| Factory Builder | Builds the factory |
| Factory Manager | Factory operations |

### Architecture

```text
Factory
│
└── Production Line
      │
      ├── Motor
      ├── Pump
      ├── Tank
      ├── Conveyor
      ├── Valve
      └── Compressor
```

### Workflow

```text
FactoryBuilder
      │
      ▼
Create Factory
      │
      ▼
Create Production Line
      │
      ▼
Create Machines
      │
      ▼
Return Factory
```

### Result

- Modular hierarchy
- Easy scalability
- Clean separation of responsibilities

---

# Milestone 2 – Machine Framework

### Objective

Develop reusable industrial machine models.

### Machines

- Motor
- Pump
- Tank
- Conveyor
- Valve
- Compressor

### Architecture

```text
              BaseMachine
                   │
      ┌────────────┼────────────┐
      │            │            │
    Motor        Pump         Tank
      │            │            │
 Conveyor      Compressor     Valve
```

### Machine Lifecycle

```text
Created
   │
Initialized
   │
Running
   │
Stopped
```

### Result

- Reusable machine models
- Shared base class
- Ready for sensor integration

---

# Milestone 3 – Sensor Framework

### Objective

Develop reusable Industrial IoT sensors.

### Sensors

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

### Architecture

```text
               BaseSensor
                    │
 ┌──────────┬────────────┬───────────┐
 │          │            │           │
Temp    Pressure      Current      RPM
```

### Sensor Workflow

```text
Machine
    │
Read Value
    │
Create Packet
    │
Publish MQTT
```

### Result

- Standardized telemetry
- MQTT-ready sensors
- Modular sensor framework

---

# Milestone 4 – Machine–Sensor Integration

### Objective

Automatically attach sensors to industrial machines.

### Integration

```text
Factory Builder
        │
        ▼
 Sensor Registry
        │
        ▼
Attach Sensors
        │
        ▼
Machines Ready
```

### Data Flow

```text
Machine
   │
Sensor
   │
MQTT Packet
   │
MQTT Broker
```

### Result

- Automatic sensor assignment
- Simplified configuration
- Consistent telemetry generation

---

# Milestone 5 – Industrial Behavior Engine

### Objective

Generate realistic industrial machine behavior.

### Architecture

```text
Behavior Engine
       │
       ▼
Machine Behavior
       │
       ▼
Machine Variables
```

### State Machine

```text
STOPPED
    │
STARTING
    │
WARMUP
    │
NORMAL
    │
HIGH LOAD
    │
OVERLOADED
    │
FAULT
```

### Runtime

```text
Clock Tick
     │
Behavior Update
     │
Machine Variables
     │
Sensors Read Values
```

### Result

- Dynamic telemetry
- Realistic machine operation
- State-driven simulation

---

# Milestone 6 – Factory Simulator V2

### Objective

Execute a continuous Industrial Digital Twin.

### Workflow

```text
Initialize
    │
Build Factory
    │
Register Behaviors
    │
Collect Sensors
    │
Start Simulation
    │
Continuous Loop
```

### Simulation Loop

```text
Clock Tick
     │
Behavior Update
     │
Sensor Read
     │
MQTT Publish
```

### Result

- Continuous execution
- Graceful shutdown
- Stable simulation

---

# Milestone 7 – Full Phase 1 Integration

### Complete Flow

```text
Factory
    │
Production Line
    │
Machines
    │
Behavior Engine
    │
Sensors
    │
MQTT Publisher
    │
MQTT Broker
```

### Validation

- ✅ Factory initialized
- ✅ 6 Machines created
- ✅ 17 Sensors attached
- ✅ Continuous simulation
- ✅ Dynamic telemetry
- ✅ MQTT publishing
- ✅ Graceful shutdown

### Result

Phase 1 Industrial Digital Twin successfully completed.

---

# 🔄 System Workflow

```text
                Factory Simulator
                       │
                       ▼
               Build Factory
                       │
                       ▼
          Register Machine Behaviors
                       │
                       ▼
           Discover Attached Sensors
                       │
                       ▼
             Start Simulation Clock
                       │
                       ▼
               Continuous Loop
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
 Update Machine State          Read Sensors
         │                           │
         └─────────────┬─────────────┘
                       ▼
                Create MQTT Packet
                       │
                       ▼
                 Publish MQTT
                       │
                       ▼
                 MQTT Broker
```

---

# 🏭 Factory Architecture

```text
Factory
│
└── Production Line
      │
      ├── Motor
      ├── Pump
      ├── Tank
      ├── Conveyor
      ├── Valve
      └── Compressor
```

---

# ⚙️ Machine–Sensor Architecture

```text
Motor
│
├── Temperature Sensor
├── Current Sensor
├── RPM Sensor
└── Vibration Sensor

Pump
│
├── Pressure Sensor
├── Flow Sensor
└── Current Sensor

Tank
│
├── Level Sensor
├── Temperature Sensor
└── Pressure Sensor

Conveyor
│
├── RPM Sensor
├── Current Sensor
└── Proximity Sensor

Valve
│
└── Pressure Sensor

Compressor
│
├── Temperature Sensor
├── Pressure Sensor
└── Current Sensor
```

---

# 📡 Telemetry Pipeline

```text
Industrial Machine
        │
        ▼
Behavior Engine
        │
        ▼
Industrial Sensor
        │
        ▼
MQTT Packet
        │
        ▼
MQTT Publisher
        │
        ▼
MQTT Broker
        │
        ▼
Future Dataset Generator
        │
        ▼
Machine Learning IDS
```

# Phase 1 Summary

## Completed Components

- Factory Architecture
- Machine Framework
- Sensor Framework
- Machine–Sensor Integration
- Behavior Engine
- Factory Simulator V2
- Full System Integration

---

# Next Phase

```text
Phase 2

Cyber Attack Engine

        │

Spoofing
Replay
DoS
Injection
PLC Attacks

        │

Dataset Generation

        │

Machine Learning IDS
```

---


# Conclusion

Phase 1 successfully establishes the Industrial Digital Twin for LightX-IDS. The simulator continuously generates realistic industrial telemetry through modular machines, sensors, behavior models, and MQTT communication, providing a strong foundation for cyberattack simulation and future intrusion detection research.


# For Running
python -m backend.industrial.simulator.factory_simulator