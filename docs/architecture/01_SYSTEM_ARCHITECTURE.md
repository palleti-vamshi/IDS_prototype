# LightX-IDS System Architecture 

 

## 1. Overview 

 

LightX-IDS (Lightweight Industrial Intrusion Detection System) is an Industrial IoT cybersecurity system designed to simulate an industrial environment, generate normal and attack traffic, prepare datasets, train machine-learning models, detect anomalous activity, and present the results through a web-based dashboard. 

 

The system is organized into multiple layers so that industrial simulation, attack generation, dataset engineering, machine learning, backend services, and frontend visualization can be developed and tested independently. 

 

The major architectural layers are: 

 

1. Industrial Environment Simulation 

2. Attack Simulation 

3. Dataset Engineering 

4. Machine Learning and Intrusion Detection 

5. Backend API 

6. Frontend Dashboard 

7. Deployment 

 

The overall architecture follows a pipeline: 

 

Industrial Environment 

        | 

        v 

Sensor / Device Data 

        | 

        v 

Attack Simulation 

        | 

        v 

Raw Dataset 

        | 

        v 

Dataset Cleaning 

        | 

        v 

Dataset Standardization 

        | 

        v 

Combined LightX Dataset 

        | 

        v 

Machine Learning / IDS 

        | 

        v 

Backend API 

        | 

        v 

Frontend Dashboard 

 

The architecture is designed to support both offline dataset-based analysis and, eventually, real-time intrusion detection. 

 

--- 

 

## 2. High-Level System Architectur
 

+--------------------------------------------------------------+ 

|                       LightX-IDS                              | 

+--------------------------------------------------------------+ 

 

                         Industrial Layer 

                                | 

                                v 

                  +--------------------------+ 

                  | Industrial Environment   | 

                  |      Simulation          | 

                  +--------------------------+ 

                                | 

                                v 

                  +--------------------------+ 

                  | Sensors / IoT Devices    | 

                  | Temperature / Pressure   | 

                  | Thermostat / Modbus      | 

                  +--------------------------+ 

                                | 

                                v 

                  +--------------------------+ 

                  | MQTT / Device Traffic    | 

                  +--------------------------+ 

                                | 

                                v 

                  +--------------------------+ 

                  | Attack Simulation        | 

                  | Injection / DDoS /       | 

                  | Backdoor / Password /     | 

                  | Scanning / XSS / etc.    | 

                  +--------------------------+ 

                                | 

                                v 

                  +--------------------------+ 

                  | Dataset Generation       | 

                  +--------------------------+ 

                                | 

                                v 

                  +--------------------------+ 

                  | Dataset Engineering      | 

                  | Profiling                 | 

                  | Cleaning                  | 

                  | Standardization           | 

                  | Reporting                 | 

                  +--------------------------+ 

                                | 

                                v 

                  +--------------------------+ 

                  | LightX Combined Dataset  | 

                  +--------------------------+ 

                                | 

                                v 

                  +--------------------------+ 

                  | Machine Learning / IDS   | 

                  | Training & Detection     | 

                  +--------------------------+ 

                                | 

                                v 

                  +--------------------------+ 

                  | Backend API              | 

                  | FastAPI / Services       | 

                  +--------------------------+ 

                                | 

                                v 

                  +--------------------------+ 

                  | React Frontend Dashboard | 

                  +--------------------------+ 

                                | 

                                v 

                  +--------------------------+ 

                  | Monitoring & Analytics   | 

                  +--------------------------+ 
## 3. Architectural Components 

### 3.1 Industrial Environment Simulation 

The industrial simulation layer represents the factory environment used for generating Industrial IoT traffic. 

The simulator represents devices and sensors that produce measurements such as: 

Device ID 

Temperature 

Pressure 

Sensor status 

Timestamp 

Device state 

Other industrial sensor values 

The simulator is intended to provide a controlled environment in which normal industrial activity can be reproduced consistently. 

The simulated environment can communicate using Industrial IoT communication mechanisms such as MQTT. 

The generated sensor traffic forms the baseline for normal system behavior and provides the input on which attack scenarios can be applied. 

 

### 3.2 MQTT Communication Layer 

MQTT is used as the communication mechanism for IoT-style sensor messaging in the industrial environment. 

The communication flow can be represented as: 

+------------------+ 

| Sensor / Device  | 

+------------------+ 

         | 

         | MQTT Message 

         v 

+------------------+ 

| MQTT Broker      | 

+------------------+ 

         | 

         v 

+------------------+ 

| Subscriber /     | 

| Monitoring Layer | 

+------------------+

MQTT messages can contain sensor readings and device-related information. 

The communication layer provides a realistic mechanism for producing Industrial IoT traffic before attack simulation and detection are applied. 

 

### 3.3 Attack Simulation 

The attack simulation layer introduces malicious activity into the otherwise normal industrial environment. 

The project datasets contain multiple attack categories depending on the source dataset. 

Observed attack categories include: 

Injection 

Backdoor 

Password attacks 

DDoS 

DoS 

Ransomware 

XSS 

Scanning 

MITM 

Normal traffic is represented using the label: 

0 = Normal 

Attack traffic is represented using: 

1 = Attack 

The attack type is retained separately as a multiclass field. 

Example: 

label = 0 

attack_type = normal 

or: 

label = 1 

attack_type = injection 

This allows LightX-IDS to support both binary intrusion detection and attack-type classification. 

 

## 4. Dataset Engineering Architecture 

The dataset engineering layer converts raw Industrial IoT and network datasets into a consistent format suitable for machine-learning workflows. 

The current dataset engineering workflow uses the TON-IoT datasets containing: 

Modbus 

Thermostat 

Weather 

Network 

The processing pipeline is: 

Raw TON-IoT Dataset 

        | 

        v 

     Profiling 

        | 

        v 

     Cleaning 

        | 

        v 

  Standardization 

        | 

        v 

 Individual Final Datasets 

        | 

        v 

     Combining 

        | 

        v 

LightX Combined Dataset 

### 4.1 Dataset Profiling 

Profiling is performed before cleaning to understand the structure and quality of each dataset. 

The profiler checks: 

- Dataset shape 

- Data types 

- Null values 

Duplicate rows 

Numeric statistics 

Label distribution 

Attack-type distribution 

The profiling implementation is located at: 

dataset_engineering/src/profiling/profiler.py 

The generated profiling information is stored under: 

dataset_engineering/docs/datasets/profiling/ 

 

### 4.2 Dataset Cleaning 

The cleaning layer removes exact duplicate records and invalid label/type records. 

The cleaning implementation is located at: 

dataset_engineering/src/cleaning/cleaner.py 

The cleaner also handles TON-IoT placeholder values where applicable. 

In the network dataset, values represented by - in DNS, SSL, HTTP, and related fields indicate that a particular protocol-specific field is not applicable to that connection. 

These placeholders are converted to actual missing values during cleaning. 

The current cleaning process does not attempt to replace such values with artificial sensor measurements. 

 

### 4.3 Dataset Standardization 

The standardization layer maps dataset-specific column names to the common LightX-IDS schema. 

The standardization implementation is located at: 

dataset_engineering/src/standerdization/standerizer.py 

The common schema uses fields such as: 

sensor_reading_1 

sensor_reading_2 

sensor_reading_3 

sensor_reading_4 

label 

attack_type 

timestamp 

Network-specific fields are represented using: 

source_ip 

destination_ip 

source_port 

destination_port 

protocol 

service 

duration 

src_bytes 

dst_bytes 

label 

attack_type 

The purpose of standardization is to make heterogeneous datasets easier to process using a common downstream workflow. 

 

## 5. Current Dataset Architecture 

The current dataset engineering repository contains raw, processed, and standardized versions of the datasets. 

dataset_engineering/ 

| 

+-- datasets/ 

|   | 

|   +-- raw/ 

|   |   | 

|   |   +-- ton_iot/ 

|   |       +-- Train_Test_IoT_Modbus.csv 

|   |       +-- Train_Test_IoT_Thermostat.csv 

|   |       +-- Train_Test_IoT_Weather.csv 

|   |       +-- train_test_network.csv 

|   | 

|   +-- processed/ 

|   |   +-- modbus_clean.csv 

|   |   +-- thermostat_clean.csv 

|   |   +-- weather_clean.csv 

|   |   +-- network_clean.csv 

|   |   +-- Train_Test_IoT_Modbus_clean.csv 

|   |   +-- Train_Test_IoT_Thermostat_clean.csv 

|   |   +-- Train_Test_IoT_Weather_clean.csv 

|   |   +-- train_test_network_clean.csv 

|   | 

|   +-- standardized/ 

|       +-- modbus_final.csv 

|       +-- thermostat_final.csv 

|       +-- weather_final.csv 

|       +-- network_final.csv 

|       +-- lightx_combined.csv 

| 

+-- src/ 

    | 

    +-- profiling/ 

    |   +-- profiler.py 

    | 

    +-- cleaning/ 

    |   +-- cleaner.py 

    | 

    +-- standerdization/ 

    |   +-- standerizer.py 

    | 

    +-- reporting/ 

        +-- combine.py 

 

##  6. Standardized Dataset Flow 

The four standardized datasets are combined into a single LightX dataset. 

+---------------------+ 

|   Modbus Final      | 

|    17,792 rows      | 

+---------------------+ 

          | 

          | 

+---------------------+ 

| Thermostat Final    | 

|    32,350 rows      | 

+---------------------+ 

          | 

          | 

+---------------------+ 

| Weather Final       | 

|    39,260 rows      | 

+---------------------+ 

          | 

          | 

+---------------------+ 

| Network Final       | 

|   190,474 rows      | 

+---------------------+ 

          | 

          v 

+---------------------+ 

| Combining           | 

+---------------------+ 

          | 

          v 

+---------------------+ 

| LightX Combined     | 

| Dataset             | 

+---------------------+ 

The combined dataset is generated by: 

dataset_engineering/src/reporting/combine.py 

The resulting file is: 

datasets/standardized/lightx_combined.csv 

The combined dataset provides a common data source for subsequent machine-learning and intrusion-detection stages. 

 

## 7. Machine Learning / IDS Layer 

The machine-learning layer uses the processed and standardized datasets to develop intrusion-detection capabilities. 

The intended workflow is: 

LightX Dataset 

      | 

      v 

Feature Preparation 

      | 

      v 

Train / Test Split 

      | 

      v 

Model Training 

      | 

      v 

Model Evaluation 

      | 

      v 

Attack Prediction 

      | 

      v 

Prediction Result 

The system is intended to support: 

Binary attack detection 

Attack-type classification 

Performance evaluation 

False-positive analysis 

Explainability 

Real-time prediction 

The exact final ML model, feature-selection strategy, model metrics, and trained-model architecture cannot be filled in at this stage unless the completed machine-learning implementation and results are provided. 

 

## 8. Backend Architecture 

The backend acts as the interface between the machine-learning/detection components and the frontend dashboard. 

The backend is organized into components including: 

backend/ 

| 

+-- api/ 

+-- attacks/ 

+-- core/ 

+-- datasets/ 

+-- detection/ 

+-- industrial/ 

+-- models/ 

+-- preprocessing/ 

+-- services/ 

+-- main.py 

The backend is intended to provide API access to system functionality such as: 

Sensor information 

Attack monitoring 

IDS predictions 

Dataset statistics 

System logs 

Configuration/settings 

The exact API endpoints, request/response schemas, authentication implementation, database configuration, and deployment configuration cannot be filled in here without the final backend implementation/API documentation. 

 

## 9. Frontend Architecture 

The frontend provides the user-facing monitoring and analytics interface. 

The frontend is implemented using: 

React 

Vite 

Tailwind CSS 

React Router 

Axios 

React Icons 

Charting components 

The frontend contains the following major pages: 

Dashboard 

Sensors 

Attack Monitoring 

IDS Prediction 

Dataset Analytics 

System Logs 

Settings 

Login 

The routing structure includes paths corresponding to: 

/ 

 /sensors 

 /attacks 

 /prediction 

 /dataset 

 /logs 

 /settings 

 /login 

The frontend communicates with the backend through API service modules. 

The intended communication architecture is: 

+--------------------------+ 

| React Frontend           | 

|                          | 

| Dashboard                | 

| Sensors                  | 

| Attack Monitoring        | 

| IDS Prediction           | 

| Dataset Analytics        | 

| System Logs              | 

| Settings                 | 

+------------+-------------+ 

             | 

             | HTTP API 

             v 

+--------------------------+ 

| Backend API              | 

+------------+-------------+ 

             | 

       +-----+-----+ 

       |           | 

       v           v 

+----------+  +-----------+ 

| Detection|  | Datasets  | 

| / Models |  | / Services| 

+----------+  +-----------+ 

 

## 10. Dashboard Architecture 

The dashboard is responsible for presenting the current system state in a human-readable form. 

Dashboard components include statistical cards and sensor visualizations. 

Examples of dashboard components include: 

StatCard 

TemperatureChart 

PressureChart 

The dashboard is designed to provide a centralized view of: 

Industrial sensor activity 

Current system statistics 

Attack activity 

IDS predictions 

Dataset analytics 

System events 

The exact final dashboard metrics depend on the backend API and completed detection implementation. 

 

## 11. Frontend API Communication 

The frontend contains an API service layer that abstracts communication with the backend. 

The frontend uses an API base URL configured through the Vite environment configuration. 

The development API configuration used during development is: 

http://localhost:8000/api 

This allows the frontend to communicate with the locally running backend while keeping the API address configurable. 

The frontend API layer is intended to provide separate service functions for: 

Sensors 

Attacks 

Predictions 

Dataset statistics 

## 12. Authentication Architecture 

The frontend contains a login page and authentication-related hooks. 

The final authentication mechanism depends on the completed backend authentication implementation. 

The exact authentication provider, token format, persistence mechanism, user roles, and authorization rules cannot be filled in until the final authentication implementation is confirmed. 

 

## 13. Data Flow 

The complete intended data flow of LightX-IDS is: 

Industrial Simulation 

        | 

        v 

Sensor / IoT Messages 

        | 

        v 

Attack Simulation 

        | 

        v 

Traffic / Event Data 

        | 

        v 

Dataset Generation 

        | 

        v 

Raw Dataset 

        | 

        v 

Profiling 

        | 

        v 

Cleaning 

        | 

        v 

Standardization 

        | 

        v 

LightX Combined Dataset 

        | 

        v 

Feature Preparation 

        | 

        v 

ML Model 

        | 

        v 

IDS Prediction 

        | 

        v 

Backend API 

        | 

        v 

Frontend Dashboard 

        | 

        v 

Human Monitoring / Analysis 

 

## 14. Separation of Responsibilities 

The architecture separates responsibilities between components. 

Industrial Simulation 

Responsible for: 

Simulating industrial devices 

Generating sensor readings 

Producing IoT communication 

Attack Simulation 

Responsible for: 

Generating malicious scenarios 

Producing attack traffic/events 

Associating events with attack categories 

Dataset Engineering 

Responsible for: 

Profiling datasets 

Cleaning datasets 

Standardizing schemas 

Combining datasets 

Producing reusable datasets for ML 

Machine Learning 

Responsible for: 

Training intrusion-detection models 

Predicting attack activity 

Classifying attack types 

Evaluating model performance 

Supporting explainability 

Backend 

Responsible for: 

Exposing system functionality through APIs 

Connecting detection/model components to the frontend 

Providing sensor, attack, prediction, and dataset information 

Frontend 

Responsible for: 

Visualizing system state 

Displaying sensor information 

Monitoring attacks 

Displaying IDS predictions 

Presenting dataset analytics 

Showing system logs 

Providing configuration interfaces 

 

## 15. Current Implementation Status 

Based on the currently available project structure and implementation information: 

Implemented / Available 

TON-IoT raw datasets 

Dataset profiling 

Dataset cleaning 

Dataset standardization 

Dataset combination 

Dataset reports 

LightX combined dataset 

React/Vite frontend structure 

Frontend routing 

Dashboard components 

Sensor charts 

Attack monitoring page structure 

IDS prediction page structure 

Dataset analytics page structure 

System logs page structure 

Settings page structure 

Login page structure 

Frontend API service structure 

Production frontend build 

Cannot be filled in currently 

The following architectural details cannot be stated as completed until the relevant implementation/results are confirmed: 

Final ML model architecture 

Final ML accuracy, precision, recall, F1-score, and other evaluation metrics 

Final false-positive reduction method 

Final explainability implementation 

Confirmed real-time detection pipeline 

Complete backend API endpoint specification 

Database architecture, if any 

Production authentication implementation 

Final deployment infrastructure 

Production hosting configuration 

Final CI/CD architecture 

These should be updated in this document once the corresponding implementation is finalized. 

 

## 16. Design Principles 

LightX-IDS follows the following architectural principles: 

Modularity 

Each major stage is separated so that dataset engineering, machine learning, backend development, and frontend development can evolve independently. 

Reusability 

The dataset-engineering pipeline is designed to process multiple datasets using a common workflow. 

Standardization 

Different source datasets are mapped into a common LightX-IDS representation wherever possible. 

Extensibility 

The architecture allows additional datasets, attack types, ML models, sensors, and dashboard features to be added later. 

Separation of Concerns 

Data processing, detection, API services, and presentation are maintained as separate layers. 

Explainability 

The system is intended to provide understandable intrusion-detection results rather than only producing a binary prediction. 

Real-Time Readiness 

Although the current workflow includes offline dataset processing, the architecture is designed to support eventual real-time sensor and attack monitoring. 

 

## 17. Summary 

LightX-IDS is structured as a layered Industrial IoT intrusion-detection platform. 

The system begins with an industrial environment and IoT traffic, introduces or captures attack activity, processes the resulting data through a reusable dataset-engineering pipeline, and prepares the data for machine-learning-based intrusion detection. 

The resulting predictions are exposed through a backend API and presented through a React-based dashboard. 

The architecture therefore connects: 

Industrial Environment 

        | 

        v 

IoT Communication 

        | 

        v 

Attack Simulation 

        | 

        v 

Dataset Engineering 

        | 

        v 

Machine Learning 

        | 

        v 

Intrusion Detection 

        | 

        v 

Backend API 

        | 

        v 

Frontend Dashboard 

This layered architecture provides the foundation for developing LightX-IDS as a lightweight, modular, and extensible Industrial IoT intrusion-detection system.