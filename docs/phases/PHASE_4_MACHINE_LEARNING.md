# Phase 4 — Machine Learning

## 1. Objective

Phase 4 implements a leakage-free, reproducible, and industrially grounded machine learning evaluation pipeline for the LightX-IDS intrusion detection system. The objective is to evaluate how lightweight and standard machine learning classifiers perform on realistic, multi-sensor industrial IoT telemetry without artificial dataset balancing, label leakage, or test-set optimization.

---

## 2. Machine Learning Pipeline Architecture

The Phase 4 machine learning pipeline is located in `backend/ml/` and follows a modular design:

```
Raw Telemetry (100K CSV)
       │
       ▼
[DatasetLoader] ──> Schema Validation (13 columns, sensor_code verified)
       │
       ▼
[FeatureGenerator] ──> Causal Stream Features (rolling_std, is_duplicate_value, time_delta, etc.)
       │
       ▼
[DatasetSplitter] ──> 80% Train / 10% Validation / 10% Test (Stratified or Temporal)
       │
       ├──> [FeatureGenerator.fit()] ──> Fit device stats on Train ONLY
       │
       ▼
[FeatureSelector] ──> Drops non-predictive columns (label, attack_type, timestamp, record_id, sequence_number)
       │
       ▼
[DatasetTransformer] ──> StandardScaler (numeric) + OneHotEncoder (categorical) fitted on Train ONLY
       │
       ▼
[ModelTrainer] ──> Trains Classifier (Logistic Regression, Decision Tree, Random Forest, XGBoost)
       │
       ▼
[ThresholdOptimizer] ──> Tunes operating threshold on Validation split ONLY using F1 objective
       │
       ▼
[ModelEvaluator] ──> Evaluates FROZEN threshold on untouched Test split exactly ONCE
       │
       ▼
[ErrorAnalyzer & FeatureImportance] ──> Per-attack recall, false positive breakdown, feature importance
```

---

## 3. Dataset Used for Machine Learning

The authoritative Phase 3 dataset is:
- `dataset/lightx_ids_dataset_100k.csv` (100,000 records × 13 columns)

Additional verified benchmark datasets:
- `dataset/lightx_ids_dataset_10k.csv` (10,000 records)
- `dataset/lightx_ids_dataset_1k.csv` (1,000 records)

### Telemetry Distribution
- **Normal Telemetry:** 56,843 records (56.84%)
- **Attack Telemetry:** 43,157 records (43.16%)
- **Physical Sensors:** 19 unique physical sensors across 6 industrial machines
- **Active Attack Classes:** 14 distinct attack classes (11 broad/global attacks + 3 localized attacks)

---

## 4. Features and Labels

### Predictive Features (18 Features)
1. **Physical Telemetry Values:** `value`
2. **Causal Stream Features:**
   - `value_change`: Difference from previous observation per sensor
   - `is_duplicate_value`: Flag indicating repeat of previous observation
   - `time_delta`: Inter-arrival time difference (seconds)
   - `rolling_mean`: 5-tick moving average per sensor
   - `rolling_std`: 5-tick rolling standard deviation
   - `rolling_max`: 5-tick rolling maximum
   - `rolling_min`: 5-tick rolling minimum
   - `percentage_change`: Normalized relative rate of change
3. **Training-Derived Deviation Features:**
   - `device_mean_deviation`: Difference from device mean learned on training data
   - `z_score`: Device-level standard score learned on training data
4. **Categorical Context:** `topic`, `device_id`, `sensor_code`, `sensor_type`, `unit`, `status`, `source`

### Excluded Non-Predictive Columns (Leakage Prevention)
- `label`, `attack_type`, `record_id`, `timestamp`, `sequence_number`, `device_message_count`, `sensor_message_count`

---

## 5. Supported Machine Learning Models

1. **Logistic Regression:**
   - Linear baseline, `C=50`, balanced class weighting, `solver='lbfgs'`, `max_iter=3000`.
2. **Decision Tree:**
   - Interpretable rule-based model, `criterion='entropy'`, `max_depth=10`, `min_samples_split=10`.
   - Highly lightweight (~0.01 MB footprint, 0.41s training time).
3. **Random Forest:**
   - 200 estimators, `criterion='entropy'`, `max_features='sqrt'`.
4. **XGBoost:**
   - Gradient boosted trees, 300 estimators, `learning_rate=0.05`, `max_depth=8`, `tree_method='hist'`.

---

## 6. Model Evaluation Results (100K Dataset)

### Authoritative Baseline (Random Stratified 80/10/10)
| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | FPR | FNR | Best Threshold |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost** | **88.82%** | **86.76%** | **87.44%** | **87.10%** | **0.9618** | **0.9576** | **10.13%** | **12.56%** | 0.40 |
| **Decision Tree** | 87.64% | 85.33% | 86.16% | 85.75% | 0.9525 | 0.9443 | 11.24% | 13.84% | 0.50 |
| **Random Forest** | 86.69% | 86.41% | 82.06% | 84.18% | 0.9386 | 0.9360 | 9.80% | 17.94% | 0.55 |
| **Logistic Regression** | 75.04% | 69.23% | 75.87% | 72.40% | 0.8136 | 0.7933 | 25.59% | 24.13% | 0.45 |

---

## 7. Key Findings & Insights

1. **Physical Feature Generalization:**
   - When all physical identifiers (`device_id`, `sensor_code`, `topic`) are removed in feature ablation, Decision Tree and XGBoost retain over **97% of their predictive power** (86.92% accuracy). The models learn telemetry physics (`rolling_std`, `is_duplicate_value`, `time_delta`, `z_score`), not arbitrary sensor tags.
2. **Temporal Evaluation & Non-Stationary Shift:**
   - Under chronological splitting where later novel attacks (Slow Drift) appear in test, supervised tree models overfit to historic boundaries, experiencing higher false alarms. Logistic Regression exhibits smoother decision boundaries with 84.16% accuracy.
3. **Hard Attack Classes:**
   - Abrupt attacks (Spoofing, False Data Injection, Noise, Drift) achieve 95%–100% recall.
   - Sensor Freeze Attack achieves 57.07% recall because normal industrial sensors naturally hold constant values for brief periods during steady-state operation.
   - Replay Attack achieves 76.78% recall because replayed payloads contain authentic historical telemetry.

---

## 8. Artifacts and Reports

- Master Benchmark Table: `reports/phase4/phase4_master_benchmark.csv`
- Full Academic Report: `reports/phase4/PHASE_4_FINAL_REPORT.md`
- Audit Verification: `reports/phase4/PHASE_4_AUDIT_REPORT.md`
- Confusion Matrices, ROC/PR Curves, and Error Summaries: `backend/ml/reports/`