# LIGHTX-IDS — PHASE 4.1 RESEARCH-GRADE ML OPTIMIZATION & DOCUMENTATION REPORT
## Comprehensive Multi-Attack Benchmark, Temporal Generalization, and Root-Cause Diagnostic Analysis

**Project:** LightX-IDS: Lightweight Explainable Real-Time Intrusion Detection System for Industrial IoT Networks
**Repository:** `IDS_prototype`
**Branch:** `antigravity-development`
**Authoritative Dataset:** `dataset/lightx_ids_dataset_100k.csv` (100,000 records × 13 columns, 19 physical IoT sensors)
**Evaluation Protocol:** 80,000 Train / 10,000 Validation / 10,000 Test
**Status:** COMPLETE / FROZEN (Phase 4 & Phase 4.1 Complete; Phase 5 Not Started)

---

## 1. Executive Summary

In Phase 4, the initial machine-learning baseline achieved **97.14% test accuracy** (with 96.67% F1-score) using an XGBoost classifier on the authoritative 100K industrial IoT dataset (`dataset/lightx_ids_dataset_100k.csv`). Granular error attribution revealed that **80.0% of all false negatives** were concentrated in network communication anomalies (Packet Drop, Packet Delay, and DoS attacks).

The objective of **Phase 4.1** was to investigate whether LightX-IDS could legitimately, scientifically, and causally improve detection capability without data leakage, test snooping, label manipulation, synthetic dataset distortion, or record deletion.

Through causal timing feature engineering and validation-driven hyperparameter optimization, LightX-IDS achieved a **99.65% stratified multi-attack benchmark performance**. However, extensive chronological and diagnostic evaluations demonstrated that benchmark accuracy alone is insufficient to describe real-time industrial deployment dynamics.

This final Phase 4 report establishes a **Three-Evaluation Framework** that cleanly separates distinct research questions:
1. **Stratified Multi-Attack Benchmark Performance (99.65% Accuracy):** Evaluates multi-attack classification capacity when attack classes are represented across training and test splits.
2. **Controlled Temporal Generalization (97.63% Accuracy):** Evaluates continuous time-series performance when early examples of a continuous kinetic ramp attack (Slow Drift) are present during training, yielding **99.77% Slow Drift recall**.
3. **Strict Chronological Zero-Shot Generalization (85.30% Accuracy):** Evaluates performance when an attack type (Slow Drift) is completely absent from training.

---

## 2. Dataset and Evaluation Protocol

### 2.1 Authoritative Dataset Profile
All Phase 4 and 4.1 evaluations are executed strictly on the frozen authoritative dataset:
- **File Path:** `dataset/lightx_ids_dataset_100k.csv`
- **Total Records:** 100,000
- **Features:** 13 raw columns (`record_id`, `timestamp`, `topic`, `device_id`, `sensor_code`, `sensor_type`, `value`, `unit`, `status`, `attack_type`, `label`, `source`, `sequence_number`).
- **Physical Sensors:** 19 unique industrial sensors across 5 physical machine subsystems (Motor `MTR-001`, Pump `PMP-001`, Tank `TNK-001`, Conveyor `CNV-001`, Compressor `CMP-001`, Valve `VLV-001`).
- **Missing Values:** Exactly 0 in operational telemetry (`attack_type` is null strictly for normal telemetry).
- **Target Class Balance:**
  - Normal Telemetry: 56,854 records (56.85%)
  - Attack Telemetry: 43,146 records (43.15%)

> [!IMPORTANT]
> The authoritative dataset is READ-ONLY. No rows were deleted, no labels were modified or rebalanced, no timestamps were altered, and no attack distributions were manipulated.

### 2.2 Stratified Multi-Attack Evaluation Protocol
- **Training Set (80%):** 80,000 records. Used exclusively for fitting preprocessors, scalers, encoders, device baseline statistics, and model tree structures.
- **Validation Set (10%):** 10,000 records. Used exclusively for hyperparameter tuning and optimizing the classification operating threshold $\tau^*$.
- **Test Set (10%):** 10,000 records ($5,685$ Normal, $4,315$ Attack). Kept untouched until final evaluation. Evaluated in a single forward pass with the frozen threshold.

---

## 3. Phase 4 Baseline Benchmark

The control baseline established at the end of initial Phase 4 feature development:

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | FPR | FNR | Operating Threshold ($\tau^*$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost (Phase 4 Baseline)** | **97.14%** | **97.17%** | **96.18%** | **96.67%** | **0.9970** | **0.9962** | **2.13%** | **3.82%** | **0.55** |
| Decision Tree (Phase 4 Baseline) | 96.27% | 96.07% | 95.25% | 95.66% | 0.9906 | 0.9853 | 2.96% | 4.75% | 0.65 |
| Random Forest (Phase 4 Baseline) | 96.19% | 96.90% | 94.18% | 95.52% | 0.9945 | 0.9927 | 2.29% | 5.82% | 0.60 |
| Logistic Regression (Phase 4 Baseline)| 81.31% | 81.60% | 73.19% | 77.17% | 0.8579 | 0.8692 | 12.52% | 26.81% | 0.45 |

---

## 4. Phase 4 Optimization & Causal Formulation

### 4.1 Error-Driven Discovery: Collapse of Inter-Arrival Variance
Forensic audit of Phase 4 false negatives revealed that 132 out of 165 missed attacks (80.0%) were communication-layer network anomalies (Packet Drop, Packet Delay, and DoS attacks) where physical sensor payloads remained unchanged.

Statistical inspection of inter-arrival intervals (`time_delta`) exposed a key physical distinction:
- **Normal Telemetry:** Mean inter-arrival time = $0.208\,\text{s}$, Standard Deviation $\sigma = 0.085\,\text{s}$ (reflecting physical RTOS thread scheduling and sensor polling jitter).
- **Packet Drop Attack:** Mean = $0.106\,\text{s}$, Standard Deviation $\sigma = 0.0057\,\text{s}$.
- **Packet Delay Attack:** Mean = $0.094\,\text{s}$, Standard Deviation $\sigma = 0.0050\,\text{s}$.
- **DoS Attack:** Mean = $0.068\,\text{s}$, Standard Deviation $\sigma = 0.0030\,\text{s}$.

Synthetic attack loops transmit packets with rigid microsecond timer periodicity, causing inter-arrival variance to collapse by an order of magnitude ($\sigma$ drops from $0.085\,\text{s}$ to $<0.006\,\text{s}$).

### 4.2 Causal Real-Time Timing Feature Formulation
Four continuous real-time inter-arrival timing features were incorporated into `FeatureGenerator`:
1. `rolling_time_delta_5`: Backward 5-packet rolling mean of inter-arrival time per device.
2. `rolling_time_delta_std_5`: Backward 5-packet rolling standard deviation of inter-arrival time per device (exposes variance collapse).
3. `rolling_global_td_std_10`: Backward 10-packet rolling standard deviation of global bus inter-arrival time.
4. `packet_rate_10`: Estimated instantaneous arrival rate (packets/sec) computed as $1.0 / (\mu_{\Delta t, 10} + 10^{-4})$.

### 4.3 Validation-Driven Hyperparameter Search
Grid search screening was performed strictly using Training (80,000) and Validation (10,000) splits. Configuration **C7** emerged as optimal:
- `n_estimators`: 500, `max_depth`: 10, `learning_rate`: 0.05, `min_child_weight`: 2, `subsample`: 0.95, `colsample_bytree`: 0.95, `reg_alpha`: 0.05, `reg_lambda`: 2.0.
- Selected operating threshold on validation split: $\tau^* = 0.35$.

---

## 5. Phase 4.1 Stratified Multi-Attack Benchmark

Evaluated on the 10,000-sample untouched test set using the frozen validation threshold $\tau^* = 0.35$:

### 5.1 Authoritative Stratified Benchmark Results

| Model | Feats | Th ($\tau^*$) | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | FPR | FNR | TP | FP | TN | FN | Train Time | Model Size |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost (Phase 4.1)** | **40** | **0.35** | **99.65%** | **99.35%** | **99.84%** | **99.60%** | **0.99992** | **0.99989** | **0.49%** | **0.16%** | **4308** | **28** | **5657** | **7** | **2.56 s** | **2.85 MB** |
| Decision Tree | 40 | 0.55 | 98.08% | 97.06% | 98.54% | 97.79% | 0.99605 | 0.99353 | 2.27% | 1.46% | 4252 | 129 | 5556 | 63 | 0.88 s | 0.05 MB |
| Random Forest | 40 | 0.55 | 97.59% | 96.38% | 98.10% | 97.23% | 0.99779 | 0.99710 | 2.80% | 1.90% | 4233 | 159 | 5526 | 82 | 3.51 s | 57.26 MB |
| Logistic Reg. | 40 | 0.40 | 82.75% | 78.40% | 82.85% | 80.56% | 0.88361 | 0.88087 | 17.33% | 17.15% | 3575 | 985 | 4700 | 740 | 0.48 s | 0.01 MB |

> [!NOTE]
> The **99.65%** result MUST be described as **"99.65% stratified multi-attack benchmark performance"**. It represents optimal classifier capability under random stratified split conditions and must not be conflated with guaranteed deployment performance under unseen temporal distribution shifts.

### 5.2 Per-Attack Classification Breakdown
Under the stratified benchmark, XGBoost achieves **100.00% recall across 10 of 14 attack classes**, missing only 7 total packets out of 4,315 attack records:

| Attack Class | Category | Test Samples | Detected | Missed (FN) | Recall Rate | Baseline Recall (Phase 4) | Recall Improvement |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **DoS Attack** | Communication | 388 | 388 | **0** | **100.00%** | 93.30% | +6.70% (26 missed $\rightarrow$ 0) |
| **Packet Drop Attack** | Communication | 360 | 360 | **0** | **100.00%** | 80.56% | +19.44% (70 missed $\rightarrow$ 0) |
| **Packet Delay Attack** | Communication | 377 | 377 | **0** | **100.00%** | 90.45% | +9.55% (36 missed $\rightarrow$ 0) |
| **MQTT Topic Hijacking**| Communication | 384 | 384 | **0** | **100.00%** | 100.00% | Maintained 100.0% |
| **Replay Attack** | Communication | 379 | 379 | **0** | **100.00%** | 100.00% | Maintained 100.0% |
| **False Data Injection**| Sensor Telemetry | 400 | 400 | **0** | **100.00%** | 100.00% | Maintained 100.0% |
| **Sensor Freeze** | Sensor Telemetry | 389 | 389 | **0** | **100.00%** | 100.00% | Maintained 100.0% |
| **Sensor Noise Injection**| Sensor Telemetry | 368 | 368 | **0** | **100.00%** | 100.00% | Maintained 100.0% |
| **Intermittent Attack** | Sensor Telemetry | 382 | 382 | **0** | **100.00%** | 100.00% | Maintained 100.0% |
| **Sensor Spoofing** | Sensor Telemetry | 16 | 16 | **0** | **100.00%** | 100.00% | Maintained 100.0% |
| **Sensor Drift** | Slow Kinetic | 371 | 370 | 1 | **99.73%** | 99.46% | +0.27% |
| **Slow Drift** | Slow Kinetic | 381 | 379 | 2 | **99.48%** | 87.38% | +12.10% |
| **Motor Overload** | Machine Mechanical | 99 | 96 | 3 | **96.97%** | 96.00% | +0.97% |
| **Valve Stuck** | Valve Mechanical | 21 | 20 | 1 | **95.24%** | 95.00% | +0.24% |
| **TOTAL / OVERALL** | | **4,315** | **4,308** | **7** | **99.84%** | **96.18%** | **+3.66% Absolute Recall** |

---

## 6. Controlled Feature Ablation Battery

A 10-experiment ablation battery evaluated the marginal contribution of each feature family:

| # | Experiment Configuration | Features ($k$) | Val Acc | Val F1 | Th ($\tau^*$) | Test Acc | Test Prec | Test Rec | Test F1 | Test ROC-AUC | Test FPR | Test FNR |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Baseline Features (Pre-optimization) | 20 | 88.75% | 87.09% | 0.40 | 89.38% | 87.16% | 88.41% | 87.78% | 0.9664 | 9.89% | 11.59% |
| **2** | **Full Phase 4.1 Optimized Pipeline** | **40** | **99.69%** | **99.64%** | **0.35** | **99.65%** | **99.35%** | **99.84%** | **99.60%** | **0.99992** | **0.49%** | **0.16%** |
| 3 | Without New Timing Features | 36 | 97.14% | 96.67% | 0.55 | 97.17% | 97.10% | 96.32% | 96.71% | 0.99715 | 2.18% | 3.68% |
| 4 | Without All Communication Features | 30 | 96.50% | 95.95% | 0.50 | 96.40% | 95.70% | 95.97% | 95.83% | 0.99573 | 3.27% | 4.03% |
| 5 | Without Multi-Window Features | 32 | 98.74% | 98.54% | 0.45 | 98.82% | 98.54% | 98.73% | 98.63% | 0.99928 | 1.11% | 1.27% |
| 6 | Without Physical Dynamics Features | 35 | 99.69% | 99.64% | 0.35 | 99.60% | 99.29% | 99.79% | 99.54% | 0.99993 | 0.55% | 0.21% |
| 7 | Without Sensor-Aware Baseline Features| 36 | 99.71% | 99.66% | 0.35 | 99.66% | 99.38% | 99.84% | 99.61% | 0.99993 | 0.47% | 0.16% |
| 8 | Without Plant-Wide Features | 36 | 98.64% | 98.42% | 0.50 | 98.80% | 98.59% | 98.63% | 98.61% | 0.99931 | 1.07% | 1.37% |
| 9 | Without Physical Identity (Pure Behavioral)| 37 | 99.70% | 99.65% | 0.40 | 99.71% | 99.49% | 99.84% | 99.66% | 0.99993 | 0.39% | 0.16% |
| 10| Without Redundant Features (Clean Causal)| 36 | 99.69% | 99.64% | 0.35 | 99.65% | 99.35% | 99.84% | 99.60% | 0.99992 | 0.49% | 0.16% |

**Key Takeaways:**
- Removing the new inter-arrival timing features (Exp 3) drops test accuracy from **99.65% back to 97.17%**, confirming timing dynamics as the primary causal driver of the +2.51% gain.
- Stripping physical machine identity tags (`device_id`, `sensor_code`, `topic` dropped in Exp 9) yields **99.71% test accuracy**, demonstrating that LightX-IDS learns genuine behavioral physics rather than memorizing sensor labels.

---

## 7. Multi-Seed Stability Verification

To verify that the 99.65% benchmark is structural rather than an artifact of random seed 42, repeated 80/10/10 evaluation was conducted across 5 fixed random seeds:

| Seed | Accuracy | Precision | Recall | F1-Score | ROC-AUC | FPR | FNR | Operating Threshold ($\tau^*$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 42 | 99.65% | 99.35% | 99.84% | 99.60% | 0.99992 | 0.49% | 0.16% | 0.35 |
| 43 | 99.66% | 99.74% | 99.47% | 99.61% | 0.99986 | 0.19% | 0.53% | 0.55 |
| 44 | 99.57% | 99.38% | 99.63% | 99.50% | 0.99991 | 0.47% | 0.37% | 0.45 |
| 45 | 99.67% | 99.56% | 99.68% | 99.62% | 0.99991 | 0.33% | 0.32% | 0.45 |
| 46 | 99.60% | 99.35% | 99.72% | 99.54% | 0.99990 | 0.49% | 0.28% | 0.45 |
| **MEAN** | **99.63%** | **99.48%** | **99.67%** | **99.57%** | **0.99990** | **0.40%** | **0.33%** | — |
| **STD** | **±0.04%** | **±0.17%** | **±0.14%** | **±0.05%** | **±0.00003** | **±0.13%** | **±0.14%** | — |

---

## 8. Strict Chronological Zero-Shot Evaluation

### 8.1 Protocol & Authoritative Result
Under a strict chronological split reflecting pure forward time deployment:
- **TRAIN:** Records 1–80,000
- **VALIDATION:** Records 80,001–90,000
- **TEST:** Records 90,001–100,000

**Authoritative Result:**
- **Accuracy:** **85.30%**
- **Precision:** **60.66%**
- **Recall:** **46.88%**
- **F1-Score:** **52.88%**
- **ROC-AUC:** **0.9168**

### 8.2 Slow Drift Campaign Distribution Analysis
Detailed dataset inspection revealed that the **Slow Drift Attack** is concentrated at the end of the simulation campaign:
- **Dataset Occurrence Range:** Records 87,965–91,760.
- **Training Set (1–80,000):** Contains **0 Slow Drift samples**.
- **Validation Set (80,001–90,000):** Contains **2,036 Slow Drift samples**.
- **Test Set (90,001–100,000):** Contains **1,760 Slow Drift samples**.

### 8.3 Correct Research Interpretation
The strict chronological evaluation does not merely test stationary temporal extrapolation. Because Training contains zero Slow Drift records, the evaluation protocol simultaneously tests:
1. **Temporal distribution shift over continuous time**, AND
2. **Zero-shot generalization to an attack type completely absent from training.**

Therefore, rather than stating that "the model simply cannot extrapolate Slow Drift," the scientific finding is that:
> *"The strict chronological protocol simultaneously introduces temporal distribution shift and an unseen attack type."*

---

## 9. Slow Drift Root-Cause & Implementation Investigation

### 9.1 Historical Code vs. Runtime Discrepancy
Investigation of the Phase 3 attack generator codebase revealed a discrepancy between declared configuration and actual execution runtime:
- **Declared Configuration:** Duration = 60 seconds, Max Drift = 10.
- **Runner Execution:** The attack engine executed **200 ticks** at a tick interval of **0.05 seconds**.
- **Actual Runtime Duration:** $200 \times 0.05\,\text{s} = 10.0\,\text{seconds}$ (instead of 60 seconds).

### 9.2 Physical Impact on Generated Telemetry
Because the attack ran for 10 seconds rather than 60 seconds, the expected linear drift accumulated to:
$$\text{Expected Drift} = \frac{10\,\text{s}}{60\,\text{s}} \times 10 \approx 1.67$$

Observed telemetry values in `dataset/lightx_ids_dataset_100k.csv` exhibit a common drift offset of approximately **+1.65 to +1.66** across the campaign.

> [!NOTE]
> Phase 3 code and datasets are **FROZEN**. This implementation/runtime limitation is documented as historical context explaining the exact drift magnitude in the dataset, without altering frozen Phase 3 code or historical metrics.

---

## 10. Controlled Temporal Experiment

To isolate whether the degradation in the strict chronological test was caused by unseen attack exposure rather than temporal drift alone, a controlled temporal experiment was conducted.

### 10.1 Protocol & Distribution
- **TRAIN:** Records 1–89,000 (Contains **1,036 Slow Drift samples** from the early phase of the campaign).
- **VALIDATION:** Records 89,001–90,000 (Contains **1,000 Slow Drift samples**).
- **TEST:** Records 90,001–100,000 (Contains **1,760 Slow Drift samples** and **8,240 Normal samples**).

### 10.2 Authoritative Controlled Results

| Metric | Authoritative Controlled Value |
| :--- | :---: |
| **Accuracy** | **97.63%** |
| **Precision** | **88.29%** |
| **Recall** | **99.77%** |
| **F1-Score** | **93.68%** |
| **ROC-AUC** | **0.99870** |
| **PR-AUC** | **0.99331** |
| **False Positive Rate (FPR)** | **2.83%** |
| **False Negative Rate (FNR)** | **0.23%** |
| **Frozen Operating Threshold ($\tau^*$)** | **0.10** |

#### Confusion Matrix (Test Set: N=10,000)
- **True Negatives (TN):** **8,007**
- **False Positives (FP):** **233**
- **False Negatives (FN):** **4**
- **True Positives (TP):** **1,756**
- **Slow Drift Recall:** **99.77%** (1,756 out of 1,760 detected).

### 10.3 Scientific Interpretation
When early Slow Drift examples are available during training, subsequent Slow Drift detection recall rises from 46.88% to **99.77%**.

This provides strong empirical evidence that:
> *"Unseen attack-type exposure is a dominant contributor to the original strict-temporal degradation."*

*(This finding indicates high sensitivity to unseen attack types, though it does not claim unseen attack exposure is the sole cause of all temporal variance.)*

---

## 11. Threshold Diagnostic

To verify whether the operating threshold of $\tau^* = 0.10$ selected in the controlled temporal experiment was an artifact of an all-attack validation set (records 89,001–90,000 containing only Slow Drift), a threshold calibration diagnostic was executed.

### 11.1 Mixed Validation Protocol
- **Training Set:** Records 1–89,000.
- **Mixed Validation Set:** 1,000 early Slow Drift samples + 1,000 historical Normal samples.
- **Test Set:** Records 90,001–100,000 (untouched).

### 11.2 Result
- Optimizing F1-score on the balanced mixed validation set yielded the **exact same operating threshold: $\tau^* = 0.10$**.
- Test set performance remained identical:
  - **Accuracy:** **97.63%**
  - **F1-Score:** **93.68%**
  - **Recall:** **99.77%**
  - **False Positives:** **233** (FPR = 2.83%)

**Conclusion:** The threshold of 0.10 is driven by model output calibration on continuous kinetic ramp features rather than an artifact of validation set class imbalance.

---

## 12. False-Positive Diagnostic Analysis

### 12.1 Authoritative Controlled Temporal FP Profile
In the authoritative controlled temporal evaluation:
- Normal Test Samples: 8,240
- Correct Normal (TN): 8,007
- False Positives (FP): 233
- False Positive Rate: 2.83%

### 12.2 Model Probability Distributions
Inspecting predicted attack probabilities on normal telemetry:
- **Correct Normal Telemetry ($N=8,007$):** Mean probability $\approx 0.0100$, Maximum $\approx 0.099445$.
- **False Positive Telemetry ($N=233$):** Mean probability $\approx 0.3048$, Median $\approx 0.1382$, Maximum $\approx 0.99986$.

Several high-probability false positives ($p > 0.90$) emerge immediately after the Slow Drift campaign terminates around record 91,760.

### 12.3 Feature Separation Analysis
Statistical comparison between correct normal and false positive samples identified key feature differences:
- `time_delta` and `rolling_time_delta_std_5`
- `rolling_global_td_std_10` and `rolling_global_td_10`
- `packet_rate_10` and `rolling_seq_std_5`
- `seq_gap_dev` and `plant_duplicate_ratio_19`

These feature differences demonstrate clear distributional separation between post-attack normal traffic and baseline normal traffic, though individual features are not claimed to independently prove causality.

---

## 13. Campaign Transition Analysis

A diagnostic was executed to measure whether false positives are concentrated at the immediate campaign transition boundary (Slow Drift $\rightarrow$ Normal recovery).

### 13.1 Temporal FP Concentration Windowing
Evaluating the 8,240 normal test records following the end of Slow Drift at record 91,760:

| Post-Transition Window | Normal Records Evaluated | False Positives (FP) | Window FPR | Cumulative FP Proportion |
| :--- | :---: | :---: | :---: | :---: |
| **First 100 Records** (91,761–91,860) | 100 | 63 | **63.00%** | 28.64% |
| **First 500 Records** (91,761–92,260) | 500 | 63 | **12.60%** | 28.64% |
| **First 1,000 Records** (91,761–92,760)| 1,000 | 64 | **6.40%** | 29.09% |
| **First 2,000 Records** (91,761–93,760)| 2,000 | 81 | **4.05%** | **36.82%** |
| **Remaining Normal Period** (93,761–100,000) | 6,240 | 139 | **2.23%** | **63.18%** |

*(Note: Diagnostic script reconstructed feature calculation yielding 220 FPs total in this run; authoritative controlled experiment total remains 233 FPs).*

### 13.2 Correct Interpretation
While the first 100 post-transition records exhibit an intense FP spike (63.0% FPR), the first 2,000 records account for **36.82%** of false positives, while the remaining normal period contains **63.18%**.

Therefore, false positives cannot be attributed solely to transition lag:
> *"A substantial fraction of false positives occurs near the campaign transition, but the majority occurs later in the normal period, supporting a mixed transition-effect and broader normal-distribution-shift explanation."*

---

## 14. Known Limitations & Diagnostic Clarifications

### 14.1 Exploratory Feature-Carryover Diagnostic Note
An additional exploratory script (`analyze_fp_feature_carryover.py`) produced an accuracy of 96.31% and 365 false positives.

> [!CAUTION]
> These numbers are **NON-AUTHORITATIVE**. The script reconstructed feature processing rather than passing through the exact project pipeline path. These findings are cited strictly as *exploratory reconstructed analysis*, while **97.63% accuracy and 233 FPs** remain the authoritative controlled temporal benchmark.

### 14.2 Summary of Methodological Boundaries
1. **Stratified Multi-Attack Benchmark (99.65%):** Assumes attack classes are represented across train and test sets.
2. **Chronological Evaluation (85.30%):** Sensitive to unseen attack types during forward temporal deployment.
3. **Slow Drift Duration (10s vs 60s):** Historical artifact of Phase 3 execution; frozen and documented.

---

## 15. Final Research Interpretation

The scientific conclusions of Phase 4 and Phase 4.1 are formulated as follows:

> *"Phase 4 evaluation demonstrates strong performance under the stratified multi-attack benchmark, achieving 99.65% accuracy. However, chronological evaluation reveals an important limitation: when Slow Drift is completely absent from training, strict temporal zero-shot performance falls substantially. A controlled experiment that exposes the model to early Slow Drift examples raises later Slow Drift recall to 99.77%, indicating that unseen attack-type exposure is a dominant contributor to the original temporal degradation. Residual false positives are not confined to the immediate campaign transition; diagnostic analysis indicates both transition effects and broader normal-traffic distribution shift. These findings motivate Phase 5 work on false-positive reduction and robustness rather than further optimization of benchmark accuracy alone."*

---

## 16. Phase 5 Motivation

These findings define the technical scope for Phase 5 development:
1. **False-Positive Reduction:** Development of post-transition stabilization filters and adaptive baseline tracking to suppress post-attack transition spikes.
2. **Robustness & Unseen Attack Generalization:** Implementation of semi-supervised or anomaly-based detection heads to complement supervised GBDTs when encountering novel kinetic drift patterns.
3. **Online Model Adaptation:** Stream-based model updating for continuous OT environments.

Further optimization of benchmark accuracy beyond 99.65% is frozen.

---

## 17. Final Conclusion

Phase 4 and Phase 4.1 are **COMPLETE AND FROZEN**.

The evaluation framework is codified into three distinct authoritative benchmarks:
1. **Stratified Multi-Attack Benchmark:** **99.65% Accuracy | 99.60% F1 | 99.84% Recall**
2. **Controlled Temporal Generalization:** **97.63% Accuracy | 93.68% F1 | 99.77% Slow Drift Recall**
3. **Strict Chronological Zero-Shot Evaluation:** **85.30% Accuracy | 52.88% F1 | 46.88% Recall**

All code, datasets, and benchmarks are frozen, reproducible, and documented.
