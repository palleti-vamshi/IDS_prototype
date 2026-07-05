# Phase 2 – Cyber Attack Framework

## Document Information

| Field | Value |
|--------|-------|
| Document | Phase 2 – Cyber Attack Framework |
| Project | LightX-IDS |
| Version | 1.0 |
| Status | Completed |
| Author | Vamshi |
| Type | Phase Design Document |
| Last Updated | July 2026 |

---

# 1. Introduction

After establishing a realistic Industrial IoT environment in Phase 1, the next objective was to simulate cyber attacks against the virtual factory.

An Intrusion Detection System cannot be developed using only normal operational traffic. Machine Learning models require both legitimate and malicious communication in order to learn the characteristics of cyber attacks.

Therefore, Phase 2 introduces a reusable Cyber Attack Framework capable of generating multiple Industrial IoT attack scenarios without modifying the underlying industrial infrastructure.

Rather than implementing each attack independently, a common attack framework was designed using Object-Oriented Programming principles. Every attack shares the same lifecycle while implementing its own attack-specific behavior.

This modular approach makes it easy to introduce additional attack types in future phases without affecting the existing implementation.

---

# 2. Learning Objectives

After reading this chapter, the reader will understand:

- Why attack simulation is required.
- The architecture of the Cyber Attack Framework.
- The role of BaseAttack.
- How Attack Manager coordinates attacks.
- How Attack Scheduler controls execution timing.
- How different attacks reuse the common framework.
- The engineering decisions behind the attack architecture.

---

# 3. Phase Objectives

The objectives of Phase 2 were:

- Design a reusable cyber attack framework.
- Simulate multiple Industrial IoT attacks.
- Reuse the MQTT communication layer from Phase 1.
- Generate malicious industrial traffic.
- Ensure attacks can be executed independently.
- Prepare the platform for dataset generation.

---

# 4. Folder Structure

backend/
└── attacks/
    ├── attack_config.py
    ├── attack_manager.py
    ├── base_attack.py
    ├── dos_attack.py
    ├── replay_attack.py
    ├── spoofing_attack.py
    ├── injection_attack.py
    ├── scheduler.py
    ├── logger.py
    └── tests/

Every module has a single responsibility.

| File | Responsibility |
|------|----------------|
| base_attack.py | Common attack lifecycle |
| attack_manager.py | Coordinates attacks |
| scheduler.py | Controls execution timing |
| attack_config.py | Stores configuration values |
| dos_attack.py | Simulates DoS attack |
| replay_attack.py | Simulates replay attack |
| spoofing_attack.py | Simulates spoofing attack |
| injection_attack.py | Simulates data injection attack |
| logger.py | Attack logging |
| attack_test.py | Framework testing |

---

# 5. Cyber Attack Framework Architecture

The attack framework was designed using inheritance.

Instead of every attack implementing connection handling, logging, execution control, and cleanup independently, these responsibilities are centralized inside BaseAttack.

```text
                    BaseAttack
                         │
     ┌──────────┬────────┼─────────┬──────────┐
     │          │        │         │          │
     ▼          ▼        ▼         ▼
   DoS      Replay   Spoofing  Injection
```

This architecture allows every attack to share the same lifecycle while implementing only its own attack logic.

---

# 6. BaseAttack

## What is BaseAttack?

BaseAttack is the parent class for every cyber attack implemented within LightX-IDS.

It provides the common execution lifecycle used by all attack modules.

Every attack inherits:

- Logging
- MQTT Publisher
- Attack duration
- Packet interval
- Start procedure
- Stop procedure

Each concrete attack implements only one method:

```python
execute()
```

which contains the attack-specific logic.

---

## Responsibilities

- Initialize attack configuration.
- Create MQTT Publisher.
- Start attack execution.
- Execute attacks at fixed intervals.
- Stop after configured duration.
- Disconnect safely.
- Log execution events.

---

## Attack Lifecycle

```text
Create Attack
      │
      ▼
Initialize Publisher
      │
      ▼
Start Attack
      │
      ▼
Loop
 │
 ├── execute()
 ├── wait(interval)
 └── duration reached?
      │
      ▼
Stop Attack
      │
      ▼
Disconnect MQTT
```

This lifecycle is shared by every attack in the project.

---

## Engineering Decision

Instead of duplicating attack execution code four times, inheritance was used.

Benefits:

- Less code duplication.
- Consistent behavior.
- Easier maintenance.
- Easier extension.

---

# 7. Attack Manager

## Purpose

The Attack Manager is responsible for coordinating multiple attack modules.

Instead of starting each attack manually, the Attack Manager registers attack objects and launches them when required.

---

## Responsibilities

- Register attacks.
- Maintain attack collection.
- Create execution threads.
- Start attacks.
- Stop attacks.

---

## Workflow

```text
Register Attack

↓

Attack Manager

↓

Create Thread

↓

Attack.start()

↓

Attack executes independently
```

---

## Why Threads?

Each attack executes independently.

Using Python threads allows multiple attacks to operate simultaneously without blocking one another.

This design also prepares the framework for future scenarios involving concurrent cyber attacks.

---

# 8. Attack Scheduler

## Purpose

The Attack Scheduler controls when attacks should begin.

Rather than embedding delays inside every attack, scheduling is centralized in one reusable component.

---

## Responsibilities

- Delay attack execution.
- Log waiting periods.
- Coordinate attack timing.

---

## Engineering Note

Separating scheduling logic from attack logic improves maintainability and keeps attack classes focused solely on attack behavior.

---

# 9. Attack Configuration

All configurable values are centralized inside `attack_config.py`.

Examples include:

- MQTT topics.
- Client IDs.
- Packet intervals.
- Attack durations.
- Fake device identifiers.
- Attack labels.

### Benefits

- Easy modification.
- Consistent configuration.
- Reduced hardcoded values.
- Easier experimentation.

Current configurable attacks include:

- DoS
- Replay
- Spoofing
- Data Injection

---

# 10. Denial of Service (DoS) Attack

## What is a DoS Attack?

A Denial of Service (DoS) attack attempts to overwhelm a target by transmitting an excessive number of packets within a short period. In Industrial IoT environments, such attacks can delay or disrupt communication between sensors, controllers, and monitoring systems.

Within LightX-IDS, the DoS attack rapidly publishes MQTT messages to simulate network congestion.

### Responsibilities

- Generate high-frequency MQTT messages.
- Simulate communication flooding.
- Produce malicious traffic for dataset generation.
- Evaluate IDS performance under heavy network load.

### Workflow

```text
Generate Payload
        │
        ▼
MQTT Publisher
        │
        ▼
MQTT Broker
        │
        ▼
Subscriber & PLC
```

### Characteristics

- Very small packet interval.
- High packet transmission rate.
- Continuous execution for the configured duration.

---

# 11. Replay Attack

## What is a Replay Attack?

A Replay Attack captures previously transmitted legitimate messages and retransmits them later.

Although the data itself appears valid, it is no longer current, potentially causing incorrect decisions within industrial control systems.

### Responsibilities

- Reuse previously valid sensor values.
- Publish repeated MQTT messages.
- Simulate delayed communication attacks.

### Example

```text
Original Sensor Value

29.4 °C

↓

Captured

↓

Replayed Multiple Times
```

### Purpose

Replay attacks help evaluate whether the Intrusion Detection System can distinguish between genuine real-time communication and duplicated historical traffic.

---

# 12. Spoofing Attack

## What is a Spoofing Attack?

A Spoofing Attack impersonates a legitimate industrial device by sending messages using a fake identity.

Instead of compromising a real sensor, the attacker pretends to be a trusted device.

### Responsibilities

- Simulate fake industrial devices.
- Publish forged MQTT messages.
- Test authentication and trust assumptions.

### Example

```text
Fake Sensor

↓

MQTT Publisher

↓

MQTT Broker

↓

PLC believes the message originated from a legitimate device.
```

### Purpose

Spoofing attacks evaluate how well the IDS can identify unauthorized devices within the industrial network.

---

# 13. Data Injection Attack

## What is a Data Injection Attack?

A Data Injection Attack modifies sensor readings before they reach the industrial controller.

Rather than interrupting communication, the attacker manipulates the contents of the transmitted data.

### Responsibilities

- Generate manipulated sensor values.
- Publish forged industrial measurements.
- Simulate false operational conditions.

### Example

Normal Temperature

29.4 °C

↓

Injected Temperature

85.0 °C

↓

PLC processes incorrect information.

### Purpose

This attack evaluates whether abnormal sensor values can be detected before affecting industrial decision making.

---

# 14. End-to-End Attack Execution Flow

The following diagram illustrates the execution flow of every attack module.

```text
Create Attack Object
          │
          ▼
Attack Manager Registers Attack
          │
          ▼
Attack Manager Starts Thread
          │
          ▼
BaseAttack.start()
          │
          ▼
execute()
          │
          ▼
MQTT Publisher
          │
          ▼
MQTT Broker
          │
          ▼
Subscriber
          │
          ▼
PLC Controller
          │
          ▼
Factory State Updated
```

Each attack follows this common lifecycle while implementing its own attack-specific logic.

---

# 15. Testing

Testing was performed to verify the correctness and stability of the Attack Framework.

## Individual Attack Testing

Each attack module was executed independently to verify:

- Successful MQTT connection.
- Correct message publication.
- Expected execution duration.
- Proper shutdown behavior.

Validated attacks include:

- DoS Attack
- Replay Attack
- Spoofing Attack
- Data Injection Attack

---

## Framework Testing

The complete framework was tested by:

- Registering attacks through the Attack Manager.
- Starting attacks in separate threads.
- Verifying concurrent execution.
- Confirming graceful shutdown.

These tests demonstrated that the framework behaves reliably under normal operating conditions.

---

# 16. Engineering Decisions

Several architectural decisions shaped the design of the Attack Framework.

| Decision | Reason | Benefit |
|----------|--------|----------|
| BaseAttack Abstract Class | Common lifecycle for every attack. | Eliminates duplicated code. |
| Attack Manager | Centralized coordination. | Easier management of multiple attacks. |
| Thread-Based Execution | Independent attack execution. | Supports concurrent simulations. |
| Central Configuration File | Store all configurable values in one place. | Simplifies maintenance and experimentation. |
| MQTT Reuse | Reuse existing communication layer. | No duplicate networking implementation. |
| Modular Attack Classes | One class per attack. | Easy extension with future attack types. |

---

# 17. Lessons Learned

Implementation of the Attack Framework provided several software engineering insights:

- Reusable base classes simplify development.
- Centralized configuration improves maintainability.
- Threading enables concurrent attack execution.
- Separating attack logic from communication reduces complexity.
- Building on the existing MQTT infrastructure avoids unnecessary duplication.

These lessons will guide the implementation of future attack types and detection modules.

---

# 18. Phase Outcome

The following deliverables were completed during Phase 2.

| Deliverable | Status |
|-------------|--------|
| BaseAttack Framework | ✅ |
| Attack Configuration | ✅ |
| Attack Manager | ✅ |
| Attack Scheduler | ✅ |
| DoS Attack | ✅ |
| Replay Attack | ✅ |
| Spoofing Attack | ✅ |
| Data Injection Attack | ✅ |
| Framework Testing | ✅ |

Phase 2 successfully introduced malicious industrial traffic generation while preserving the modular architecture established during Phase 1.

---

# 19. Preparation for Phase 3

With both normal industrial communication and cyber attack simulation available, the next phase focuses on generating structured datasets.

The objectives of Phase 3 include:

- Capture MQTT communication.
- Collect normal and malicious traffic.
- Automatically label captured data.
- Export datasets in CSV format.
- Prepare datasets for Machine Learning training.

Successful completion of Phase 3 will provide the data required to build and evaluate the Intrusion Detection System.

---

# 20. Summary

Phase 2 extended the Industrial Environment by introducing a reusable Cyber Attack Framework capable of simulating multiple Industrial IoT attacks.

Through the use of inheritance, centralized configuration, and thread-based execution, the framework remains modular, scalable, and easy to extend.

By reusing the MQTT communication infrastructure developed during Phase 1, malicious traffic can be generated without modifying the underlying industrial environment.

The completion of this phase provides the malicious data required for dataset generation and Machine Learning in the subsequent phases.