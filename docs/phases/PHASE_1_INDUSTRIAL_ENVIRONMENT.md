---

# 10. Engineering Decisions

During the planning phase, several important architectural decisions were made to ensure that LightX-IDS remains modular, maintainable, scalable, and easy to extend. Rather than making implementation decisions during development, these design choices were established before writing the majority of the code.

The following table summarizes the key engineering decisions made during Phase 0.

| Decision | Reason | Benefits | Trade-offs |
|----------|--------|----------|------------|
| Modular Project Structure | Separate different responsibilities into independent modules. | Better organization, easier maintenance, scalable architecture. | Slightly more folders and files to manage. |
| Layered Architecture | Divide the project into logical layers such as Industrial Environment, Attack Framework, Dataset Generation, and Machine Learning. | Clear separation of concerns and easier future expansion. | Requires careful planning of communication between layers. |
| Python as Primary Language | Support Machine Learning, rapid development, and extensive library availability. | Faster development and excellent ecosystem. | Lower raw performance compared to C++. |
| MQTT Communication | Simulate realistic Industrial IoT communication using a lightweight protocol. | Low overhead and publish-subscribe communication. | Requires an MQTT broker for communication. |
| Object-Oriented Design | Improve code reuse and maintainability through classes and inheritance. | Cleaner architecture and easier extension. | Slightly higher initial design complexity. |
| Base Classes (BaseSensor & BaseAttack) | Provide a common implementation for similar components. | Reduces code duplication and standardizes behavior. | Adds an abstraction layer for beginners to understand. |
| Phase-Based Development | Complete one subsystem before moving to the next. | Easier testing, documentation, and debugging. | Longer planning phase before advanced features. |
| Independent Testing | Verify every subsystem before integration. | Early bug detection and improved reliability. | Requires additional test modules. |

These decisions established a strong architectural foundation that continues to guide the development of every subsequent phase.

---

# 11. Development Roadmap

The complete LightX-IDS project is divided into multiple development phases. Each phase introduces a specific capability while building upon the previous phase.

| Phase | Objective | Status |
|--------|-----------|--------|
| Phase 0 | Project Planning and Architecture | ✅ Completed |
| Phase 1 | Industrial Environment Simulation | ✅ Completed |
| Phase 2 | Cyber Attack Framework | ✅ Completed |
| Phase 3 | Dataset Generation | ⏳ Planned |
| Phase 4 | Machine Learning Intrusion Detection | ⏳ Planned |
| Phase 5 | Dashboard & Visualization | ⏳ Planned |
| Phase 6 | Backend REST API | ⏳ Planned |
| Phase 7 | Frontend Development | ⏳ Planned |
| Phase 8 | Deployment, Testing & Final Documentation | ⏳ Planned |

The phased development strategy ensures that every subsystem is fully implemented, tested, documented, and validated before introducing additional complexity.

---

# 12. Success Criteria

Phase 0 was considered successful when the following objectives were achieved:

- A clear project vision was established.
- The software architecture was designed.
- The technology stack was finalized.
- The project folder structure was planned.
- Development phases were defined.
- Functional and non-functional requirements were documented.
- Engineering decisions were recorded.
- A roadmap for future implementation was prepared.

Meeting these objectives ensured that development could proceed with a clear direction and minimized the likelihood of major architectural changes later in the project.

---

# 13. Phase Outcome

The following deliverables were completed during Phase 0.

| Deliverable | Status |
|-------------|--------|
| Project Vision | ✅ |
| Problem Analysis | ✅ |
| Functional Requirements | ✅ |
| Non-Functional Requirements | ✅ |
| Technology Selection | ✅ |
| Software Architecture Planning | ✅ |
| Engineering Decisions | ✅ |
| Development Roadmap | ✅ |

Phase 0 established the engineering foundation upon which all remaining phases of LightX-IDS are built.

---

# 14. Preparation for Phase 1

With the project architecture finalized, the next phase focuses on implementing the Industrial Environment Simulation.

The objectives of Phase 1 include:

- Implementing industrial sensors.
- Establishing MQTT communication.
- Developing the PLC controller.
- Simulating factory operation.
- Testing communication between all industrial components.

Successful completion of Phase 1 provides the operational environment required for introducing cyber attack simulations in Phase 2.

---

# 15. Factory State

## What is Factory State?

The Factory State represents the current operational condition of the simulated factory. It acts as a centralized storage location where the latest values from all industrial sensors are maintained.

Instead of each module storing its own copy of sensor data, the PLC updates a single shared state. This ensures that every subsystem works with the same information.

### Responsibilities

- Store the latest temperature reading.
- Store the latest pressure reading.
- Maintain the current factory status.
- Provide a consistent view of the factory for future modules.

### Example Factory State

```json
{
    "temperature": 29.4,
    "pressure": 101.8,
    "status": "NORMAL"
}
```

### Why is it important?

The Factory State becomes the source of truth for the entire platform. Later phases such as dataset generation, intrusion detection, and the dashboard will all consume this information.

---

# 16. Rule Engine

## What is the Rule Engine?

The Rule Engine contains the logic used by the PLC to determine the operational condition of the factory.

Rather than embedding decision logic directly inside the PLC Controller, the rules are separated into their own module. This keeps the controller focused on coordination while the Rule Engine focuses on evaluation.

### Responsibilities

- Evaluate incoming sensor values.
- Determine whether the factory is operating normally.
- Update the operational status.
- Support future expansion with additional industrial rules.

### Current Status

At this stage, the Rule Engine performs basic operational checks.

Future phases will introduce more advanced rules and machine learning based decision making.

---

# 17. Factory Simulator

## Purpose

The Factory Simulator coordinates the execution of the industrial environment.

Instead of manually starting every sensor and communication component, the simulator initializes and manages the complete factory workflow.

### Responsibilities

- Start industrial sensors.
- Initialize communication.
- Coordinate continuous simulation.
- Provide a single entry point for industrial testing.

### Workflow

```text
Start Simulation
        │
        ▼
Initialize MQTT
        │
        ▼
Start Temperature Sensor
        │
        ▼
Start Pressure Sensor
        │
        ▼
Publish MQTT Messages
        │
        ▼
PLC Receives Updates
        │
        ▼
Update Factory State
```

---

# 18. End-to-End Execution Flow

The complete execution flow of the Industrial Environment is illustrated below.

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
                       ▼
                 Factory State
```

### Step-by-Step Execution

1. The simulator starts all industrial components.
2. Temperature and Pressure sensors generate values.
3. Sensor readings are converted into JSON payloads.
4. The MQTT Publisher sends the payloads to the broker.
5. The MQTT Broker distributes messages to subscribers.
6. The MQTT Subscriber receives the data.
7. The PLC Controller processes the incoming values.
8. The Factory State is updated with the latest operational information.

This execution cycle repeats continuously throughout the simulation.

---

# 19. Testing

Testing was performed throughout the implementation of Phase 1 to ensure that every subsystem operated correctly before integration.

## Unit Testing

The following components were tested individually:

- MQTT Publisher
- MQTT Subscriber
- Temperature Sensor
- Pressure Sensor
- PLC Controller

## Integration Testing

After verifying each module independently, integration testing confirmed that all industrial components communicated correctly.

The following scenarios were validated:

- MQTT connection established successfully.
- Temperature sensor publishes data.
- Pressure sensor publishes data.
- Subscriber receives sensor messages.
- PLC updates Factory State correctly.
- Continuous simulation executes without interruption.

Successful completion of these tests confirmed that the Industrial Environment was ready for Phase 2.

---

# 20. Engineering Decisions

Several important design decisions were made during Phase 1.

| Decision | Reason | Benefit |
|----------|--------|----------|
| MQTT Communication | Simulate real Industrial IoT communication. | Lightweight and scalable messaging. |
| Reusable Publisher | Avoid duplicated communication code. | Improved maintainability. |
| BaseSensor | Common sensor behavior. | Easier extension for new sensors. |
| Centralized Factory State | Single source of truth. | Consistent system state. |
| Separate Rule Engine | Keep PLC logic modular. | Cleaner architecture. |
| Modular Folder Structure | Separate responsibilities. | Easier maintenance and testing. |

These decisions reduced coupling between components and prepared the project for future expansion.

---

# 21. Lessons Learned

During the implementation of Phase 1, several important software engineering lessons were learned:

- Building modular software simplifies future development.
- Separating communication from business logic improves maintainability.
- MQTT is well suited for Industrial IoT simulations.
- Independent testing helps identify problems before integration.
- A well-planned architecture reduces redesign effort in later phases.

These lessons influenced the design of all subsequent phases.

---

# 22. Phase Outcome

The following deliverables were successfully completed during Phase 1.

| Deliverable | Status |
|-------------|--------|
| Industrial Environment | ✅ |
| MQTT Communication | ✅ |
| MQTT Publisher | ✅ |
| MQTT Subscriber | ✅ |
| Temperature Sensor | ✅ |
| Pressure Sensor | ✅ |
| PLC Controller | ✅ |
| Factory State | ✅ |
| Rule Engine | ✅ |
| Factory Simulator | ✅ |
| Integration Testing | ✅ |

Phase 1 successfully established a realistic Industrial IoT simulation environment capable of generating and processing operational factory data.

---

# 23. Preparation for Phase 2

With the Industrial Environment fully operational, the next phase introduces cyber attack simulation.

Phase 2 focuses on:

- Designing a reusable attack framework.
- Implementing multiple Industrial IoT attack types.
- Integrating attacks into the MQTT communication layer.
- Producing malicious industrial traffic.
- Preparing the platform for dataset generation.

The modular architecture established during Phase 1 enables attack modules to reuse the existing MQTT communication infrastructure without modifying the industrial components.

---

# 24. Summary

Phase 1 transformed the architectural plans created during Phase 0 into a functioning Industrial IoT simulation.

A modular communication infrastructure was developed using MQTT, reusable industrial sensors were implemented, and a PLC controller was created to monitor factory operation through a centralized Factory State.

The completion of this phase provides the operational foundation required for introducing cyber attack simulation, dataset generation, and machine learning in subsequent phases.

With Phase 1 completed, LightX-IDS now possesses a stable Industrial Environment that serves as the backbone for the remainder of the project.