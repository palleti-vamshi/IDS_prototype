# LightX-IDS — Folder Structure

## 1. Overview

The LightX-IDS project is organized into separate directories for the backend, frontend, dataset engineering, datasets, documentation, backups, and supporting utilities.

The structure separates the different stages of the system while keeping dataset processing and application development modular.

## 2. Project Root Structure


IDS_prototype/

│

├── backend/

├── dataset/

├── dataset_engineering/

├── backups/

├── docs/

├── frontend/

└── …

The exact remaining root-level files and directories cannot be completely documented until the complete frontend and remaining project contents are provided.

## 3. Backend Structure

The backend contains the Industrial IoT simulation, attack simulation, MQTT collection, preprocessing, dataset generation, and backend application entry point.

Backend/

│

├── attacks/

│   ├── attack_manager.py

│   ├── dos_attack.py

│   ├── replay_attack.py

│   ├── injection_attack.py

│   └── spoofing_attack.py

│

├── industrial/

│   ├── config/

│   │   └── mqtt_config.py

│   └── simulator/

│       └── factory_simulator.py

│

├── preprocessing/

│   ├── __init__.py

│   ├── collector.py

│   ├── csv_export.py

│   ├── dataset_manager.py

│   ├── dataset_writer.py

│   ├── generation_config.py

│   ├── labeler.py

│   ├── parser.py

│   ├── pipeline.py

│   ├── preprocessing_config.py

│   ├── schemas.py

│   └── simulation_runner.py

│

├── tests/

│   ├── __init__.py

│   ├── test_collector.py

│   ├── test_csv_export.py

│   ├── test_dataset_manager.py

│   ├── test_dataset_writer.py

│   ├── test_labeler.py

│   ├── test_parser.py

│   └── test_pipeline.py

│

├── services/

├── utils/

├── datasets/

├── api/

├── core/

├── detection/

├── models/

├── main.py

└── generate_dataset.py

Backend Directory Responsibilities

Directory/File	Responsibility

Attacks/	Contains attack implementations and attack management.

Industrial/	Contains the industrial factory simulation and MQTT configuration.

Preprocessing/	Processes collected MQTT data and generates labeled datasets.

Tests/	Contains tests for preprocessing and collection components.

Services/	Reserved for backend service-layer functionality.

Utils/	Reserved for reusable backend utilities.

Api/	Backend API layer.

Core/	Core backend functionality and configuration.

Detection/	Intrusion-detection related functionality.

Models/	Backend/model-related components.

Datasets/	Backend-side dataset storage/output location.

Main.py	Backend application entry point.

Generate_dataset.py	Starts the automatic dataset-generation workflow.

The detailed contents of api/, core/, detection/, models/, services/, and utils/ cannot be filled in from the backend files currently provided.

## 4. Backend Preprocessing Structure

The preprocessing module forms the main dataset-generation pipeline.

Backend/preprocessing/

│

├── __init__.py

├── collector.py

├── csv_export.py

├── dataset_manager.py

├── dataset_writer.py

├── generation_config.py

├── labeler.py

├── parser.py

├── pipeline.py

├── preprocessing_config.py

├── schemas.py

└── simulation_runner.py

Collector.py

Implements MQTTCollector.

Responsibilities:

Connect to the MQTT broker.

Subscribe to configured MQTT topics.

Receive MQTT messages.

Convert received messages into RawMQTTMessage objects.

Forward messages to the preprocessing callback.

Schemas.py

Defines the data contracts used by preprocessing.

The three main data structures are:

RawMQTTMessage

ParsedSensorRecord

LabeledRecord

They represent the progression from raw MQTT data to parsed data and finally labeled dataset records.

Parser.py

Converts RawMQTTMessage objects into ParsedSensorRecord objects.

It:

Decodes JSON payloads.

Validates that the payload is a dictionary.

Extracts sensor information.

Converts sensor values to floating-point values.

Rejects invalid messages.

Labeler.py

Converts parsed sensor records into LabeledRecord objects.

It assigns:

Label = 0

For normal traffic and:

Label = 1

When an attack is active.

The attack type is stored in attack_type.

Dataset_writer.py

Maintains labeled records in memory.

It provides operations to:

Add records.

Retrieve records.

Clear records.

Count records.

Csv_export.py

Exports labeled records into a CSV file.

The records are converted from dataclass objects into dictionaries before being written.

Dataset_manager.py

Coordinates the preprocessing components.

Its main responsibilities are:

Raw MQTT Message

        |

        V

Message Parser

        |

        V

Labeler

        |

        V

Dataset Writer

        |

        V

CSV Exporter

It also monitors attack-state events so that records received during an attack can be assigned the appropriate attack label and attack type.

Pipeline.py

Connects the MQTT collector and dataset manager.

The main flow is:

MQTTCollector

      |

      V

DatasetManager

      |

      +à MessageParser

      |

      +à Labeler

      |

      +à DatasetWriter

      |

      +à CSVExporter

The MQTT collector runs in a background thread.

Simulation_runner.py

Starts and stops the Industrial IoT factory simulator in a background thread.

Generation_config.py

Contains dataset-generation parameters, including:

Target dataset size

Normal traffic duration

Attack duration

Cooldown duration

Attack weights

The configured target dataset size is:

100,000 records

## 5. Backend Attack Structure

The attack subsystem is located in:

Backend/attacks/

The documented attack types include:

DoS

Replay

Injection

Spoofing

The AttackRunner dynamically creates and executes these attack scenarios.

Attack order is randomized during dataset generation.

The attack duration and cooldown duration are also randomized within the configured ranges.

## 6. Backend Dataset Generation

The automatic dataset-generation entry point is:

Backend/generate_dataset.py

The overall workflow is:

Factory Simulator

        |

        V

Dataset Pipeline

        |

        V

Attack Runner

        |

        V

Dataset Manager

        |

        V

CSV Dataset

The generator starts the simulator, starts the preprocessing pipeline, executes attack scenarios, exports the dataset, and then stops the running components.

## 7. Dataset Engineering Structure

The dataset-engineering module is organized separately from the backend preprocessing pipeline.

Dataset_engineering/

│

├── datasets/

│   ├── raw/

│   │   └── ton_iot/

│   │       ├── Train_Test_IoT_Modbus.csv

│   │       ├── Train_Test_IoT_Thermostat.csv

│   │       ├── Train_Test_IoT_Weather.csv

│   │       └── train_test_network.csv

│   ├── processed/

│   │   ├── modbus_clean.csv

│   │   ├── network_clean.csv

│   │   ├── thermostat_clean.csv

│   │   ├── weather_clean.csv

│   │   ├── Train_Test_IoT_Modbus_clean.csv

│   │   ├── Train_Test_IoT_Thermostat_clean.csv

│   │   ├── Train_Test_IoT_Weather_clean.csv

│   │   └── train_test_network_clean.csv

│   └── standardized/

│       ├── modbus_final.csv

│       ├── network_final.csv

│       ├── thermostat_final.csv

│       ├── weather_final.csv

│       └── lightx_combined.csv

│

├── src/

│   ├── profiling/

│   │   └── profiler.py

│   ├── cleaning/

│   │   └── cleaner.py

│   ├── standerdization/

│   │   └── standerizer.py

│   └── reporting/

│       └── combine.py

│

└── docs/

    └── datasets/

## 8. Dataset Engineering Source Structure

Src/profiling/

Contains:

Profiler.py

The profiler generates information about:

Dataset shape

Data types

Null values

Duplicate records

Descriptive statistics

Binary labels

Attack types

Src/cleaning/

Contains:

Cleaner.py

The cleaner:

Removes exact duplicate rows.

Converts placeholder null values where required.

Removes rows with missing labels.

Removes rows with missing or empty attack types.

Writes cleaned datasets.

Src/standerdization/

Contains:

Standerizer.py

The standardizer maps dataset-specific column names to the LightX-IDS schema.

The directory name is currently spelled standerdization in the project structure.

Src/reporting/

Contains:

Combine.py

This module combines the standardized Modbus, Thermostat, Weather, and Network datasets into:

Lightx_combined.csv

## 9. Dataset Engineering Documentation

The dataset-engineering documentation is stored under:

Dataset_engineering/docs/datasets/

The documented files include:

Dataset_engineering/docs/datasets/

│

├── modbus_report.md

├── thermostat_report.md

├── weather_report.md

├── network_report.md

├── ton_iot.md

│

├── profiling/

│   ├── modbus_profile.txt

│   ├── network_profile.txt

│   ├── thermostat_profile.txt

│   └── weather_profile.txt

│

└── cleaning/

The cleaning/ directory is currently empty.

## 10. Root Dataset Structure

Generated LightX-IDS datasets are also stored at the project root under:

Dataset/

The currently provided files are:

Dataset/

├── lightx_ids_raw_1k.csv

├── lightx_ids_raw_10k.csv

└── lightx_ids_raw_100k.csv

These represent generated raw dataset versions at different dataset sizes.

## 11. Backup Structure

Backup datasets are stored under:

Backups/

The currently provided backup is:

Backups/

└── lightx_ids_raw_100k_backup.csv

## 12. Frontend Structure

The frontend is a React-based application using Vite and the previously provided project configuration.

The documented frontend pages/components include:

Frontend/

├── pages/

│   ├── Dashboard/

│   ├── Sensors/

│   ├── AttackMonitoring/

│   ├── IDSPrediction/

│   ├── DatasetAnalytics/

│   ├── SystemLogs/

│   ├── Settings/

│   ├── Login/

│   └── NotFound/

│

├── components/

├── hooks/

├── services/

└── …

The frontend contains routes for:

/

 /sensors

 /attacks

 /prediction

 /dataset

 /logs

 /settings

 /login

The exact complete frontend directory tree cannot be filled in until the complete frontend contents are included.

## 13. Documentation Structure

The project documentation is maintained under:

Docs/

The architecture documentation includes:

Docs/

└── architecture/

    ├── 01_SYSTEM_ARCHITECTURE.md

    ├── 02_DATA_FLOW.md

    └── 03_FOLDER_STRUCTURE.md

Additional documentation directories and files should be documented as they are completed.

## 14. Separation of Responsibilities

The project structure separates responsibilities into major layers:

Industrial Simulation

        |

        V

Attack Simulation

        |

        V

Data Collection

        |

        V

Backend Preprocessing

        |

        V

Dataset Engineering

        |

        V

Machine Learning

        |

        V

Backend API

        |

        V

Frontend

This separation allows individual components to be developed, tested, and modified without requiring the entire project to be rewritten.

## 15. Testing Structure

The backend preprocessing tests are located under:

Backend/tests/

The provided tests cover:

Test_collector.py

Test_csv_export.py

Test_dataset_manager.py

Test_dataset_writer.py

Test_labeler.py

Test_parser.py

Test_pipeline.py

These tests exercise individual preprocessing components and basic end-to-end pipeline behavior.

## 16. Empty or Incomplete Directories

The following directories/files were provided as empty or without sufficient implementation details:

Backend/services/

Backend/utils/

Backend/preprocessing/preprocessing_config.py

Dataset_engineering/docs/datasets/cleaning/

Their detailed responsibilities cannot be filled in beyond their currently known locations.

The detailed contents of the backend API, detection, models, core modules, and complete frontend implementation have not been fully provided in the current documentation source material and therefore cannot be filled in accurately at this stage.

## 17. Summary

The LightX-IDS project uses a modular folder structure separating:

Industrial simulation

Cyberattack simulation

MQTT data collection

Dataset preprocessing

Dataset engineering

Dataset storage

Dataset backups

Backend functionality

Frontend functionality

Testing

Documentation

The most important data-processing separation is:

Backend/

    Simulation + Attack Generation + Live Preprocessing

Dataset_engineering/

    External Dataset Profiling + Cleaning + Standardization + Combination

Dataset/

    Generated Dataset Versions

Backups/

    Dataset Backups

Frontend/

    User Interface and Dashboard

Docs/

    Project Documentation

This organization supports independent development of the simulation, dataset-engineering, detection, backend, and frontend layers while maintaining clear data flow between them.