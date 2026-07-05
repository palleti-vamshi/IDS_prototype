# LightX-IDS System Architecture

## Document Information

| Field | Value |
|--------|-------|
| Document | System Architecture |
| Project | LightX-IDS |
| Version | 1.0 |
| Status | Approved |
| Author | Vamshi |
| Type | Software Architecture Document |
| Last Updated | July 2026 |

---

# 1. Introduction

LightX-IDS (Lightweight Industrial Intrusion Detection System) is a modular Industrial Internet of Things (IIoT) cybersecurity platform designed to simulate a smart factory, generate industrial communication traffic, simulate cyber attacks, create machine learning datasets, and detect malicious activities in real time.

The project follows a phased engineering approach, where each phase introduces a new capability while maintaining a modular and scalable architecture. Every completed phase is tested, documented, and frozen before development continues to the next stage.

Rather than building a single monolithic application, LightX-IDS is divided into independent layers such as industrial simulation, communication, attack simulation, dataset generation, machine learning, and visualization. This separation improves maintainability, scalability, and future extensibility.

The objective of this architecture document is to provide a complete overview of the system, describe the responsibilities of each major layer, explain how components interact, and establish a common architectural reference for all future phases of development.

---

# 2. Problem Statement

Industrial Internet of Things (IIoT) environments have become an essential part of modern manufacturing systems. Sensors, Programmable Logic Controllers (PLCs), communication protocols, and supervisory systems continuously exchange data to automate industrial processes and improve operational efficiency.

As industrial systems become increasingly interconnected, they are also becoming more exposed to cyber threats. Attacks such as Denial of Service (DoS), Replay, Spoofing, and Data Injection can disrupt normal factory operations, manipulate sensor values, or interfere with control decisions. Such attacks may lead to production downtime, equipment damage, safety risks, and financial losses.

Traditional Intrusion Detection Systems are primarily designed for conventional IT networks and often fail to consider the unique characteristics of industrial environments, including continuous sensor communication, real-time control requirements, and protocol-specific behavior.

Although several research solutions exist, many focus only on machine learning models without providing a complete industrial simulation environment capable of generating realistic normal and malicious traffic.

LightX-IDS addresses this challenge by providing a modular Industrial IoT platform that combines factory simulation, cyber attack generation, dataset creation, machine learning, and real-time intrusion detection into a single extensible architecture.

The project serves both as a practical learning platform for Industrial Cybersecurity and as a foundation for experimenting with intrusion detection techniques in simulated smart factory environments.

---

# 3. Vision

The long-term vision of LightX-IDS is to provide a complete, modular, and extensible Industrial Internet of Things (IIoT) Intrusion Detection System capable of simulating industrial operations, generating realistic cyber attack scenarios, collecting labeled datasets, training machine learning models, and detecting malicious activities in real time.

The project is designed to replicate the communication flow of a modern smart factory, allowing industrial devices such as sensors and PLCs to exchange data through MQTT while supporting controlled cyber attack simulations. This environment provides a realistic foundation for cybersecurity experimentation without requiring access to physical industrial hardware.

Rather than focusing on a single technology, LightX-IDS integrates multiple domains including Industrial IoT, network communication, cybersecurity, software engineering, data engineering, and machine learning into one unified platform.

When all development phases are completed, the system will be capable of:

- Simulating an Industrial IoT factory environment.
- Generating realistic normal operational traffic.
- Simulating multiple industrial cyber attacks.
- Automatically collecting and labeling industrial datasets.
- Training and evaluating Machine Learning based Intrusion Detection Systems.
- Detecting malicious traffic in real time.
- Visualizing factory operations, attacks, and alerts through an interactive dashboard.
- Providing a modular architecture that can be extended with additional sensors, communication protocols, attack types, and detection algorithms.

The architecture has been intentionally designed to ensure that each subsystem can evolve independently while remaining fully integrated within the overall LightX-IDS platform.

---

# 4. Project Objectives

The primary objective of LightX-IDS is to design and develop a modular Industrial Internet of Things (IIoT) Intrusion Detection System that accurately simulates industrial environments, generates realistic industrial communication, reproduces cyber attack scenarios, and applies Machine Learning techniques for attack detection.

The project has been divided into multiple development phases to ensure that each subsystem is independently designed, implemented, tested, documented, and validated before integration into the complete platform.

The major objectives of the project are:

- Design a modular and scalable software architecture.
- Simulate an Industrial IoT factory environment.
- Implement reliable MQTT-based communication between industrial devices.
- Simulate industrial sensors capable of producing realistic telemetry.
- Develop a Programmable Logic Controller (PLC) to monitor factory operations.
- Simulate multiple Industrial IoT cyber attacks.
- Generate labeled datasets containing both normal and malicious traffic.
- Train and evaluate Machine Learning based Intrusion Detection models.
- Detect cyber attacks in real time.
- Provide an interactive dashboard for monitoring factory status and security events.
- Maintain a clean, reusable, and extensible software architecture.

These objectives collectively ensure that LightX-IDS serves both as a cybersecurity research platform and as an educational software engineering project.

---

# 5. High-Level System Architecture

The complete LightX-IDS platform is organized into multiple independent architectural layers. Each layer has a clearly defined responsibility and communicates only with the layers directly connected to it.

The overall architecture is illustrated below.

```text
                           User
                             │
                             ▼
                    LightX-IDS Platform
                             │
                             ▼
         ┌───────────────────────────────┐
         │ Industrial Environment Layer  │
         └───────────────────────────────┘
                             │
                             ▼
          ┌─────────────────────────────┐
          │ MQTT Communication Layer    │
          └─────────────────────────────┘
                             │
                             ▼
          ┌─────────────────────────────┐
          │ PLC Decision Layer          │
          └─────────────────────────────┘
                             │
                             ▼
          ┌─────────────────────────────┐
          │ Cyber Attack Framework      │
          └─────────────────────────────┘
                             │
                             ▼
          ┌─────────────────────────────┐
          │ Dataset Generation Layer    │
          └─────────────────────────────┘
                             │
                             ▼
          ┌─────────────────────────────┐
          │ Machine Learning Layer      │
          └─────────────────────────────┘
                             │
                             ▼
          ┌─────────────────────────────┐
          │ Detection Engine            │
          └─────────────────────────────┘
                             │
                             ▼
          ┌─────────────────────────────┐
          │ REST API & Dashboard Layer  │
          └─────────────────────────────┘
                             │
                             ▼
                          End User
```

The layered architecture allows each subsystem to evolve independently while maintaining a clear separation of responsibilities. This modular approach improves maintainability, simplifies testing, and enables future extensions without affecting existing components.

---

# 6. System Layers

LightX-IDS is divided into eight logical layers. Each layer performs a specific role within the overall architecture and communicates with adjacent layers through clearly defined interfaces.

The following sections describe the responsibility of each architectural layer.

## 6.1 Industrial Environment Layer

### Purpose

To simulate a realistic Industrial IoT factory capable of generating normal operational data.

### Components

- Temperature Sensor
- Pressure Sensor
- Factory Simulator

### Responsibilities

- Generate industrial telemetry.
- Simulate continuous factory operation.
- Produce realistic sensor values.
- Supply operational data to the MQTT communication layer.

### Current Status

✅ Implemented (Phase 1)

### Future Role

Provide realistic operational data for dataset generation and machine learning.

---

## 6.2 MQTT Communication Layer

### Purpose

To provide reliable communication between all Industrial IoT devices.

### Components

- MQTT Publisher
- MQTT Subscriber
- Mosquitto MQTT Broker

### Responsibilities

- Publish sensor data.
- Route industrial messages.
- Deliver messages to subscribed devices.
- Maintain asynchronous communication.

### Current Status

✅ Implemented (Phase 1)

### Future Role

Transport both normal industrial traffic and malicious traffic generated during cyber attack simulations.

---

## 6.3 PLC Decision Layer

### Purpose

To simulate the behavior of an industrial Programmable Logic Controller responsible for monitoring factory operations.

### Components

- PLC Controller
- Factory State
- Rule Engine

### Responsibilities

- Receive sensor updates.
- Maintain factory state.
- Evaluate operational rules.
- Detect abnormal operating conditions.

### Current Status

✅ Implemented (Phase 1)

### Future Role

Supply operational context to the Machine Learning detection engine.

---

## 6.4 Cyber Attack Framework

### Purpose

To simulate realistic Industrial IoT cyber attacks against the virtual factory.

### Components

- BaseAttack
- Attack Manager
- Scheduler
- DoS Attack
- Replay Attack
- Spoofing Attack
- Data Injection Attack

### Responsibilities

- Generate malicious industrial traffic.
- Simulate different attack behaviors.
- Produce labeled attack data.
- Support future attack extensions.

### Current Status

✅ Implemented (Phase 2)

### Future Role

Generate malicious datasets required for Machine Learning training.

---

## 6.5 Dataset Generation Layer

**Current Status:** ⏳ Planned (Phase 3)

This layer will collect industrial communication from both normal operation and cyber attack simulations, automatically label the captured traffic, and export structured datasets suitable for Machine Learning.

---

## 6.6 Machine Learning Layer

**Current Status:** ⏳ Planned (Phase 4)

This layer will preprocess industrial datasets, train Machine Learning models, evaluate model performance, and prepare trained models for deployment.

---

## 6.7 Detection Layer

**Current Status:** ⏳ Planned

This layer will receive real-time industrial traffic and classify incoming communication as either normal or malicious using the trained Machine Learning model.

---

## 6.8 Dashboard & API Layer

**Current Status:** ⏳ Planned

This layer will provide visualization, monitoring, alerts, and REST APIs for interacting with the complete LightX-IDS platform.

---

# 7. End-to-End Data Flow

The operation of LightX-IDS follows a layered data flow architecture. Information generated inside the virtual factory travels through multiple processing stages before reaching the end user.

The following diagram illustrates the complete execution flow of the system.

```text
Temperature Sensor          Pressure Sensor
        │                         │
        └──────────────┬──────────┘
                       │
                       ▼
               MQTT Publisher
                       │
                       ▼
              Mosquitto MQTT Broker
                       │
                       ▼
               MQTT Subscriber
                       │
                       ▼
                PLC Controller
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
 Normal Factory Data          Cyber Attack Modules
         │                           │
         └─────────────┬─────────────┘
                       ▼
             Dataset Generation Layer
                       │
                       ▼
          Machine Learning Pipeline
                       │
                       ▼
          Intrusion Detection Engine
                       │
                       ▼
              REST API & Dashboard
                       │
                       ▼
                     User
```

## Data Flow Explanation

The complete system operates in the following sequence:

1. Industrial sensors continuously generate operational values.
2. Sensor data is converted into MQTT messages.
3. Messages are published to the MQTT Broker.
4. The MQTT Broker forwards messages to subscribed components.
5. The PLC Controller updates the current factory state.
6. During attack simulations, malicious traffic is injected into the communication flow.
7. The Dataset Generation Layer captures both normal and malicious traffic.
8. Machine Learning models are trained using the generated datasets.
9. During deployment, incoming traffic is classified by the Intrusion Detection Engine.
10. Detection results are displayed through the REST API and Dashboard.

This layered execution model ensures that every subsystem performs a single responsibility while contributing to the overall operation of the platform.

---

# 8. Core Design Principles

The architecture of LightX-IDS is based on established software engineering principles to ensure maintainability, scalability, and extensibility.

## 8.1 Modularity

Each subsystem has a clearly defined responsibility and can be developed, tested, and maintained independently.

Example:

- MQTT handles communication.
- Sensors generate data.
- PLC performs control logic.
- Attack modules generate malicious traffic.
- Dataset modules collect data.
- Machine Learning modules perform prediction.

---

## 8.2 Separation of Concerns

Each component focuses on one specific responsibility.

For example:

- Sensors never communicate directly with the PLC.
- The Publisher only publishes data.
- The Subscriber only receives data.
- The PLC only evaluates factory logic.

This separation reduces complexity and improves code readability.

---

## 8.3 Reusability

Reusable base classes are used wherever possible.

Examples include:

- BaseSensor
- BaseAttack

This allows new sensors and attack types to be added with minimal code duplication.

---

## 8.4 Scalability

The architecture supports future expansion without requiring significant modifications.

Examples include:

- Additional sensors
- Multiple factory production lines
- New attack types
- Additional MQTT topics
- Alternative Machine Learning models

---

## 8.5 Maintainability

The project is divided into logical folders and modules.

Each module has a well-defined responsibility, making debugging, testing, and future development easier.

---

## 8.6 Testability

Every major subsystem is designed to support independent testing before integration.

Examples:

- Sensor testing
- MQTT testing
- PLC testing
- Attack testing
- Integration testing

This approach ensures that problems are detected early during development.

---

# 9. Current Implementation Status

The development of LightX-IDS follows a phased roadmap.

| Phase | Description | Status |
|--------|-------------|--------|
| Phase 0 | Project Planning & Architecture | ✅ Completed |
| Phase 1 | Industrial Environment Simulation | ✅ Completed |
| Phase 2 | Cyber Attack Framework | ✅ Completed |
| Phase 3 | Dataset Generation | ⏳ Planned |
| Phase 4 | Machine Learning IDS | ⏳ Planned |
| Phase 5 | Dashboard & Visualization | ⏳ Planned |
| Phase 6 | REST API Backend | ⏳ Planned |
| Phase 7 | Frontend | ⏳ Planned |
| Phase 8 | Deployment & Documentation | ⏳ Planned |

At the time of writing, the industrial simulation and cyber attack framework have been successfully implemented and tested. The next milestone is dataset generation.

---

# 10. Future Expansion

The modular architecture of LightX-IDS has been designed to support future enhancements.

Potential extensions include:

- Multiple production lines
- Additional industrial sensors
- Modbus and OPC-UA protocol support
- Additional cyber attack techniques
- Deep Learning based intrusion detection
- Cloud deployment
- Docker containerization
- Real PLC integration
- Real SCADA integration
- Multi-user dashboard
- Real-time alerting system

The architecture has been intentionally designed to allow these features to be integrated without major changes to the existing system.

---

# 11. Conclusion

LightX-IDS follows a layered and modular architecture that separates industrial simulation, communication, cyber attack generation, dataset creation, machine learning, and visualization into independent but interconnected subsystems.

This architecture provides a strong foundation for incremental development, simplifies testing and maintenance, and supports future expansion as new features are introduced.

The System Architecture Document serves as the primary architectural reference for the project and provides the foundation for all subsequent phase documents.