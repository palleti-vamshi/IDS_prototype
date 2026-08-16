# Phase 2 — Attack Framework

## 1. Objective

The objective of Phase 2 is to implement a modular cyber-attack simulation framework capable of generating controlled attack traffic within the simulated Industrial IoT environment.

The framework provides the attack scenarios required for dataset generation and later IDS model development.

---

## 2. Attack Framework Overview

The LightX-IDS attack framework is designed as a modular system in which individual attacks are implemented independently and controlled through a common attack-management mechanism.

The implemented attack modules are:

- Denial of Service (DoS)
- Replay Attack
- Injection Attack
- Spoofing Attack

The framework allows attacks to be executed against the simulated MQTT-based industrial environment.

---

## 3. Implemented Attack Types

### 3.1 Denial of Service (DoS)

The DoS attack represents an attempt to disrupt normal industrial communication by generating excessive or disruptive traffic.

The attack is implemented as an independent attack module and can be registered with the attack manager for execution.

### 3.2 Replay Attack

The Replay Attack represents the reuse of previously captured or generated sensor messages.

The attack module is designed to introduce repeated or previously observed telemetry into the communication flow.

### 3.3 Injection Attack

The Injection Attack represents the insertion of manipulated or unexpected sensor information into the industrial communication channel.

The attack can be used to generate anomalous records for IDS training and evaluation.

### 3.4 Spoofing Attack

The Spoofing Attack represents the generation of sensor communication that attempts to imitate legitimate industrial-device traffic.

It provides attack traffic that can be used to evaluate the ability of LightX-IDS to distinguish legitimate telemetry from manipulated sources.

---

## 4. Attack Manager

The `AttackManager` provides centralized management of attack execution.

The attack framework uses the manager to:

1. Create an attack instance.
2. Register the attack.
3. Start the registered attack.
4. Track the execution thread.
5. Wait for attack completion.

This approach allows different attack implementations to share a common execution mechanism.

---

## 5. Attack Registration

Attacks are registered dynamically with the attack manager.

The dataset-generation workflow creates an attack instance and registers it using:

`manager.register_attack(attack)`

The manager then starts the attack using its common execution mechanism.

This keeps the individual attack implementations independent from the overall dataset-generation workflow.

---

## 6. Dynamic Attack Runner

The `AttackRunner` provides automated attack scheduling for dataset generation.

The runner maintains a collection containing:

- `DoSAttack`
- `ReplayAttack`
- `InjectionAttack`
- `SpoofingAttack`

Before each attack cycle, the collection is copied and randomly shuffled.

Therefore, the order in which attack types are executed is not fixed.

---

## 7. Attack Timing

Attack execution uses configurable randomized durations.

### Normal Traffic

Normal traffic duration is randomly selected between:

- Minimum: 15 seconds
- Maximum: 40 seconds

### Attack Traffic

Attack duration is randomly selected between:

- Minimum: 5 seconds
- Maximum: 12 seconds

### Cooldown

After each attack, a cooldown period is introduced.

Cooldown duration is randomly selected between:

- Minimum: 10 seconds
- Maximum: 25 seconds

This produces alternating periods of normal activity, attack activity, and recovery/cooldown.

---

## 8. Attack State Communication

The preprocessing pipeline uses an attack-state MQTT topic to identify attack start and stop events.

The `DatasetManager` monitors the configured `ATTACK_STATE_TOPIC`.

When an attack-start event is received:

- `attack_active` is set to `True`.
- The current `attack_type` is stored.

When an attack-stop event is received:

- `attack_active` is set to `False`.
- The stored attack type is cleared.

This state information is subsequently used by the labeling component.

---

## 9. Attack-to-Dataset Integration

The attack framework is directly integrated with dataset generation.

The overall flow is:

AttackRunner
→ AttackManager
→ Attack Module
→ Industrial/MQTT Environment
→ MQTT Collector
→ Dataset Manager
→ Labeler
→ Dataset Writer
→ CSV Dataset

During an active attack, sensor records received by the preprocessing pipeline are labeled as attack records.

Normal traffic received outside an active attack period is labeled as normal traffic.

---

## 10. Dataset Generation Target

The current dataset-generation configuration specifies a target of:

`100,000 records`

The `AttackRunner` continues executing normal and attack scenarios until the configured target number of records is reached.

The runner checks the current record count before starting each attack and stops execution when the target is reached.

---

## 11. Attack Selection

The configured attack weights are:

- DoS: 25%
- Replay: 25%
- Injection: 25%
- Spoofing: 25%

The current `AttackRunner` implementation randomizes the attack order using shuffling.

Therefore, the configured weights represent the intended attack-selection configuration, while the currently implemented runner primarily uses randomized ordering rather than weighted sampling.

---

## 12. Threaded Execution

Attack execution is monitored through attack-manager threads.

After an attack is started, the runner waits until the active attack threads have completed before beginning the cooldown period.

This ensures that the dataset-generation process does not immediately transition to the next scenario while an earlier attack is still executing.

---

## 13. Dataset Labeling

The attack framework provides the context required by the preprocessing pipeline to generate labels.

Each final dataset record contains:

- `attack_type`
- `label`

The binary label is:

- `0` — Normal
- `1` — Attack

When an attack is active, the corresponding attack type is stored in the record.

When no attack is active, the record is labeled as normal.

---

## 14. Modular Design

Each attack is implemented as a separate module.

This provides:

- Independent attack implementation
- Reusable attack components
- Centralized execution management
- Easy addition of new attack types
- Randomized attack sequencing
- Integration with automated dataset generation

Additional attack modules can be added without redesigning the complete dataset-generation pipeline.

---

## 15. Current Implementation Status

The following components are implemented:

- DoS attack module
- Replay attack module
- Injection attack module
- Spoofing attack module
- Attack Manager
- Dynamic Attack Runner
- Randomized attack ordering
- Configurable attack duration
- Normal-traffic duration
- Cooldown duration
- Attack-state communication
- Integration with dataset labeling
- Integration with automatic dataset generation

---

## 16. Limitations

The current attack framework operates against a simulated Industrial IoT environment.

The exact behavior and realism of each attack depend on the corresponding attack-module implementation and the simulated MQTT environment.

Further attack scenarios and more sophisticated attack parameterization can be added in future development.

---

## 17. Phase 2 Outcome

Phase 2 establishes the cyber-attack simulation framework required for LightX-IDS dataset generation.

The modular framework can execute multiple attack types, randomize their execution order, coordinate attack timing, communicate attack state to the preprocessing pipeline, and provide the context required for generating labeled attack traffic.