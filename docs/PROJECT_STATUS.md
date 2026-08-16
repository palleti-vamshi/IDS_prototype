# Project Status

## 1. Overview

LightX-IDS is currently under active development. The Industrial IoT simulation, attack simulation, dataset generation, dataset engineering, backend preprocessing, and frontend components have been implemented to varying degrees.

## 2. Phase Status

| Phase | Component | Status |
|---|---|---|
| Phase 0 | Project Planning | Completed |
| Phase 1 | Industrial Environment Simulation | Implemented |
| Phase 2 | Attack Framework | Implemented |
| Phase 3 | Dataset Generation | Implemented |
| Phase 4 | Machine Learning | Not completed / Cannot be filled with current information |
| Phase 5 | Dashboard | Frontend dashboard implemented |
| Phase 6 | Backend API | Backend structure exists; API implementation cannot be fully documented from the current information |
| Phase 7 | Frontend | Implemented |
| Phase 8 | Deployment | Cannot be filled with current information |

## 3. Industrial Environment

The project contains an Industrial IoT simulation environment with MQTT-based communication.

The simulator generates sensor traffic that can be collected by the preprocessing pipeline.

The available backend components include:

- Factory Simulator
- Temperature Sensor
- Pressure Sensor
- MQTT communication
- MQTT configuration

## 4. Attack Framework

The attack framework currently includes:

- DoS Attack
- Replay Attack
- Injection Attack
- Spoofing Attack

The `AttackRunner` dynamically executes attack scenarios in randomized order.

Normal traffic, attack periods, and cooldown periods are randomized within configured ranges.

The current dataset-generation configuration targets:

- 100,000 records
- Normal duration: 15–40 seconds
- Attack duration: 5–12 seconds
- Cooldown duration: 10–25 seconds

## 5. Dataset Generation

The automatic dataset-generation pipeline has been implemented.

The generation workflow consists of:

1. Starting the Industrial IoT simulator
2. Starting the preprocessing pipeline
3. Collecting MQTT messages
4. Processing sensor messages
5. Executing randomized attack scenarios
6. Labeling collected records
7. Exporting the generated dataset

The generated dataset is configured to be saved as:

`dataset/lightx_ids_dataset.csv`

Available generated dataset files include:

- `lightx_ids_raw_1k.csv`
- `lightx_ids_raw_10k.csv`
- `lightx_ids_raw_100k.csv`

A backup of the 100K dataset is also maintained.

## 6. Dataset Engineering

The dataset-engineering workflow has been implemented for TON-IoT datasets.

The current workflow includes:

- Profiling
- Cleaning
- Standardization
- Combining

The following TON-IoT datasets have been processed:

- Modbus
- Thermostat
- Weather
- Network

### Processed Dataset Sizes

| Dataset | Original Rows | Final Rows |
|---|---:|---:|
| Modbus | 31,106 | 17,792 |
| Thermostat | 32,774 | 32,350 |
| Weather | 39,260 | 39,260 |
| Network | 211,043 | 190,474 |

The standardized datasets include:

- `modbus_final.csv`
- `thermostat_final.csv`
- `weather_final.csv`
- `network_final.csv`

A combined standardized dataset is also present:

`lightx_combined.csv`

## 7. Backend Preprocessing

The backend preprocessing pipeline contains the following components:

- MQTT Collector
- Message Parser
- Labeler
- Dataset Manager
- Dataset Writer
- CSV Exporter
- Dataset Pipeline
- Dataset Generation Configuration
- Simulation Runner
- Attack Runner
- Data Schemas

The preprocessing flow is:

```text
MQTT Broker
    ↓
MQTT Collector
    ↓
Raw MQTT Message
    ↓
Message Parser
    ↓
Parsed Sensor Record
    ↓
Labeler
    ↓
Labeled Record
    ↓
Dataset Writer
    ↓
CSV Exporter