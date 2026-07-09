# 🛡️ LightX-IDS
### Lightweight Machine Learning-Based Intrusion Detection System for Industrial IoT

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-Supported-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

---

## 📖 Overview

**LightX-IDS** is a lightweight Machine Learning-based Intrusion Detection System (IDS) designed for **Industrial Internet of Things (IIoT)** environments.

Unlike conventional IDS solutions that focus solely on maximizing accuracy, LightX-IDS aims to achieve an optimal balance between:

- ⚡ Lightweight deployment
- 🎯 High intrusion detection accuracy
- 🚀 Fast inference
- 💾 Low memory footprint
- 🏭 Real-time Industrial IoT monitoring

The project is modular, scalable, and designed for deployment on resource-constrained edge devices.

---

# ✨ Features

- Industrial IoT Intrusion Detection
- Modular Machine Learning Pipeline
- Automated Feature Engineering
- Data Preprocessing Pipeline
- Hyperparameter Optimization
- Feature Importance Analysis
- Cross Validation
- Error Analysis
- Benchmark Generation
- Model Comparison
- Model Serialization
- Production-Ready Architecture

---

# 🏗️ Project Structure

```
IDS_prototype/
│
├── backend/
│   └── ml/
│       ├── preprocessing/
│       ├── feature_engineering/
│       ├── models/
│       ├── training/
│       ├── evaluation/
│       ├── experiments/
│       ├── reports/
│       ├── config.py
│       └── ...
│
├── frontend/
│
├── dataset/
│
├── README.md
└── requirements.txt
```

---

# ⚙️ Machine Learning Workflow

```
Dataset
    │
    ▼
Dataset Loader
    │
    ▼
Feature Engineering
    │
    ▼
Feature Selection
    │
    ▼
Train / Validation / Test Split
    │
    ▼
Preprocessing Pipeline
    │
    ▼
Model Training
    │
    ▼
Hyperparameter Optimization
    │
    ▼
Evaluation
    │
    ▼
Benchmarking
    │
    ▼
Model Export
```

---

# 🤖 Supported Models

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost

---

# 🔬 Feature Engineering

Current engineered features include:

- Value Change
- Duplicate Detection
- Device Message Count
- Sensor Message Count
- Time Delta
- Rolling Mean
- Rolling Standard Deviation
- Rolling Maximum
- Rolling Minimum
- Percentage Change
- Z-Score

---

# 📊 Model Evaluation

Each model is evaluated using:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Training Time
- Prediction Time
- Model Size

Additional reports generated automatically:

- Classification Report
- Confusion Matrix
- ROC Curve
- Precision-Recall Curve
- Feature Importance Report
- Benchmark Reports (CSV & JSON)

---

# 📈 Current Benchmark (100K Dataset)

| Model | Accuracy | Model Size |
|--------|----------|------------|
| Random Forest | **97.81%** | 66.89 MB |
| XGBoost | **97.79%** | 2.02 MB |
| Decision Tree | **97.36%** | **29 KB** |
| Logistic Regression | **97.22%** | **6 KB** |

---

# 🎯 Deployment Recommendation

### 🥇 Highest Accuracy

**Random Forest**

- Accuracy: **97.81%**

Suitable when computational resources are available.

---

### ⚡ Lightweight Deployment

**Decision Tree**

- Accuracy: **97.36%**
- Model Size: **29 KB**

Recommended for deployment on Industrial IoT edge devices where memory and computation are limited.

---

# 🚀 Getting Started

Clone the repository

```bash
git clone https://github.com/palleti-vamshi/IDS_prototype.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run benchmark

```bash
python -m backend.ml.experiments.experiment
```

---

# 🛣️ Project Roadmap

## ✅ Completed

- Dataset Loader
- Feature Engineering
- Feature Selection
- Dataset Splitter
- Preprocessing Pipeline
- ML Pipeline
- Model Factory
- Model Training
- Hyperparameter Optimization
- Evaluation Manager
- Error Analysis
- Feature Importance Analysis
- Benchmarking Framework
- Model Management

## 🚧 In Progress

- Threshold Optimization

## 🔜 Planned

- FastAPI Backend
- REST API Integration
- Frontend Dashboard
- Real-time MQTT Intrusion Detection
- Docker Deployment
- Explainable AI (SHAP)
- Cloud Deployment

---

# 👨‍💻 Authors

### **Vamshi Palleti**

- Machine Learning Development
- Backend Development
- System Architecture
- Model Optimization
- Evaluation Framework

### **Srinidhi**

- Frontend Development
- Dashboard UI Development
- Frontend Integration
- External Datasets cleaning

---

# 🎓 Academic Project

**LightX-IDS**

Lightweight Machine Learning-Based Intrusion Detection System for Industrial Internet of Things (IIoT)

Developed as a **Final Year B.Tech Project**.

---

# 📄 License

This project is released under the **MIT License**.