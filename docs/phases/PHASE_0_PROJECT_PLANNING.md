# Phase 0 – Project Planning

## Document Information

| Field | Value |
|--------|-------|
| Document | Phase 0 – Project Planning |
| Project | LightX-IDS |
| Version | 1.0 |
| Status | Completed |
| Author | Vamshi |
| Type | Phase Design Document |
| Last Updated | July 2026 |

---

# 1. Introduction

Every successful software project begins with careful planning before any code is written. The objective of Phase 0 was to define the vision, scope, architecture, technologies, and development strategy for LightX-IDS.

Instead of immediately implementing features, this phase focused on understanding the problem, identifying project requirements, selecting suitable technologies, designing a modular architecture, and preparing a structured roadmap for future development.

By investing time in planning, the project minimizes unnecessary redesigns during later stages and provides a clear foundation for implementation.

Phase 0 established the engineering principles that guide the development of every subsequent phase.

---

# 2. Learning Objectives

After reading this document, the reader will understand:

- Why LightX-IDS was developed.
- The real-world problem the project addresses.
- The goals and scope of the project.
- The reasoning behind the selected technologies.
- The planned software architecture.
- The phased development strategy.
- The engineering decisions made before implementation began.

---

# 3. Background

The Industrial Internet of Things (IIoT) has transformed traditional manufacturing by connecting industrial devices such as sensors, Programmable Logic Controllers (PLCs), actuators, and supervisory systems through communication networks. This connectivity enables factories to automate production, monitor equipment in real time, and improve operational efficiency.

While these advancements have increased productivity, they have also introduced new cybersecurity challenges. Industrial devices that were once isolated are now connected to internal networks and, in many cases, the Internet. As a result, industrial environments have become attractive targets for cyber attacks.

Unlike traditional IT systems, industrial systems operate under strict real-time and safety requirements. A successful cyber attack may not only compromise data but can also interrupt production, damage equipment, or create safety hazards.

To understand these challenges and explore possible detection techniques, a realistic simulation platform is required. Building and experimenting on a real industrial environment is expensive, complex, and often impractical for students and researchers.

LightX-IDS addresses this challenge by providing a software-based Industrial IoT simulation platform where industrial communication, cyber attacks, dataset generation, and Machine Learning based intrusion detection can be studied within a controlled environment.

---

# 4. Problem Identification

Modern Industrial IoT environments face several cybersecurity challenges:

- Increasing connectivity between industrial devices.
- Lack of realistic datasets for Industrial IoT intrusion detection.
- Difficulty in experimenting with cyber attacks on real industrial systems.
- Limited educational platforms that combine industrial simulation, cyber attack generation, and machine learning within a single project.
- Need for a modular system that can be extended as new technologies and attack techniques emerge.

These challenges motivated the development of LightX-IDS as both a learning platform and a practical engineering project.

---

# 5. Project Goals

The primary goals established during the planning phase were:

- Build a realistic Industrial IoT simulation.
- Simulate industrial communication using MQTT.
- Model factory devices such as sensors and PLCs.
- Develop reusable software components following Object-Oriented Programming principles.
- Simulate multiple cyber attack scenarios.
- Generate labeled datasets for Machine Learning.
- Train an Intrusion Detection System capable of detecting malicious industrial traffic.
- Visualize factory operation and attack detection through an interactive dashboard.
- Maintain a modular architecture that supports future expansion.

These goals served as the foundation for the project's phased development approach.

---

# 6. Functional Requirements

Functional requirements define the core capabilities that the LightX-IDS platform must provide. These requirements describe the expected behavior of the system from a functional perspective.

| Requirement ID | Functional Requirement | Planned Phase |
|----------------|------------------------|---------------|
| FR-01 | The system shall simulate an Industrial IoT factory environment. | Phase 1 |
| FR-02 | The system shall simulate industrial sensors such as temperature and pressure sensors. | Phase 1 |
| FR-03 | The system shall support MQTT-based communication between industrial devices. | Phase 1 |
| FR-04 | The system shall implement a PLC capable of monitoring industrial sensor data. | Phase 1 |
| FR-05 | The system shall simulate multiple Industrial IoT cyber attacks. | Phase 2 |
| FR-06 | The system shall generate labeled datasets containing both normal and malicious traffic. | Phase 3 |
| FR-07 | The system shall preprocess datasets before Machine Learning training. | Phase 4 |
| FR-08 | The system shall train Machine Learning models for intrusion detection. | Phase 4 |
| FR-09 | The system shall detect cyber attacks in real time. | Phase 5 |
| FR-10 | The system shall provide an interactive dashboard for monitoring factory operations and security events. | Phase 5 |
| FR-11 | The system shall expose REST APIs for communication between backend services and the dashboard. | Phase 6 |
| FR-12 | The system shall provide a user-friendly frontend interface. | Phase 7 |
| FR-13 | The system shall support deployment and documentation for future extensions. | Phase 8 |

The phased implementation of these requirements allows each subsystem to be independently developed, tested, documented, and validated before integration into the complete LightX-IDS platform.

---

# 7. Non-Functional Requirements

Non-functional requirements describe the quality attributes that the system should maintain throughout its development and operation.

| Requirement ID | Non-Functional Requirement |
|----------------|---------------------------|
| NFR-01 | The architecture shall be modular and easy to extend. |
| NFR-02 | The system shall follow Object-Oriented Programming principles. |
| NFR-03 | The codebase shall remain maintainable and well documented. |
| NFR-04 | Each subsystem shall support independent testing. |
| NFR-05 | The architecture shall minimize code duplication through reusable components. |
| NFR-06 | The system shall support future expansion without significant redesign. |
| NFR-07 | Communication between industrial components shall be lightweight and efficient. |
| NFR-08 | Every completed phase shall be documented and tested before moving to the next phase. |
| NFR-09 | The project shall follow a consistent folder structure and coding standard. |
| NFR-10 | Documentation shall clearly explain both implementation details and engineering decisions.

These quality requirements guided every architectural decision made during the planning phase and continue to influence the development of subsequent phases.

---

# 8. Technology Selection

Selecting the appropriate technologies was one of the most important activities during the planning phase. Every technology was chosen based on the project requirements, ease of development, community support, scalability, and future integration with Machine Learning.

The following subsections explain the reasoning behind each major technology choice.

---

## 8.1 Programming Language

### Selected Technology

**Python**

### Alternatives Considered

- C++
- Java
- Python

### Reason for Selection

Python was selected because it provides an excellent balance between rapid development, readability, extensive library support, and Machine Learning capabilities.

The later phases of LightX-IDS require data preprocessing, dataset generation, machine learning model training, and backend API development. Python provides mature libraries for all of these tasks while allowing the entire project to remain within a single programming ecosystem.

### Benefits

- Simple and readable syntax.
- Excellent support for Machine Learning.
- Large open-source ecosystem.
- Fast development cycle.
- Cross-platform compatibility.

---

## 8.2 Communication Protocol

### Selected Technology

**MQTT (Message Queuing Telemetry Transport)**

### Alternatives Considered

- HTTP
- WebSockets
- MQTT

### Reason for Selection

Industrial IoT devices continuously exchange small packets of information. MQTT is specifically designed for lightweight communication between constrained devices and follows a publish-subscribe architecture that naturally fits industrial environments.

Unlike HTTP, MQTT allows sensors to continuously publish data without requiring repeated request-response communication.

### Benefits

- Lightweight protocol.
- Publish-subscribe communication model.
- Low network overhead.
- Widely adopted in Industrial IoT.
- Easy integration with sensors and PLCs.

---

## 8.3 MQTT Broker

### Selected Technology

**Mosquitto MQTT Broker**

### Reason for Selection

Mosquitto is a lightweight, open-source MQTT broker that is easy to configure, highly reliable, and widely used for learning and research projects.

It provides all the required functionality for simulating industrial communication without introducing unnecessary complexity.

---

## 8.4 Development Environment

The project is developed using:

- Visual Studio Code
- Git
- GitHub
- Python Virtual Environment (venv)

These tools provide version control, dependency isolation, collaborative development, and a consistent development workflow.

---

## 8.5 Future Technologies

Later phases of the project will introduce additional technologies, including:

- Pandas
- NumPy
- Scikit-learn
- FastAPI
- React
- Docker

These technologies have been planned from the beginning to ensure a smooth progression from industrial simulation to real-time intrusion detection.

---

# 9. Software Architecture Planning

Before implementation began, the project architecture was divided into independent modules.

Each module was assigned a single primary responsibility.

This modular architecture allows individual components to be developed, tested, documented, and maintained independently.

The planned architecture included:

- Industrial Environment
- MQTT Communication
- PLC Layer
- Cyber Attack Framework
- Dataset Generation
- Machine Learning
- Detection Engine
- REST API
- Frontend Dashboard

This layered design ensures that future enhancements can be integrated without requiring major modifications to previously completed components.

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