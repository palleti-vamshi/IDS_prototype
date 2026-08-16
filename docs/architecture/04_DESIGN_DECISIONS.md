# LightX-IDS — Design Decisions

## 1. Overview

This document records the major design decisions identified from the current LightX-IDS implementation.

The decisions are based on the implemented backend preprocessing pipeline, Industrial IoT simulation, attack-generation workflow, dataset-engineering pipeline, and generated dataset structure.

## 2. Modular Architecture

### Decision

The system is divided into separate modules for industrial simulation, attack simulation, data collection, preprocessing, dataset engineering, backend services, and frontend functionality.

### Rationale

A modular structure allows each stage of the system to be developed and tested independently.

For example:

- The factory simulator is responsible for generating industrial sensor traffic.

- The attack subsystem is responsible for generating attack scenarios.

- The MQTT collector is responsible for receiving messages.

- The preprocessing pipeline parses and labels messages.

- Dataset engineering handles external datasets separately.

- The frontend provides visualization and interaction.

This separation reduces coupling between components and makes the system easier to extend.

## 3. MQTT for Industrial IoT Communication

### Decision

MQTT is used as the communication mechanism between the Industrial IoT simulator and the data-collection pipeline.

### Rationale

The implemented `MQTTCollector` uses the Paho MQTT client to connect to the configured MQTT broker, subscribe to configured topics, and receive sensor messages.

MQTT messages are converted into `RawMQTTMessage` objects before entering the preprocessing pipeline.

The use of MQTT also keeps the simulation close to an Industrial IoT communication model.

## 4. Separation of Raw, Parsed, and Labeled Data

### Decision

The preprocessing pipeline uses three distinct data representations:

1. `RawMQTTMessage`

2. `ParsedSensorRecord`

3. `LabeledRecord`

### Rationale

Separating these stages prevents different responsibilities from being mixed together.

The flow is:

Raw MQTT Message

       |

       V

Parsed Sensor Record

       |

       V

Labeled Record

RawMQTTMessage preserves the information received from MQTT.

ParsedSensorRecord represents validated and structured sensor information.

LabeledRecord represents the final record that can be written to the generated dataset.

This provides a clear data contract between preprocessing components.

## 5. Event-Based Attack State Tracking

### Decision

Attack state is communicated through a dedicated MQTT attack-state topic.

### Rationale

The DatasetManager listens for attack-state events and maintains:

Attack_active

Attack_type

When an attack-start event is received, the manager records the active attack and its type.

When an attack-stop event is received, the attack state is cleared.

This allows normal sensor messages to be labeled according to the attack state at the time they are received.

The resulting behavior is:

Attack Start Event

        |

        V

Attack_active = True

Attack_type = <attack>

        |

        V

Sensor Messages

        |

        V

Label = 1

And after the attack ends:

Attack Stop Event

        |

        V

Attack_active = False

Attack_type = None

        |

        V

Sensor Messages

        |

        V

Label = 0

## 6. Binary Attack Label

### Decision

The generated dataset uses a binary label field:

0 = Normal

1 = Attack

### Rationale

The Labeler directly implements this distinction.

The binary label provides a simple target for intrusion detection while the separate attack_type field retains information about the specific attack.

This gives the dataset both:

Binary intrusion-detection information.

Multi-class attack information.

## 7. Separate Attack-Type Field

### Decision

The attack category is stored separately from the binary label using the attack_type field.

### Rationale

A binary label alone cannot distinguish between different attacks.

For example:

Label = 1

Attack_type = DoS

And:

Label = 1

Attack_type = Injection

Both represent malicious traffic but provide different attack categories.

Keeping these values separate allows the same dataset to support binary detection and attack-type analysis.

##  8. Randomized Attack Scheduling

### Decision

The automatic dataset generator randomizes the order and duration of attack scenarios.

### Rationale

AttackRunner maintains a list of available attacks and shuffles their order before executing them.

The current attack classes are:

DoSAttack

ReplayAttack

InjectionAttack

SpoofingAttack

Attack durations are selected randomly within the configured range.

Normal-traffic periods and cooldown periods are also randomized.

This prevents the generated dataset from following one fixed attack sequence.

## 9. Normal Traffic Between Attack Scenarios

### Decision

Normal traffic periods are inserted before attack scenarios, followed by cooldown periods after attacks.

### Rationale

The configured dataset-generation workflow uses:

Normal Traffic

      |

      V

Attack

      |

      V

Cooldown

      |

      V

Next Scenario

The current configuration defines:

Normal duration: 15–40 seconds

Attack duration: 5–12 seconds

Cooldown: 10–25 seconds

This creates transitions between normal and malicious traffic instead of generating attacks continuously.

## 10. Fixed Target Dataset Size

### Decision

The automatic dataset generator stops when the configured target number of records is reached.

### Current Configuration

TARGET_RECORDS = 100000

### Rationale

Using a target record count provides a deterministic stopping condition for dataset generation.

AttackRunner continuously checks the number of records stored by the DatasetWriter and stops when the target is reached.

## 11. In-Memory Dataset Writing Before Export

### Decision

The current preprocessing pipeline stores LabeledRecord objects in memory before exporting them to CSV.

### Rationale

The DatasetWriter provides a simple abstraction for accumulating records.

It supports:

Add_record()

Get_records()

Clear()

Record_count()

The collected records are subsequently passed to CSVExporter.

This keeps dataset collection separate from file-writing logic.

### Limitation

The current implementation is memory-based. Large-scale or long-running generation may require a streaming or incremental storage mechanism in a future version.

## 12. CSV as the Dataset Export Format

### Decision

Generated labeled records are exported as CSV.

### Rationale

The CSVExporter uses Python’s CSV functionality and writes the fields of LabeledRecord as dataset columns.

CSV provides a simple format that can be consumed by:

Data-analysis tools.

Python/Pandas workflows.

Machine-learning preprocessing pipelines.

Dataset inspection tools.

The current generated dataset output is:

Dataset/lightx_ids_dataset.csv

## 13. Separate Dataset Engineering Pipeline

### Decision

External cybersecurity datasets are processed through a separate dataset_engineering pipeline rather than being directly mixed with the simulator-generated dataset.

### Rationale

The project uses TON-IoT datasets containing Modbus, Thermostat, Weather, and Network data.

These datasets have different original schemas.

The dataset-engineering pipeline therefore performs:

Raw Dataset

     |

     V

Profiling

     |

     V

Cleaning

     |

     V

Standardization

     |

     V

Combination

This keeps external-dataset processing independent from the real-time MQTT preprocessing pipeline.

## 14. Dataset Profiling Before Cleaning

### Decision

Each external dataset is profiled before cleaning.

### Rationale

The profiler records:

Dataset shape.

Data types.

Null counts.

Duplicate counts.

Numerical statistics.

Binary label distribution.

Attack-type distribution.

This provides information required to make cleaning decisions based on the actual dataset characteristics.

## 15. Removal of Exact Duplicate Records

### Decision

Exact duplicate rows are removed during dataset cleaning.

### Rationale

The cleaning script uses Pandas drop_duplicates().

The amount of duplication differs significantly between datasets.

For example:

Modbus contains 13,314 duplicate rows.

Thermostat contains 424 duplicate rows.

Weather contains no duplicate rows.

Network contains 20,569 duplicate rows.

Removing exact duplicates reduces repeated records while retaining the remaining data.

## 16. Handling Placeholder Null Values

### Decision

Placeholder values such as “-“ are treated as non-applicable values where appropriate rather than as valid categorical values.

### Rationale

The TON-IoT Network dataset uses “-“ in fields associated with DNS, SSL, HTTP, and related network metadata when those fields are not applicable.

The cleaning process converts these placeholders to actual missing values in the relevant columns.

This distinction is important because a missing DNS or HTTP field does not necessarily indicate corrupted data; it can simply mean that the corresponding protocol activity did not occur.

## 17. Preserve Attack Classes During Cleaning

### Decision

Attack types are retained rather than merged during dataset cleaning.

### Rationale

The dataset-engineering reports identify multiple attack categories.

For example, the Network dataset contains:

Backdoor

Ddos

Dos

Injection

Password

Ransomware

Scanning

Xss

Mitm

Dos and ddos are specifically retained as separate classes because the current processing treats them as distinct attack categories.

This preserves attack-type information for subsequent analysis and machine-learning work.

## 18. Standardized Common Schema

### Decision

The external datasets are mapped into a common LightX-IDS schema.

### Rationale

The source datasets use different column names and structures.

The standardizer maps dataset-specific fields into common names such as:

Label

Attack_type

Sensor_reading_1

Sensor_reading_2

Sensor_reading_3

Sensor_reading_4

Timestamp

For network data, the standardized schema includes fields such as:

Source_ip

Destination_ip

Source_port

Destination_port

Protocol

Service

Duration

Src_bytes

Dst_bytes

Label

Attack_type

This makes datasets from different sources easier to combine and process consistently.

## 19. Remove Unmapped Network Metadata During Standardization

### Decision

Only explicitly mapped network fields are retained in the final standardized Network dataset.

### Rationale

The standardizer creates a selected set of columns from the source dataset.

Additional fields such as detailed HTTP, SSL, DNS, and other metadata are not carried into the final standardized schema unless explicitly mapped.

This keeps the final schema focused on the fields selected for the LightX-IDS representation.

## 20. Combine Standardized Datasets After Processing

### Decision

The Modbus, Thermostat, Weather, and Network datasets are combined only after cleaning and standardization.

### Rationale

The combine.py script reads:

Modbus_final.csv

Thermostat_final.csv

Weather_final.csv

Network_final.csv

And combines them into:

Lightx_combined.csv

This ordering ensures that source-specific cleaning and schema mapping occur before combination.

## 21. Reusable Configuration

### Decision

Dataset-generation parameters are maintained in a dedicated configuration module.

### Rationale

Generation_config.py stores values such as:

TARGET_RECORDS

MIN_NORMAL_DURATION

MAX_NORMAL_DURATION

MIN_ATTACK_DURATION

MAX_ATTACK_DURATION

MIN_COOLDOWN

MAX_COOLDOWN

ATTACK_WEIGHTS

Keeping these parameters separate from execution logic makes dataset-generation behavior easier to modify.

## 22. Background Threads for Continuous Components

### Decision

The factory simulator and MQTT collector are started in background daemon threads.

### Rationale

Both the simulation and collection components need to operate continuously while the main dataset-generation workflow continues.

The use of background threads allows:

Main Generation Process

        |

        +---- Factory Simulator Thread

        |

        +---- MQTT Collector Thread

        |

        +---- Attack Runner

The current implementation therefore avoids blocking the main orchestration logic while the simulator and collector operate.

## 23. Component-Level Testing

### Decision

Individual preprocessing components have separate test scripts.

### Rationale

The project contains tests for:

Collector

CSV Exporter

Dataset Manager

Dataset Writer

Labeler

Parser

Pipeline

This provides a basic mechanism for validating individual parts of the preprocessing workflow before relying on the complete pipeline.

## 24. Design Decisions Still Pending

The following decisions cannot be filled accurately from the currently provided implementation:

Final backend API architecture.

Authentication and authorization strategy.

Database technology and persistence strategy.

ML model architecture and model-selection strategy.

Model serving/inference architecture.

Explainability implementation.

False-positive reduction strategy.

Real-time prediction API contract.

Frontend state-management architecture.

Frontend-to-backend API integration details.

Production deployment architecture.

Containerization strategy.

Logging and monitoring architecture.

Authentication/session-management implementation.

These should be documented once the corresponding backend, ML, deployment, and complete frontend implementations are finalized.