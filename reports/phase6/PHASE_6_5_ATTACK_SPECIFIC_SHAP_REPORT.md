# LIGHTX-IDS PHASE 6.5: ATTACK-SPECIFIC SHAP EXPLANATIONS REPORT

**Project:** LightX-IDS: Lightweight Explainable Real-Time Intrusion Detection System for Industrial IoT Networks  
**Author:** Antigravity Autonomous Agent (Pair Programming with Vamshi)  
**Date:** October 4, 2026  
**Branch:** `antigravity-development`  
**Phase:** 6.5 — Attack-Specific SHAP Explanations  
**Status:** COMPLETE  
**Authoritative Frozen Model:** `backend/ml/saved_models/xgboost_h3_32.pkl`  
**Authoritative Dataset:** `dataset/lightx_ids_dataset_100k.csv` (Stratified Test Split: $N=10,001$, Seed 42)

---

## 1. OBJECTIVE

The primary objective of **Phase 6.5** is to extend the LightX-IDS explainability architecture by decomposing the decision-making patterns of the frozen Phase 5 H3-32 XGBoost model across **individual, distinct attack categories**. 

While Phase 6.3 established the *global* feature importance ranking across the full test set and Phase 6.4 delivered an instance-level *local* packet explanation engine, Phase 6.5 answers the critical domain question:

> *"Which input features does the frozen intrusion detection model rely upon most strongly when classifying specific, distinct attack families, and how do these attribution patterns differ across attack classes?"*

### Scientific Language & Non-Causality Principle
In accordance with rigorous ML explainability standards, **SHAP values reflect model attribution, not physical causation**. 
- Permitted scientific terminology: *"the model relied strongly on"*, *"contributed toward the prediction"*, *"associated with the model's decision"*, *"high SHAP attribution mass"*.
- Strictly excluded terminology: *"this feature caused the attack"*, *"proves physical causation"*, *"root-cause feature"*.

---

## 2. FROZEN MODEL AND EVALUATION DATASET

### Frozen Model Architecture (`xgboost_h3_32.pkl`)
- **Pipeline Structure:** Scikit-Learn `Pipeline` composed of:
  1. `preprocessor`: `ColumnTransformer` with `StandardScaler` for numeric inputs and `OneHotEncoder(handle_unknown="ignore", sparse_output=False)` for categorical inputs.
  2. `classifier`: `XGBClassifier` (100 estimators, max depth 6, learning rate 0.1, objective `binary:logistic`).
- **Feature Space:**
  - 32 original input features (25 numeric, 7 categorical).
  - 95 transformed features post one-hot encoding.
  - Ablation: Exactly preserves the Phase 5 H3-32 ablation (removes `value_change`, `abs_value_change`, `rolling_range_5`, and `rolling_mean_10`).
- **Zero Retraining Policy:** The model weights, hyperparameters, preprocessing transformers, and decision threshold (0.35) were strictly **untouched**.

### Evaluation Split Protocol (Leakage-Safe)
- Evaluated exclusively on the **frozen test set** generated via the authoritative seed 42 stratified 80/10/10 split from `dataset/lightx_ids_dataset_100k.csv`.
- **Test Set Composition:**
  - Total records: $N = 10,001$
  - Normal records (`label == 0`): $5,685$ ($56.84\%$)
  - Attack records (`label == 1`): $4,316$ ($43.16\%$)
- **Zero Leakage:** Baseline device statistics within the `FeatureGenerator` were fitted strictly on the $80,000$-record training set. Neither the validation set nor the test set was utilized for fitting, tuning, or threshold selection.

---

## 3. METHODOLOGY

The attack-specific SHAP explanation pipeline adheres to the following computational pipeline:

```
+-------------------------------------------------------------------------------+
|  1. Filter Test Set: Select rows where label == 1 AND attack_type == Attack_i  |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|  2. Select 32 Input Features (25 Numeric + 7 Categorical in Canonical Order)   |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|  3. Transform via Frozen Preprocessor -> 95-Dimensional Transformed Space     |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|  4. Compute Log-Odds SHAP Values via TreeExplainer(classifier)                |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|  5. Exact One-Hot Aggregation: Sum transformed one-hot attributions into      |
|     their parent original categorical features -> 32-Feature SHAP Matrix      |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|  6. Metrics: Compute Mean Absolute SHAP mean(|phi_j|), Percentage Mass,        |
|     and Mean Signed SHAP mean(phi_j) across all records of Attack_i           |
+-------------------------------------------------------------------------------+
```

1. **Space of Explanation:** SHAP calculations are performed in the model's raw margin (log-odds) space using `shap.TreeExplainer(classifier)`:
   $$\text{Margin}(x) = \phi_0 + \sum_{i=1}^{95} \phi_i(x)$$
2. **Aggregated Attribution:**
   For any original categorical feature $C_k$ mapped to transformed columns $J_k \subset \{1, \dots, 95\}$:
   $$\Phi_{C_k}(x) = \sum_{j \in J_k} \phi_j(x)$$
3. **Ranking Metric:**
   Features are ranked by **Mean Absolute SHAP** across all $N_k$ attack instances:
   $$\text{MeanAbsSHAP}(f) = \frac{1}{N_k} \sum_{i=1}^{N_k} |\Phi_f(x^{(i)})|$$
   This prevents positive and negative counterbalancing effects from obscuring important features.
4. **Directional Attribution:**
   **Mean Signed SHAP** assesses the net directional bias:
   $$\text{MeanSignedSHAP}(f) = \frac{1}{N_k} \sum_{i=1}^{N_k} \Phi_f(x^{(i)})$$
   - Positive ($\text{MeanSignedSHAP} > 0$): On average, pushes predictions toward **ATTACK**.
   - Negative ($\text{MeanSignedSHAP} < 0$): On average, pushes predictions toward **NORMAL**.

---

## 4. ATTACK COVERAGE & SAMPLE COUNTS

The project defines 17 attack types from Phase 2. Of these, **14 attack types** are represented with sensor-level telemetry in the evaluation test set. Exactly **3 control-plane attacks** have 0 sensor-level samples due to Phase 3 domain design.

### Full Attack Inventory & Test Set Distribution

| Attack Type | Category | Test Sample Count | Sensor-Level SHAP Status | Reason / Eligibility |
| :--- | :--- | :---: | :---: | :--- |
| **Sensor Freeze Attack** | Sensor | 402 | **Analyzed** | Full sensor telemetry available |
| **Sensor Drift Attack** | Sensor | 399 | **Analyzed** | Full sensor telemetry available |
| **False Data Injection Attack** | Sensor | 392 | **Analyzed** | Full sensor telemetry available |
| **MQTT Topic Hijacking** | Network | 388 | **Analyzed** | Full sensor telemetry available |
| **Replay Attack** | Network | 387 | **Analyzed** | Full sensor telemetry available |
| **Slow Drift Attack** | Sensor | 384 | **Analyzed** | Full sensor telemetry available |
| **DoS Attack** | Network | 380 | **Analyzed** | Full sensor telemetry available |
| **Sensor Noise Injection Attack** | Sensor | 380 | **Analyzed** | Full sensor telemetry available |
| **Intermittent Attack** | Sensor | 365 | **Analyzed** | Full sensor telemetry available |
| **Packet Delay Attack** | Network | 361 | **Analyzed** | Full sensor telemetry available |
| **Packet Drop Attack** | Network | 355 | **Analyzed** | Full sensor telemetry available |
| **Motor Overload Attack** | Physical | 93 | **Analyzed** | Target machine sensors available |
| **Valve Stuck Attack** | Physical | 19 | **Analyzed** | Valve pressure sensor available |
| **Sensor Spoofing Attack** | Sensor | 11 | **Analyzed** | Target sensor available |
| **PLC Command Injection** | Control-Plane | 0 | **Excluded** | *Not available for sensor-level SHAP analysis because Phase 3 intentionally assigns zero sensor-level labels to this control-plane attack.* |
| **Unauthorized Command** | Control-Plane | 0 | **Excluded** | *Not available for sensor-level SHAP analysis because Phase 3 intentionally assigns zero sensor-level labels to this control-plane attack.* |
| **Setpoint Manipulation** | Control-Plane | 0 | **Excluded** | *Not available for sensor-level SHAP analysis because Phase 3 intentionally assigns zero sensor-level labels to this control-plane attack.* |
| **Total Attack Records** | — | **4,316** | **14 Analyzed** | 3 Control-plane attacks cleanly excluded |

> **Domain Verification Note:** Phase 3 explicitly established (Change 3.1) that PLC control-plane attacks interact with Modbus/EtherNet/IP control registers and do not compromise normal sensor MQTT telemetry packets. In strict adherence to scientific integrity, **zero fake or synthetic records were generated** for these classes.

---

## 5. ATTACK-SPECIFIC TOP FEATURES (RANKINGS & PERCENTAGES)

Below is the authoritative summary of the top features for all 14 evaluated attack classes, drawn directly from `reports/phase6/attack_specific/phase6_attack_specific_top10.csv`.

### 1. DoS Attack ($N = 380$)
- **Top 5 Features:**
  1. `rolling_time_delta_5` (Mean |SHAP| = 3.4659, $+3.4621$, **43.47%**)
  2. `plant_duplicate_ratio_19` (Mean |SHAP| = 2.1461, $+2.1461$, **26.92%**)
  3. `rolling_time_delta_std_5` (Mean |SHAP| = 0.6281, $+0.3547$, **7.88%**)
  4. `time_delta` (Mean |SHAP| = 0.5804, $+0.5160$, **7.28%**)
  5. `topic` (Mean |SHAP| = 0.1132, $-0.1132$, **1.42%**)
- *Interpretation:* The model relies overwhelmingly on inter-arrival timing distortion (`rolling_time_delta_5`) and plant-wide duplicate ratios to detect DoS floods.

### 2. Replay Attack ($N = 387$)
- **Top 5 Features:**
  1. `rolling_global_td_std_10` (Mean |SHAP| = 4.0229, $+4.0229$, **37.84%**)
  2. `packet_rate_10` (Mean |SHAP| = 1.5383, $+1.5294$, **14.47%**)
  3. `rolling_time_delta_std_5` (Mean |SHAP| = 1.2973, $+1.2973$, **12.20%**)
  4. `plant_duplicate_ratio_19` (Mean |SHAP| = 1.0933, $+0.9164$, **10.28%**)
  5. `rolling_time_delta_5` (Mean |SHAP| = 0.6238, $-0.4256$, **5.87%**)
- *Interpretation:* Shows sharp reliance on global arrival time variance (`rolling_global_td_std_10`) and short-term packet rate bursts (`packet_rate_10`), reflecting telemetry re-injection dynamics.

### 3. Packet Delay Attack ($N = 361$)
- **Top 5 Features:**
  1. `rolling_time_delta_5` (Mean |SHAP| = 3.5446, $+3.5446$, **50.37%**)
  2. `rolling_time_delta_std_5` (Mean |SHAP| = 0.7977, $+0.7041$, **11.33%**)
  3. `time_delta` (Mean |SHAP| = 0.6228, $+0.5005$, **8.85%**)
  4. `plant_duplicate_ratio_19` (Mean |SHAP| = 0.4892, $+0.0156$, **6.95%**)
  5. `topic` (Mean |SHAP| = 0.2018, $-0.2018$, **2.87%**)
- *Interpretation:* Over 50% of the model's attribution mass rests on `rolling_time_delta_5`, indicating strong reliance on delayed packet arrivals.

### 4. Packet Drop Attack ($N = 355$)
- **Top 5 Features:**
  1. `rolling_time_delta_5` (Mean |SHAP| = 3.6138, $+3.6138$, **46.94%**)
  2. `rolling_time_delta_std_5` (Mean |SHAP| = 1.1849, $+1.1339$, **15.39%**)
  3. `plant_duplicate_ratio_19` (Mean |SHAP| = 0.8425, $-0.8385$, **10.94%**)
  4. `time_delta` (Mean |SHAP| = 0.6824, $+0.6342$, **8.86%**)
  5. `topic` (Mean |SHAP| = 0.2008, $-0.2008$, **2.61%**)
- *Interpretation:* Similar to Packet Delay, missing packet gaps heavily trigger the model's rolling time delta detectors. Noticeably, `plant_duplicate_ratio_19` acts negatively here ($-0.8385$), because dropped packets suppress duplicate counts.

### 5. MQTT Topic Hijacking ($N = 388$)
- **Top 5 Features:**
  1. `topic` (Mean |SHAP| = 7.2381, $+7.2365$, **66.77%**)
  2. `rolling_time_delta_std_5` (Mean |SHAP| = 0.8256, $+0.8020$, **7.62%**)
  3. `plant_duplicate_ratio_19` (Mean |SHAP| = 0.8048, $-0.8048$, **7.42%**)
  4. `time_delta` (Mean |SHAP| = 0.6893, $+0.6842$, **6.36%**)
  5. `rolling_time_delta_5` (Mean |SHAP| = 0.3699, $+0.1196$, **3.41%**)
- *Interpretation:* Distinctive semantic specificity: the model places **66.77%** of its decision weight directly on `topic`, where spoofed or illegitimate MQTT topic strings drive predictions toward ATTACK.

### 6. Sensor Spoofing Attack ($N = 11$)
- **Top 5 Features:**
  1. `device_id` (Mean |SHAP| = 2.2008, $+2.2008$, **24.12%**)
  2. `plant_duplicate_ratio_19` (Mean |SHAP| = 1.3291, $-1.3291$, **14.57%**)
  3. `percentage_change` (Mean |SHAP| = 1.0507, $+1.0507$, **11.51%**)
  4. `value` (Mean |SHAP| = 0.9590, $+0.9590$, **10.51%**)
  5. `rolling_time_delta_std_5` (Mean |SHAP| = 0.3777, $+0.2482$, **4.14%**)
- *Interpretation:* Uniquely identifies `device_id` as the #1 contributor (24.12%), alongside physical telemetry shift features (`percentage_change` and raw `value`). *Caution: Sample count is limited ($N=11$).*

### 7. False Data Injection Attack ($N = 392$)
- **Top 5 Features:**
  1. `plant_duplicate_ratio_19` (Mean |SHAP| = 5.4315, $+5.4315$, **61.79%**)
  2. `time_delta` (Mean |SHAP| = 0.8839, $+0.8824$, **10.05%**)
  3. `rolling_std_3` (Mean |SHAP| = 0.3194, $+0.2097$, **3.63%**)
  4. `rolling_time_delta_std_5` (Mean |SHAP| = 0.2697, $+0.2412$, **3.07%**)
  5. `percentage_change` (Mean |SHAP| = 0.2495, $+0.1053$, **2.84%**)
- *Interpretation:* Relies primarily on `plant_duplicate_ratio_19` followed by `time_delta` and physical volatility indicator `rolling_std_3`.

### 8. Sensor Drift Attack ($N = 399$)
- **Top 5 Features:**
  1. `plant_duplicate_ratio_19` (Mean |SHAP| = 5.2265, $+5.2265$, **57.33%**)
  2. `time_delta` (Mean |SHAP| = 1.1617, $+1.1547$, **12.74%**)
  3. `rolling_std_3` (Mean |SHAP| = 0.3433, $+0.2654$, **3.77%**)
  4. `rolling_time_delta_5` (Mean |SHAP| = 0.3207, $+0.1647$, **3.52%**)
  5. `rolling_time_delta_std_5` (Mean |SHAP| = 0.3150, $+0.2855$, **3.45%**)
- *Interpretation:* The model relies on drift-induced duplicate deviations and timing distortions, accompanied by local variance (`rolling_std_3`).

### 9. Sensor Freeze Attack ($N = 402$)
- **Top 5 Features:**
  1. `plant_duplicate_ratio_19` (Mean |SHAP| = 5.7573, $+5.7573$, **63.89%**)
  2. `rolling_time_delta_5` (Mean |SHAP| = 1.3781, $+1.3781$, **15.29%**)
  3. `time_delta` (Mean |SHAP| = 0.5992, $+0.4801$, **6.65%**)
  4. `rolling_time_delta_std_5` (Mean |SHAP| = 0.2372, $+0.0504$, **2.63%**)
  5. `topic` (Mean |SHAP| = 0.1354, $-0.1354$, **1.50%**)
- *Interpretation:* Highest single attribution for `plant_duplicate_ratio_19` (63.89%), reflecting static frozen sensor values repeated across telemetry intervals.

### 10. Sensor Noise Injection Attack ($N = 380$)
- **Top 5 Features:**
  1. `plant_duplicate_ratio_19` (Mean |SHAP| = 5.1427, $+5.0734$, **58.04%**)
  2. `time_delta` (Mean |SHAP| = 1.2064, $+1.1602$, **13.61%**)
  3. `rolling_time_delta_5` (Mean |SHAP| = 0.5714, $+0.4597$, **6.45%**)
  4. `rolling_time_delta_std_5` (Mean |SHAP| = 0.3017, $+0.2748$, **3.41%**)
  5. `rolling_std_3` (Mean |SHAP| = 0.2734, $+0.1994$, **3.09%**)
- *Interpretation:* High reliance on duplicate ratios and timing deltas, with high local rolling volatility (`rolling_std_3`).

### 11. Motor Overload Attack ($N = 93$)
- **Top 5 Features:**
  1. `percentage_change` (Mean |SHAP| = 0.8107, $+0.7753$, **11.30%**)
  2. `plant_duplicate_ratio_19` (Mean |SHAP| = 0.7779, $+0.5682$, **10.84%**)
  3. `rolling_time_delta_5` (Mean |SHAP| = 0.7392, $-0.7087$, **10.30%**)
  4. `value` (Mean |SHAP| = 0.6149, $+0.6007$, **8.57%**)
  5. `rolling_global_td_std_10` (Mean |SHAP| = 0.5733, $+0.5639$, **7.99%**)
- *Interpretation:* **Physical telemetry features dominate.** Unlike network attacks, `percentage_change` (11.30%), raw `value` (8.57%), and `rolling_mean_5` (7.16%) feature prominently in the top ranks.

### 12. Valve Stuck Attack ($N = 19$)
- **Top 5 Features:**
  1. `rolling_time_delta_5` (Mean |SHAP| = 1.3649, $-1.3649$, **19.02%**)
  2. `plant_duplicate_ratio_19` (Mean |SHAP| = 1.0717, $+0.7832$, **14.93%**)
  3. `device_mean_deviation` (Mean |SHAP| = 0.9320, $+0.9320$, **12.99%**)
  4. `device_id` (Mean |SHAP| = 0.5498, $+0.5498$, **7.66%**)
  5. `z_score` (Mean |SHAP| = 0.5057, $+0.5057$, **7.05%**)
- *Interpretation:* Features indicating physical stuck-valve anomalies—`device_mean_deviation` (12.99%) and `z_score` (7.05%)—rank in the top 5. *Caution: Small sample size ($N=19$).*

### 13. Intermittent Attack ($N = 365$)
- **Top 5 Features:**
  1. `plant_duplicate_ratio_19` (Mean |SHAP| = 4.4815, $+4.4670$, **52.99%**)
  2. `rolling_time_delta_5` (Mean |SHAP| = 0.8788, $+0.6810$, **10.39%**)
  3. `time_delta` (Mean |SHAP| = 0.7061, $+0.6945$, **8.35%**)
  4. `rolling_time_delta_std_5` (Mean |SHAP| = 0.3977, $+0.3176$, **4.70%**)
  5. `rolling_std_10` (Mean |SHAP| = 0.3155, $+0.2905$, **3.73%**)
- *Interpretation:* Intermittent burst behavior causes sudden changes in duplicate ratios and rolling standard deviation over 10 packets (`rolling_std_10`).

### 14. Slow Drift Attack ($N = 384$)
- **Top 5 Features:**
  1. `plant_duplicate_ratio_19` (Mean |SHAP| = 4.9917, $+4.9650$, **54.44%**)
  2. `time_delta` (Mean |SHAP| = 0.6843, $+0.6688$, **7.46%**)
  3. `rolling_time_delta_5` (Mean |SHAP| = 0.6155, $+0.3128$, **6.71%**)
  4. `rolling_time_delta_std_5` (Mean |SHAP| = 0.5405, $+0.5380$, **5.89%**)
  5. `rolling_std_3` (Mean |SHAP| = 0.3453, $+0.2783$, **3.77%**)
- *Interpretation:* The model relies on the gradual distortion of duplicate ratios combined with inter-arrival cadence deviations.

---

## 6. CROSS-ATTACK FEATURE RECURRENCE & COMPARISON

To discover which features form generic detection pillars versus attack-specific signatures, we computed the recurrence frequency across all 14 evaluated attack classes.

### Feature Recurrence Table

| Feature | Type | Top 5 Count | Top 10 Count | Top 5 Freq (%) | Top 10 Freq (%) | Average Mean \|SHAP\| | Classification |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `plant_duplicate_ratio_19` | Numeric | **14** | **14** | **100.0%** | **100.0%** | 2.827560 | Generic Backbone |
| `rolling_time_delta_5` | Numeric | **12** | **13** | **85.7%** | **92.9%** | 1.278285 | Timing Pillar |
| `rolling_time_delta_std_5` | Numeric | **12** | **13** | **85.7%** | **92.9%** | 0.553715 | Jitter Pillar |
| `time_delta` | Numeric | **10** | **13** | **71.4%** | **92.9%** | 0.618002 | Cadence Pillar |
| `topic` | Categorical | **5** | **7** | **35.7%** | **50.0%** | 0.632222 | Attack-Specific Signature |
| `rolling_std_3` | Numeric | **4** | **7** | **28.6%** | **50.0%** | 0.169224 | Sensor Volatility |
| `percentage_change` | Numeric | **3** | **9** | **21.4%** | **64.3%** | 0.252823 | Physical Magnitude |
| `rolling_global_td_std_10` | Numeric | **2** | **11** | **14.3%** | **78.6%** | 0.441090 | Network Replay Signature |
| `value` | Numeric | **2** | **4** | **14.3%** | **28.6%** | 0.170115 | Physical Measurement |
| `device_id` | Categorical | **2** | **2** | **14.3%** | **14.3%** | 0.235772 | Identity Spoofing Signature |
| `z_score` | Numeric | **1** | **6** | **7.1%** | **42.9%** | 0.125366 | Statistical Deviation |
| `packet_rate_10` | Numeric | **1** | **5** | **7.1%** | **35.7%** | 0.198712 | Burst Rate Indicator |
| `device_mean_deviation` | Numeric | **1** | **5** | **7.1%** | **35.7%** | 0.141640 | Device Anomaly Metric |
| `rolling_std_10` | Numeric | **1** | **4** | **7.1%** | **28.6%** | 0.129225 | Extended Volatility |
| `rolling_global_td_10` | Numeric | 0 | 8 | 0.0% | 57.1% | 0.121937 | Background Cadence |
| `rolling_std_5` | Numeric | 0 | 6 | 0.0% | 42.9% | 0.122268 | Intermediate Volatility |
| `global_time_delta` | Numeric | 0 | 5 | 0.0% | 35.7% | 0.094891 | Global Timing |
| `rel_volatility` | Numeric | 0 | 2 | 0.0% | 14.3% | 0.094231 | Relative Jitter |
| `seq_gap_dev` | Numeric | 0 | 2 | 0.0% | 14.3% | 0.044175 | Sequence Integrity |

### Attack-Specific Reliance Signatures
1. **MQTT Topic Hijacking:** `topic` accounts for **66.77%** of the attribution mass (mean |SHAP| = 7.238).
2. **Replay Attack:** `rolling_global_td_std_10` (37.84%) and `packet_rate_10` (14.47%) represent **52.31%** of decision reliance.
3. **Sensor Spoofing:** `device_id` represents **24.12%** of decision reliance, followed by `percentage_change` and `value`.
4. **Motor Overload:** Physical metrics (`percentage_change`, `value`, `rolling_mean_5`, `rel_volatility`) collectively comprise over **35%** of the explanation.

---

## 7. CONTROL CHECK: DATASET CADENCE & TIMING CHARACTERISTICS

In accordance with Step 8 of the project rules, we explicitly inspected whether attack-specific SHAP attributions are dominated by dataset cadence and timing features:
- **`plant_duplicate_ratio_19`**: Top-5 in 14/14 attacks ($100\%$). Average mean |SHAP|: $2.828$.
- **`rolling_time_delta_5`**: Top-5 in 12/14 attacks ($85.7\%$). Average mean |SHAP|: $1.278$.
- **`rolling_time_delta_std_5`**: Top-5 in 12/14 attacks ($85.7\%$). Average mean |SHAP|: $0.554$.
- **`time_delta`**: Top-5 in 10/14 attacks ($71.4\%$). Average mean |SHAP|: $0.618$.

### Scientific Disclosure
These features are **honestly reported and not artificially suppressed**. The digital twin simulation architecture emits packets on strict per-sensor schedules. Consequently:
1. Whenever network attacks (DoS, Delay, Drop) occur, inter-arrival intervals are disrupted immediately.
2. Whenever sensor attacks (Freeze, Drift, Noise) alter packet values or repetition patterns, the rolling duplicate window across the 19 plant devices is altered.
3. The frozen XGBoost model has capitalized heavily on these statistical cadence markers. This is genuine model behavior and highlights an operational reality: the IDS acts primarily as a temporal and cadence integrity monitor, supplemented by physical domain metrics.

---

## 8. REPRESENTATIVE LOCAL EXPLANATIONS

Using the Phase 6.4 `LocalShapExplainer`, we extracted representative instances from the test set for five target attack classes, computing their additive decompositions and generating publication-grade waterfall plots in `reports/phase6/attack_specific/`.

### Summary of Representative Instances

| Target Attack | Record ID | Actual Label | Predicted Label | Attack Probability | Raw Margin | Base Value | Fidelity Error | Waterfall Artifact |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **DoS Attack** | 3203 | 1 | ATTACK | 99.36% | +5.0460 | -0.2719 | $4.05 \times 10^{-6}$ | `local_shap_dos_attack_3203.png` |
| **Replay Attack** | 10977 | 1 | ATTACK | 99.99% | +9.1711 | -0.2719 | $3.10 \times 10^{-6}$ | `local_shap_replay_attack_10977.png` |
| **Sensor Freeze** | 48510 | 1 | ATTACK | 99.94% | +7.4103 | -0.2719 | $3.10 \times 10^{-6}$ | `local_shap_sensor_freeze_attack_48510.png` |
| **Motor Overload**| 75660 | 1 | ATTACK | 99.66% | +5.6721 | -0.2719 | $3.10 \times 10^{-6}$ | `local_shap_motor_overload_attack_75660.png` |
| **Slow Drift** | 88360 | 1 | ATTACK | 99.99% | +9.0006 | -0.2719 | $3.10 \times 10^{-6}$ | `local_shap_slow_drift_attack_88360.png` |

### Detailed Representative Decompositions

#### 1. DoS Attack (Record #3203)
- **Prediction:** ATTACK ($P = 99.36\%$, Raw Margin = $+5.05$, Base = $-0.27$)
- **Top Positive Contributors (Pushes toward Attack):**
  1. `plant_duplicate_ratio_19` ($\phi = +3.326$, raw value: $0.316$)
  2. `rolling_time_delta_5` ($\phi = +0.833$, raw value: $0.063\text{ s}$)
  3. `rolling_time_delta_std_5` ($\phi = +0.733$, raw value: $0.0025$)
  4. `time_delta` ($\phi = +0.639$, raw value: $0.066\text{ s}$)
  5. `rolling_global_td_10` ($\phi = +0.277$)
- **Top Negative Contributors (Pushes toward Normal):**
  1. `topic` ($\phi = -0.111$, raw: `factory/line1/pressure`)
  2. `device_mean_deviation` ($\phi = -0.100$, raw: $-0.827$)

#### 2. Replay Attack (Record #10977)
- **Prediction:** ATTACK ($P = 99.99\%$, Raw Margin = $+9.17$, Base = $-0.27$)
- **Top Positive Contributors (Pushes toward Attack):**
  1. `rolling_global_td_std_10` ($\phi = +4.405$, raw: $2.347$)
  2. `packet_rate_10` ($\phi = +1.836$, raw: $-6.593$)
  3. `rolling_time_delta_std_5` ($\phi = +1.554$, raw: $1.569$)
  4. `rolling_global_td_10` ($\phi = +0.424$)
  5. `rolling_seq_std_5` ($\phi = +0.422$)
- **Top Negative Contributors (Pushes toward Normal):**
  1. `rolling_mean_3` ($\phi = -0.053$, raw: $0.100$)
  2. `topic` ($\phi = -0.051$, raw: `factory/line1/vibration`)

#### 3. Sensor Freeze Attack (Record #48510)
- **Prediction:** ATTACK ($P = 99.94\%$, Raw Margin = $+7.41$, Base = $-0.27$)
- **Top Positive Contributors (Pushes toward Attack):**
  1. `plant_duplicate_ratio_19` ($\phi = +5.551$, raw: $1.000$)
  2. `rolling_time_delta_5` ($\phi = +1.436$, raw: $0.169\text{ s}$)
  3. `time_delta` ($\phi = +0.733$, raw: $0.171\text{ s}$)
  4. `value` ($\phi = +0.074$, raw: $0.100$)
  5. `device_mean_deviation` ($\phi = +0.056$, raw: $-0.494$)
- **Top Negative Contributors (Pushes toward Normal):**
  1. `seq_gap_dev` ($\phi = -0.083$)
  2. `topic` ($\phi = -0.079$)

#### 4. Motor Overload Attack (Record #75660)
- **Prediction:** ATTACK ($P = 99.66\%$, Raw Margin = $+5.67$, Base = $-0.27$)
- **Top Positive Contributors (Pushes toward Attack):**
  1. `percentage_change` ($\phi = +1.784$, raw: $+0.00063$)
  2. `plant_duplicate_ratio_19` ($\phi = +1.105$, raw: $0.632$)
  3. `rel_volatility` ($\phi = +0.641$, raw: $0.0109$)
  4. `packet_rate_10` ($\phi = +0.497$, raw: $41.87$)
  5. `rolling_std_10` ($\phi = +0.449$, raw: $0.0908$)
- **Top Negative Contributors (Pushes toward Normal):**
  1. `rolling_time_delta_5` ($\phi = -1.104$, raw: $0.258\text{ s}$)
  2. `time_delta` ($\phi = -0.239$, raw: $0.238\text{ s}$)

#### 5. Slow Drift Attack (Record #88360)
- **Prediction:** ATTACK ($P = 99.99\%$, Raw Margin = $+9.00$, Base = $-0.27$)
- **Top Positive Contributors (Pushes toward Attack):**
  1. `plant_duplicate_ratio_19` ($\phi = +5.141$, raw: $0.158$)
  2. `time_delta` ($\phi = +0.880$, raw: $0.318\text{ s}$)
  3. `rolling_time_delta_5` ($\phi = +0.857$, raw: $0.312\text{ s}$)
  4. `rolling_time_delta_std_5` ($\phi = +0.712$, raw: $0.0197$)
  5. `rolling_global_td_std_10` ($\phi = +0.498$, raw: $0.100$)
- **Top Negative Contributors (Pushes toward Normal):**
  1. `rolling_seq_std_5` ($\phi = -0.099$)
  2. `topic` ($\phi = -0.067$)

---

## 9. SHAP FIDELITY VERIFICATION

To verify the numerical exactness of the TreeExplainer implementation, additive reconstruction fidelity was verified across $N=200$ randomly selected attack records from the test split.

For each observation $x$, the raw decision margin $f(x)$ predicted by the classifier was compared against the sum of the base value $\phi_0$ and all $95$ transformed SHAP values:

$$\epsilon(x) = \left| f(x) - \left( \phi_0 + \sum_{j=1}^{95} \phi_j(x) \right) \right|$$

### Fidelity Results
- **Samples Checked:** 200 attack records
- **Maximum Absolute Error:** $1.05 \times 10^{-5}$ ($0.0000105$)
- **Mean Absolute Error:** $2.59 \times 10^{-6}$ ($0.00000259$)
- **Tolerance Requirement:** $< 1.0 \times 10^{-4}$ ($0.0001$)
- **Status:** **PASSED (100% compliant)**

---

## 10. SCIENTIFIC LIMITATIONS & THREATS TO VALIDITY

1. **Simulated Digital-Twin Environment:** Telemetry is generated from an industrial digital twin simulating a manufacturing line with 19 sensors. Real-world physical environments exhibit non-stationary sensor noise and asynchronous packet routing.
2. **Cadence Feature Dominance:** The model relies strongly on `plant_duplicate_ratio_19` and rolling time deltas. In production deployments where background network latency varies dynamically, reliance on these features must be monitored for drift.
3. **Imbalanced Attack Sample Counts in Test Split:** While high-frequency attacks have $350\text{--}400$ samples (e.g., Sensor Freeze $N=402$, DoS $N=380$), low-frequency targeted attacks have smaller sample sizes:
   - Motor Overload: $N = 93$
   - Valve Stuck: $N = 19$
   - Sensor Spoofing: $N = 11$  
   *Rankings for $N < 30$ must be interpreted as preliminary empirical observations rather than definitive population distributions.*
4. **Control-Plane Attack Exclusion:** In accordance with Phase 3 design, PLC attacks (`PLC Command Injection`, `Unauthorized Command`, `Setpoint Manipulation`) produce 0 sensor-level alerts because they target industrial control logic rather than sensor communications. They require dedicated control-plane monitoring rather than sensor-level ML.
5. **Stratified Benchmark Context:** The 99.65% multi-attack accuracy reported in Phase 4.1 applies strictly to the frozen stratified benchmark and should not be cited as universal field accuracy under arbitrary out-of-distribution attacks.

---

## 11. UNIT TEST SUITE AND VERIFICATION

A dedicated test suite was implemented in `backend/ml/tests/test_attack_specific_shap.py`, verifying all Phase 6.5 requirements.

### Test Execution Summary
- **Test Command:**  
  `PYTHONPATH=. ./venv/bin/python -m unittest backend/ml/tests/test_attack_specific_shap.py -v`
- **Output:**
  ```
  test_01_frozen_model_loads ... ok
  test_02_attack_specific_dataset_selection ... ok
  test_03_no_control_plane_fake_sensor_samples ... ok
  test_04_every_analyzed_attack_has_label_one ... ok
  test_05_attack_type_correctly_preserved ... ok
  test_06_shap_transformed_has_95_features ... ok
  test_07_aggregated_output_has_32_original_features ... ok
  test_08_mean_absolute_shap_non_negative ... ok
  test_09_representative_shap_fidelity_less_than_1e4 ... ok
  test_10_missing_zero_sample_attack_classes_handled ... ok
  test_11_cross_attack_frequency_computation ... ok

  Ran 11 tests in 2.646s
  OK
  ```

### Full Regression Suite Results
1. `backend/ml/tests/test_local_shap_explainer.py` (Phase 6.4): **11/11 tests pass (OK)**
2. `backend/ml/tests` (Full ML Suite): **30/30 tests pass (OK)**
3. `backend/tests` (Full Pipeline Suite): **26/26 tests pass (OK)**
4. Tracked file integrity: `git diff --check` reported **zero issues**.

---

## 12. GENERATED ARTIFACTS INVENTORY

All generated artifacts are preserved under `reports/phase6/attack_specific/`:

1. **`phase6_attack_specific_shap.csv`** (35 KB)  
   Complete tabular record of mean |SHAP|, mean signed SHAP, percentage contribution, and rank across all 32 features for every evaluated attack type.
2. **`phase6_attack_specific_top10.csv`** (11 KB)  
   Clean filtered table of the top 10 features for all 14 evaluated attack classes.
3. **`phase6_cross_attack_feature_frequency.csv`** (1.7 KB)  
   Cross-attack feature recurrence frequencies in Top 5 and Top 10 across all attack classes.
4. **`phase6_attack_specific_heatmap.png`** (700 KB)  
   High-resolution publication heatmap displaying attack types vs top original physical features with annotated cell values.
5. **`phase6_attack_specific_rankings.png`** (799 KB)  
   Multi-panel faceted horizontal bar chart displaying the top 5 features with color-coded feature types for every attack class.
6. **`phase6_attack_specific_representatives.json`** (11 KB)  
   Structured JSON file recording full metrics, margin breakdowns, top positive and negative contributors, and fidelity metrics for the representative attack instances.
7. **Representative Waterfall Plots:**
   - `local_shap_dos_attack_3203.png` (192 KB)
   - `local_shap_replay_attack_10977.png` (186 KB)
   - `local_shap_sensor_freeze_attack_48510.png` (182 KB)
   - `local_shap_motor_overload_attack_75660.png` (196 KB)
   - `local_shap_slow_drift_attack_88360.png` (187 KB)

---

## 13. FINAL VERDICT

```
================================================================================
FINAL VERDICT: A — PASS / READY FOR 6.6
================================================================================
```

### Justification:
1. **Mathematical Soundness:** Exact additive TreeExplainer computation in log-odds space with reconstruction fidelity error $< 1.1 \times 10^{-5}$ ($< 10^{-4}$ requirement).
2. **Feature Aggregation:** Transformed 95 one-hot features mapped and aggregated back to the 32 original physical and timing inputs without distortion.
3. **Scientific Integrity:** Zero fake samples created for control-plane attacks; strictly non-causal language preserved throughout; timing dominance disclosed honestly.
4. **Zero Model Tampering:** The frozen Phase 5 H3-32 model (`xgboost_h3_32.pkl`) and its fitted pipeline remain completely untouched.
5. **Comprehensive Validation:** 11/11 Phase 6.5 tests passed, 11/11 Phase 6.4 tests passed, and 56 total project unit tests passed cleanly.
6. **Production Readiness:** Full visualization and CSV artifacts generated in `reports/phase6/attack_specific/`.

The LightX-IDS codebase is fully prepared for **Phase 6.6: Natural-Language Explanations**.
