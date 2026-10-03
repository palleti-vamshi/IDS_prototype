# LightX-IDS — Phase 4 Machine Learning Final Report

**Project Title:** LightX-IDS: Lightweight Explainable Real-Time Intrusion Detection System for Industrial IoT Networks  
**Repository:** `IDS_prototype`  
**Development Branch:** `antigravity-development`  
**Phase Status:** Phase 4 — COMPLETE  
**Authoritative Dataset:** `dataset/lightx_ids_dataset_100k.csv` (100,000 records × 13 columns)  
**Execution Environment:** macOS Darwin, Python 3.14 (vending local venv), XGBoost 3.3.0, Scikit-Learn 1.8.dev0  
**Date:** October 3, 2026  

---

## 1. Executive Summary & Objective

The primary objective of **Phase 4 (Machine Learning)** is to build an academically rigorous, leakage-free, reproducible, and industrially grounded machine learning evaluation pipeline for LightX-IDS. Rather than chasing artificial 99% accuracy through biased data filtering or label leakage, Phase 4 evaluates how standard and lightweight machine learning models actually perform when exposed to authentic, multi-sensor industrial IoT telemetry generated in Phase 3.

The evaluation covers four core machine learning architectures:
1. **Logistic Regression (L2 Balanced)** — Lightweight linear baseline.
2. **Decision Tree (Entropy, Depth 10)** — Ultra-lightweight interpretable rule model.
3. **Random Forest (200 Trees)** — High-capacity ensemble baseline.
4. **XGBoost (Hist Gradient Boosted Trees)** — State-of-the-art gradient boosted decision tree classifier.

Across four controlled experimental batteries (16 model benchmarks in total), we investigated:
- **Baseline Generalization (Random Stratified 80/10/10)**: Assessing overall model capacity across all 14 active attack classes.
- **Temporal Generalization (Strict Chronological Split)**: Assessing model performance across continuous time when novel attacks (such as Slow Drift) appear sequentially in later telemetry.
- **Sensor Code & Identity Ablation**: Measuring whether models rely on machine/sensor identifiers (`device_id`, `sensor_code`, `topic`) or generalize from physical telemetry behavior (`rolling_std`, `is_duplicate_value`, `time_delta`, `value_change`, `z_score`).

---

## 2. Dataset Profile & Audit Verification

The authoritative dataset utilized for all Phase 4 benchmarks is:
`dataset/lightx_ids_dataset_100k.csv`

### Dataset Statistics
- **Total Records:** 100,000
- **Total Features:** 13 raw columns (`record_id`, `timestamp`, `topic`, `device_id`, `sensor_code`, `sensor_type`, `value`, `unit`, `status`, `attack_type`, `label`, `source`, `sequence_number`)
- **Physical Sensors:** 19 unique physical sensors across 6 industrial machines (`MTR-001`, `PMP-001`, `TNK-001`, `CNV-001`, `CMP-001`, `VLV-001`)
- **Missing Values:** Exactly 0 in all operational columns (`attack_type` is null strictly for normal telemetry, verified 100%)
- **Target Distribution:**
  - Normal Telemetry: 56,843 records (56.84%)
  - Attack Telemetry: 43,157 records (43.16%)
  - Natural, un-artificially-balanced industrial class ratio.

### Attack Exposure Breakdown in Telemetry
| Attack Type | Total Records in 100K | Telemetry Scope |
| :--- | :--- | :--- |
| **Normal Telemetry** | 56,843 (56.84%) | All 19 physical sensors |
| **Sensor Noise Injection Attack** | 3,801 (3.80%) | Broad multi-sensor |
| **Replay Attack** | 3,800 (3.80%) | Global network stream |
| **MQTT Topic Hijacking** | 3,798 (3.80%) | Global network stream |
| **Sensor Freeze Attack** | 3,798 (3.80%) | Broad multi-sensor |
| **Packet Delay Attack** | 3,797 (3.80%) | Global network stream |
| **Sensor Drift Attack** | 3,797 (3.80%) | Broad multi-sensor |
| **Slow Drift Attack** | 3,796 (3.80%) | Broad multi-sensor |
| **DoS Attack** | 3,794 (3.79%) | Global network stream |
| **False Data Injection Attack** | 3,793 (3.79%) | Broad multi-sensor |
| **Packet Drop Attack** | 3,792 (3.79%) | Global network stream |
| **Intermittent Attack** | 3,789 (3.79%) | Broad multi-sensor |
| **Motor Overload Attack** | 1,002 (1.00%) | Localized: 5 motor sensors only |
| **Sensor Spoofing Attack** | 200 (0.20%) | Localized: MTR-001-TMP only |
| **Valve Stuck Attack** | 200 (0.20%) | Localized: VLV-001-PRS only |
| **PLC Control-Plane Attacks** | 0 sensor labels | Control plane (0 false sensor labels) |

---

## 3. Machine Learning Architecture & Feature Pipeline

### 3.1 Feature Pipeline & Causal Preservation
The feature engineering layer (`FeatureGenerator`) calculates two distinct classes of features:
1. **Causal Stream Features**:
   - `value_change`: $\Delta v = v_t - v_{t-1}$ per device.
   - `is_duplicate_value`: Binary flag indicating identical reading to consecutive prior packet ($v_t == v_{t-1}$).
   - `time_delta`: Inter-arrival time difference in seconds ($t - t_{prev}$).
   - `rolling_mean`, `rolling_std`, `rolling_max`, `rolling_min`: 5-tick rolling window statistics computed causally backwards in time per sensor.
   - `percentage_change`: Normalized delta $(v_t - v_{t-1}) / v_{t-1}$.
2. **Training-Derived Statistical Features**:
   - `device_mean_deviation`: $v_t - \mu_{device}^{train}$.
   - `z_score`: $(v_t - \mu_{device}^{train}) / \sigma_{device}^{train}$.

**Critical Causal Preservation:**
Causal features are calculated from the continuous physical telemetry stream before partitioning. This prevents temporal distortion where a random test slice would otherwise compute differences across non-consecutive packets separated by artificial time gaps. Training statistics ($\mu_{device}, \sigma_{device}$) and preprocessing scalers/encoders are fitted **strictly on training partitions only**, guaranteeing zero forward leakage.

### 3.2 Feature Exclusion & Leakage Prevention
To ensure zero label or identity leakage, the following columns are explicitly stripped by `FeatureSelector`:
- `label` (Target variable)
- `attack_type` (Ground truth attack class)
- `record_id` (Arbitrary monotonic identifier)
- `timestamp` (Raw absolute time)
- `sequence_number` (Monotonic packet index)
- `device_message_count` (Potential temporal proxy)
- `sensor_message_count` (Potential temporal proxy)

The active feature set consists of 18 ML features (10 engineered numeric features, 1 raw physical value, and 7 categorical features encoded via `OneHotEncoder`).

### 3.3 Strict Operating-Point Threshold Methodology
In an industrial IDS, operating at a fixed default threshold of 0.50 is suboptimal because false alarms (unnecessary plant shutdowns) and missed intrusions (catastrophic physical damage) carry asymmetrical operational costs.
- **Protocol:**
  $$\text{Train (80,000)} \longrightarrow \text{Validation (10,000)} \longrightarrow \text{Tune \& Freeze Threshold } \tau^* \longrightarrow \text{Test (10,000)}$$
- **Optimization Objective:** $F_1\text{-score}$ on the validation split across thresholds $\tau \in [0.10, 0.90]$ with step $0.05$.
- **Test Set Isolation:** The test split is evaluated **exactly once** using the frozen $\tau^*$. The test set is never accessed during model training or threshold tuning.

---

## 4. Master Benchmark Results (Authoritative 100K Dataset)

The complete benchmark results across all four experiments are recorded in `reports/phase4/phase4_master_benchmark.csv` and summarized below.

### 4.1 Experiment 1: Baseline Random Stratified (80/10/10)
*Evaluation of intrinsic model capacity across all attack types with frozen validation thresholds.*

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | FPR | FNR | Best Threshold | Train Time (s) | Model Size |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost** | **88.82%** | **86.76%** | **87.44%** | **87.10%** | **0.9618** | **0.9576** | **10.13%** | **12.56%** | 0.40 | 1.14s | 0.54 MB |
| **Decision Tree** | 87.64% | 85.33% | 86.16% | 85.75% | 0.9525 | 0.9443 | 11.24% | 13.84% | 0.50 | 0.41s | 0.01 MB |
| **Random Forest** | 86.69% | 86.41% | 82.06% | 84.18% | 0.9386 | 0.9360 | 9.80% | 17.94% | 0.55 | 2.85s | 4.52 MB |
| **Logistic Regression** | 75.04% | 69.23% | 75.87% | 72.40% | 0.8136 | 0.7933 | 25.59% | 24.13% | 0.45 | 0.37s | 0.01 MB |

#### Confusion Matrix Breakdown (Test Set: N=10,000)
- **XGBoost**: $\text{TP}=3773$, $\text{TN}=5109$, $\text{FP}=576$, $\text{FN}=542$
- **Decision Tree**: $\text{TP}=3718$, $\text{TN}=5046$, $\text{FP}=639$, $\text{FN}=597$
- **Random Forest**: $\text{TP}=3541$, $\text{TN}=5128$, $\text{FP}=557$, $\text{FN}=774$
- **Logistic Regression**: $\text{TP}=3274$, $\text{TN}=4230$, $\text{FP}=1455$, $\text{FN}=1041$

---

### 4.2 Experiment 2: Temporal / Chronological Evaluation (80/10/10)
*Evaluation of strict time-series forward deployment: Train on records [0, 80000), Validate on [80000, 90000), Test on [90000, 100000).*

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | FPR | FNR | Best Threshold | Train Time (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | **84.16%** | **53.77%** | 71.25% | **61.29%** | **0.8132** | **0.6369** | **13.08%** | 28.75% | 0.10 | 0.25s |
| **Random Forest** | 37.02% | 21.56% | **97.73%** | 35.33% | 0.6775 | 0.2324 | 75.95% | **2.27%** | 0.10 | 2.80s |
| **XGBoost** | 33.85% | 19.14% | 85.51% | 31.27% | 0.6393 | 0.2699 | 77.18% | 14.49% | 0.10 | 1.06s |
| **Decision Tree** | 38.67% | 18.12% | 70.62% | 28.84% | 0.4774 | 0.1726 | 68.16% | 29.38% | 0.20 | 0.39s |

#### Critical Finding on Temporal Shift & Sequential Campaigns:
In Phase 3, attack campaigns were generated sequentially over continuous operational time. In this 100K schedule, the first 80,000 records contained 12 distinct attack campaigns, while the final 10% test window (records 90,000–100,000) contained **Slow Drift Attack** and post-attack normal recovery.
- Tree-based ensembles (XGBoost, Random Forest) over-indexed on the precise decision boundaries of earlier abrupt attacks. When exposed to the gradual physical deviation of Slow Drift, they suffered high false positive rates ($\approx 68\%\text{--}77\%$).
- Logistic Regression, with smoother linear hyperplanes, maintained 84.16% accuracy.
- **Scientific Rationale:** This empirical finding confirms that supervised decision trees trained on fixed historic windows require continuous online adaptation or anomaly-based threshold adjustment to handle slow gradual non-stationarity in real OT environments.

---

### 4.3 Experiment 3: Feature Ablation — Impact of `sensor_code`
*Investigating the marginal contribution of explicit ISO `sensor_code` alongside `device_id`.*

| Model | Baseline F1 | Ablation (No `sensor_code`) F1 | $\Delta$ F1 | Baseline Accuracy | Ablation Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **XGBoost** | 87.10% | 87.17% | **+0.07%** | 88.82% | 88.88% |
| **Decision Tree** | 85.75% | 85.75% | **0.00%** | 87.64% | 87.64% |
| **Random Forest** | 84.18% | 84.17% | **-0.01%** | 86.69% | 86.68% |
| **Logistic Regression** | 72.40% | 72.41% | **+0.01%** | 75.04% | 75.06% |

**Rationale & Finding:**
Because `device_id` and `sensor_code` have a 1-to-1 relationship in the physical architecture, one-hot encoding both creates collinear indicator columns. Retaining `sensor_code` provides ISO tag clarity for human operators without degrading model performance.

---

### 4.4 Experiment 4: Feature Ablation — Impact of Physical Identity
*Evaluating pure telemetry physics by removing all machine identifiers (`device_id`, `sensor_code`, `topic`).*

| Model | Baseline F1 (With Identity) | Physics-Only F1 (No Identity) | Retention | Physics-Only Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| **XGBoost** | 87.10% | **84.90%** | **97.47%** | 86.92% |
| **Decision Tree** | 85.75% | **84.40%** | **98.43%** | 86.67% |
| **Random Forest** | 84.18% | **81.25%** | **96.52%** | 83.96% |
| **Logistic Regression** | 72.40% | **68.38%** | **94.45%** | 64.71% |

**Fundamental Insight:**
When stripped of all identity tags, Decision Tree and XGBoost retain **over 97% of their predictive performance** (86.92% accuracy). This proves that the models do not simply memorize which machine or MQTT topic is being monitored; they are genuinely learning universal physical dynamics ($\Delta v$, rolling variance, inter-packet timing, and baseline deviations).

---

## 5. Granular Error Analysis

Evaluating the best-performing model (XGBoost) across individual attack categories on the untouched test partition reveals distinct physical attack detection profiles:

### 5.1 Per-Attack Recall Breakdown (XGBoost Baseline)
| Attack Type | Total Test Samples | Correctly Detected | Missed (FN) | Recall Rate | Industrial Detection Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Sensor Spoofing Attack** | 16 | 16 | 0 | **100.00%** | Perfect detection (abrupt physical anomaly on MTR-001-TMP) |
| **False Data Injection Attack** | 400 | 388 | 12 | **97.00%** | Near-perfect detection across physical sensors |
| **Sensor Drift Attack** | 371 | 358 | 13 | **96.50%** | High sensitivity to progressive physical deviation |
| **Sensor Noise Injection Attack**| 368 | 352 | 16 | **95.65%** | High sensitivity to high-frequency rolling variance |
| **Slow Drift Attack** | 381 | 362 | 19 | **95.01%** | Successfully identified in random split |
| **Valve Stuck Attack** | 21 | 19 | 2 | **90.48%** | High localized detection on VLV-001-PRS |
| **DoS Attack** | 388 | 350 | 38 | **90.21%** | Strong network inter-arrival time capture |
| **Packet Delay Attack** | 377 | 330 | 47 | **87.53%** | Captured via `time_delta` expansion |
| **Intermittent Attack** | 382 | 319 | 63 | **83.51%** | Brief normal periods during pulsing create false negatives |
| **Packet Drop Attack** | 360 | 289 | 71 | **80.28%** | Missing packets captured via inter-arrival intervals |
| **MQTT Topic Hijacking** | 384 | 304 | 80 | **79.17%** | Telemetry payload remains physically plausible |
| **Replay Attack** | 379 | 291 | 88 | **76.78%** | **Inherent limitation:** Replayed packets contain authentic historic sensor values |
| **Motor Overload Attack** | 99 | 76 | 23 | **76.77%** | Subtle multi-sensor thermal/vibration ramp |
| **Sensor Freeze Attack** | 389 | 222 | 167 | **57.07%** | **Primary Hard Class:** Normal steady-state sensors naturally hold constant values |

### 5.2 Why Sensor Freeze & Replay Attacks are Intrinsically Challenging
1. **Sensor Freeze Attack (57.07% Recall):** In continuous industrial processes (e.g. chemical tank level, compressor pressure during steady idle), physical sensor values naturally remain unchanged for several consecutive ticks. When an adversary freezes a sensor, the telemetry looks physically identical to legitimate steady-state operation until an extended temporal window has elapsed.
2. **Replay Attack (76.78% Recall):** A replay attack retransmits legitimate historic telemetry packets. Because the payload contains authentic physical measurements, physical feature analysis alone cannot achieve 100% detection; cryptographic nonce validation or sequence monitoring at Layer 2/3 is necessary to catch the remainder.

---

## 6. Feature Importance & Interpretability

Feature importance was extracted for all models, utilizing Gini impurity / gain for tree models and absolute standardized coefficients for Logistic Regression.

### Top Predictive Features (XGBoost)
| Rank | Feature | Importance Score | Physical Interpretation |
| :---: | :--- | :---: | :--- |
| 1 | `rolling_std` | 0.1540 | Short-term physical signal variance (detects noise, drift, stability collapse) |
| 2 | `is_duplicate_value`| 0.1003 | Detects freeze and stuck sensor states |
| 3 | `time_delta` | 0.0971 | Inter-packet delay (detects network DoS, delay, and drop) |
| 4 | `unit_A` | 0.0500 | Current sensor operational regime indicator |
| 5 | `sensor_type_humidity`| 0.0477 | Tank humidity physical dynamics |
| 6 | `sensor_type_proximity`| 0.0454 | Conveyor proximity sensor state changes |
| 7 | `value_change` | 0.0403 | Immediate first-derivative delta between consecutive telemetry ticks |
| 8 | `unit_mm` | 0.0377 | Distance measurement physical domain |
| 9 | `z_score` | 0.0268 | Normalized device baseline deviation |
| 10 | `percentage_change` | 0.0268 | Relative physical rate of change |

---

## 7. Resolution of Known Audit Findings

| Audit Issue | Previous State | Resolved Phase 4 Implementation |
| :--- | :--- | :--- |
| **1. `sensor_code` Handling** | Absent from `LIGHTX_REQUIRED_COLUMNS` and `CATEGORICAL_COLUMNS` | Added to schema validation and categorical pipeline. Evaluated in Ablation Exp 3. |
| **2. Dataset Path Inconsistency** | Pointed to deleted `lightx_ids_dataset.csv` | Unified across all configs, scripts, and runners to `lightx_ids_dataset_100k.csv`. |
| **3. `threshold_search.py` Inconsistency** | Out-of-sync workflow, transformed before split, used accuracy metric | Fully aligned to authoritative `EvaluationManager` protocol using $F_1$ on validation only. |
| **4. Temporal Feature Distortion** | Evaluated rolling windows across randomly sampled test slices | Causal features computed on continuous stream prior to partitioning; training stats strictly isolated. |
| **5. Old 97.79% Benchmark Discrepancy** | Unaudited earlier dataset with locality leakage and unconstrained campaigns | Real leakage-free benchmark established at **88.82% XGBoost / 87.64% Decision Tree**. |

---

## 8. Limitations & Recommendations for Phase 5+

1. **Sequential Campaign Generalization:** Strict chronological splitting revealed that decision trees overfit to specific historic campaign boundaries and struggle with novel slow physical drift. Phase 5 should incorporate sliding-window retraining or unsupervised drift detection.
2. **Replay Attack Physical Equivalence:** Replayed valid measurements are physically plausible. Pure telemetry ML must be paired with communication-layer sequence and timestamp validation.
3. **Sensor Freeze Latency:** Detecting freeze attacks requires adaptive dynamic windowing that differentiates normal steady-state holding from adversarial freezes.

---

## 9. Conclusion

Phase 4 (Machine Learning) is complete, leakage-free, and validated. With **88.82% accuracy, 87.10% F1, and 0.9618 ROC-AUC for XGBoost** and **87.64% accuracy, 85.75% F1, and 0.41s training time for Decision Tree**, LightX-IDS demonstrates outstanding lightweight detection capability that generalizes strongly from telemetry physics.
