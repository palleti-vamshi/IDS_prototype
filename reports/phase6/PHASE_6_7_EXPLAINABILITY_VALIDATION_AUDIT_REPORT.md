# LIGHTX-IDS PHASE 6.7: EXPLAINABILITY VALIDATION & AUDIT REPORT

**Project:** LightX-IDS: Lightweight Explainable Real-Time Intrusion Detection System for Industrial IoT Networks  
**Author:** Antigravity Autonomous Agent (Pair Programming with Vamshi)  
**Date:** October 4, 2026  
**Branch:** `antigravity-development`  
**Phase:** 6.7 — Explainability Validation & Audit  
**Status:** COMPLETE  
**Authoritative Frozen Model:** `backend/ml/saved_models/xgboost_h3_32.pkl`  
**Authoritative Dataset:** `dataset/lightx_ids_dataset_100k.csv` (Seed 42 Stratified Split)

---

## 1. EXECUTIVE SUMMARY

This report presents the independent, rigorous scientific audit of the entire **LightX-IDS Phase 6 Explainability Pipeline** (Phases 6.1 through 6.6). 

The audit was executed under zero-modification constraints: no model retraining, no threshold adjustments, no feature tampering, and no suppression of inconvenient empirical findings. 

All 16 audit dimensions were systematically evaluated. The audit confirms that the explainability stack faithfully explains the frozen Phase 5 H3-32 XGBoost classifier (`xgboost_h3_32.pkl`), operates strictly in read-only inference mode with zero data leakage, achieves additive TreeExplainer reconstruction fidelity error $< 8.6 \times 10^{-6}$, and generates human-readable explanations that are 100% compliant with strict non-causal language and control-room safety policies.

### Audit Scorecard Summary
| Audit Item | Scope | Status | Key Metric / Verification |
| :--- | :--- | :---: | :--- |
| **Audit 1: Model Immutability** | Cryptographic & size integrity of saved models | **PASS** | SHA-256 unchanged; distinct from base XGBoost |
| **Audit 2: Pipeline Structure** | Architecture, feature dimensionality, and order | **PASS** | Pipeline: `preprocessor` + `classifier`; 32 original $\rightarrow$ 95 transformed |
| **Audit 3: Dataset Separation** | 80/10/10 disjointness and test split membership | **PASS** | Disjoint; all 6 representative records in test set |
| **Audit 4: Leakage Audit** | Read-only verification of explainability modules | **PASS** | Zero `.fit()`, `.fit_transform()`, or test recalculations |
| **Audit 5: Feature Causality** | Temporal integrity of the 32 input features | **PASS WITH LIMITATION** | Zero forward-looking shifts; cadence reliance documented |
| **Audit 6: SHAP Fidelity** | Additive log-odds reconstruction $\phi_0 + \sum \phi_i \approx f(x)$ | **PASS** | Max error: $8.58 \times 10^{-6}$ (Threshold: $< 1.0 \times 10^{-4}$) |
| **Audit 7: 95 $\rightarrow$ 32 Aggregation** | One-hot aggregation back to original features | **PASS** | Aggregation mismatch: $2.02 \times 10^{-6}$; all 7 categoricals preserved |
| **Audit 8: Attack Coverage** | 14 active attacks & 3 control-plane exclusions | **PASS WITH LIMITATION** | 14 analyzed, 0 fakes for control plane; small sample sizes noted |
| **Audit 9: Faithfulness** | Narrative alignment with numerical SHAP values | **PASS** | 20/20 test samples 100% faithful; direction and magnitudes match |
| **Audit 10: Language Safety** | Elimination of causal overclaiming & unsafe commands | **PASS** | 0 causal claims; 0 unsafe physical commands |
| **Audit 11: Determinism** | Reproducibility across duplicate runs | **PASS** | Bitwise identical outputs across duplicate executions |
| **Audit 12: Representative Consistency** | Consistency against stored Phase 6.4–6.6 artifacts | **PASS** | 6/6 representative cases perfectly consistent |
| **Audit 13: Regression Testing** | Full ML and backend test suite execution | **PASS** | 43 ML tests pass; 26 backend tests pass; `git diff --check` clean |
| **Audit 14: Artifact Integrity** | Verification of all Phase 6 reports and figures | **PASS** | 17/17 required Phase 6 files and directories present |
| **Audit 15: Reproducibility** | Python runtime & package version lock | **PASS** | Fully documented environment (`python 3.14.6`, `shap 0.52.0`) |
| **Audit 16: Freeze Verification** | Immutability of Phase 1–5 configurations | **PASS** | Phase 4.1 (99.65%) & Phase 5 H3-32 ablation strictly frozen |

---

## 2. AUDIT SCOPE & METHODOLOGY

The audit examined every software component and analytical output created across Phase 6:
- `backend/ml/explainability/shap_local_explainer.py` (Local SHAP & Waterfall plotting)
- `backend/ml/explainability/attack_explainer.py` (Attack-specific attribution & cross-attack analysis)
- `backend/ml/explainability/human_explainer.py` (Plain-English translation layer)
- `reports/phase6/` (Global importance, local waterfalls, attack heatmaps, and representative JSONs)

Verification was performed using an automated verification harness (`scratch/run_phase6_7_audit.py`) on the authoritative environment (`Python 3.14.6`, `XGBoost 3.3.0`, `SHAP 0.52.0`, `scikit-learn 1.9.0`).

---

## 3. AUDIT 1 — MODEL IMMUTABILITY

**Status:** `PASS`

The frozen Phase 5 H3-32 model file was cryptographically hashed and compared against the baseline unablated Phase 4 model to verify model distinction and file preservation.

- **Target Model:** `backend/ml/saved_models/xgboost_h3_32.pkl`
  - **SHA-256 Hash:** `3ba36c9dd2192d36182077f5f191708c279ac6020f17dd5d524429e5b63e6a58`
  - **File Size:** `2,600,231 bytes` (~2.48 MB)
- **Baseline Model:** `backend/ml/saved_models/xgboost.pkl`
  - **SHA-256 Hash:** `376af82ad3120a7a428453fef0616983ad3ee654d3826c96b1da5ec73384ea34`
  - **File Size:** `2,513,323 bytes` (~2.40 MB)
- **Model Disjointness:** Verified. The H3-32 model has not been replaced or overwritten by the baseline model, and its byte content was not modified during explainability operations.

---

## 4. AUDIT 2 — MODEL PIPELINE STRUCTURE

**Status:** `PASS`

The internal architecture of the deserialized H3-32 model was inspected:
- **Pipeline Named Steps:** Exactly `['preprocessor', 'classifier']`
- **Classifier Architecture:** `xgboost.sklearn.XGBClassifier` (100 estimators, max depth 6, learning rate 0.1)
- **Input Feature Count:** 32 original features (25 numeric + 7 categorical)
- **Transformed Feature Count:** Exactly 95 features after `ColumnTransformer` execution (StandardScaler for numeric, OneHotEncoder for categorical)
- **Feature Canonical Alignment:** The feature ordering enforced by `LocalShapExplainer`, `AttackSpecificShapExplainer`, and `HumanReadableExplainer` perfectly matches the scikit-learn `preprocessor.get_feature_names_out()` sequence.

---

## 5. AUDIT 3 — TRAIN / VALIDATION / TEST SEPARATION

**Status:** `PASS`

The dataset was reconstructed using the authoritative Seed 42 stratified split protocol from `dataset/lightx_ids_dataset_100k.csv`:
- **Total Dataset Size:** 100,000 records
- **Training Split:** 80,000 records (80.00%)
- **Validation Split:** 9,999 records (10.00%)
- **Test Split:** 10,001 records (10.00%)
- **Disjointness Check:**
  - $\text{Train} \cap \text{Val} = \emptyset$ (0 overlapping records)
  - $\text{Train} \cap \text{Test} = \emptyset$ (0 overlapping records)
  - $\text{Val} \cap \text{Test} = \emptyset$ (0 overlapping records)
- **Representative Case Membership:**
  All 6 authoritative representative records belong strictly to the **Test Split**:
  - Record #3203 (DoS Attack): **Test Split** (`True`)
  - Record #10977 (Replay Attack): **Test Split** (`True`)
  - Record #48510 (Sensor Freeze Attack): **Test Split** (`True`)
  - Record #75660 (Motor Overload Attack): **Test Split** (`True`)
  - Record #88360 (Slow Drift Attack): **Test Split** (`True`)
  - Record #93364 (Nominal Normal): **Test Split** (`True`)

---

## 6. AUDIT 4 — EXPLAINABILITY DATA LEAKAGE

**Status:** `PASS`

A code audit of `shap_local_explainer.py`, `attack_explainer.py`, and `human_explainer.py` verified that the explainability layer is strictly **read-only**:
- **Zero In-Situ Fitting:** Neither `.fit()` nor `.fit_transform()` is invoked anywhere within the explainability package.
- **Frozen Transformations:** All telemetry preprocessing routes exclusively through the pre-fitted `preprocessor.transform()`.
- **Zero Threshold Tuning:** Decision thresholds are fixed at $\tau^* = 0.35$ (frozen from Phase 4.1/5 validation).
- **Stateless Batching:** Batch attack explanations compute summary statistics on test subsets without updating baseline statistics or model state.

---

## 7. AUDIT 5 — FEATURE CAUSALITY & TEMPORAL AUDIT

**Status:** `PASS WITH LIMITATION`

All 32 H3-32 features and their implementations in `FeatureGenerator` were audited for temporal validity:
- **Causal Rolling Formulation:** All rolling window computations (`rolling_time_delta_5`, `rolling_std_3`, `rolling_global_td_10`, etc.) use backwards-looking causal windows with `closed='left'` or standard sequential rolling buffers.
- **Zero Lookahead:** No negative shift operations (`shift(-k)`), centered windows (`center=True`), or future-looking index manipulations exist in the feature generation pipeline.

### Documented Project Limitation (Cadence Reliance):
The feature causality audit confirms mathematical causality (no future information leakage), but underscores a known dataset characteristic: the frozen model relies heavily on `plant_duplicate_ratio_19` and `rolling_time_delta_5` across multiple attack types. In a synthetic digital twin with fixed periodic sensor publishing intervals, attacks disturb timing regularities immediately. This is genuine model behavior and is documented as an empirical property of the simulator.

---

## 8. AUDIT 6 — SHAP ADDITIVE FIDELITY

**Status:** `PASS`

Additive reconstruction fidelity was audited across 120 test samples balanced across Normal, DoS, Replay, Sensor Freeze, Motor Overload, and Slow Drift:

$$\text{Error}(x) = \left| f_{\text{raw}}(x) - \left( \phi_0 + \sum_{i=1}^{95} \phi_i(x) \right) \right|$$

### Fidelity Error Statistics ($N=120$)
- **Mean Absolute Error (MAE):** $2.39 \times 10^{-6}$
- **Median Absolute Error:** $1.91 \times 10^{-6}$
- **95th Percentile Error:** $5.75 \times 10^{-6}$
- **Maximum Absolute Error:** $8.58 \times 10^{-6}$
- **Samples Exceeding $1.0 \times 10^{-4}$:** **0 samples (0.0%)**
- **Evaluation:** Reconstruction fidelity easily satisfies the $< 1.0 \times 10^{-4}$ benchmark by more than an order of magnitude.

---

## 9. AUDIT 7 — 95 $\rightarrow$ 32 FEATURE AGGREGATION

**Status:** `PASS`

The explainability layer aggregates the 95 one-hot transformed SHAP values back to the 32 physical input features by summing all dummy indicator attributions for each categorical feature:

$$\Phi_{C_k} = \sum_{j \in \text{OneHot}(C_k)} \phi_j$$

### Aggregation Verification
- **Total Transformed Features:** 95
- **Total Physical Target Features:** 32 (25 numeric, 7 categorical)
- **Categorical One-Hot Dummy Counts:**
  - `topic`: 11 categories
  - `device_id`: 19 categories
  - `sensor_code`: 19 categories
  - `sensor_type`: 10 categories
  - `unit`: 9 categories
  - `status`: 1 category
  - `source`: 1 category
  *(Sum of categorical dummies = 70; Numeric features = 25; Total = 95)*
- **Maximum Aggregation Mismatch ($\max \left| \sum_{j=1}^{95} \phi_j - \sum_{k=1}^{32} \Phi_k \right|$):** **$2.02 \times 10^{-6}$**
- **Conclusion:** Aggregation is mathematically exact down to single-precision floating point limits. Zero attribution mass is lost or double-counted.

---

## 10. AUDIT 8 — ATTACK-SPECIFIC COVERAGE & ZERO-SAMPLE POLICY

**Status:** `PASS WITH LIMITATION`

The test split ($N=10,001$) contains 4,316 attack records spanning 14 sensor-level attack types:
- **Analyzed Attacks (14):** Sensor Freeze (402), Sensor Drift (399), False Data Injection (392), MQTT Topic Hijacking (388), Replay (387), Slow Drift (384), DoS (380), Sensor Noise Injection (380), Intermittent (365), Packet Delay (361), Packet Drop (355), Motor Overload (93), Valve Stuck (19), Sensor Spoofing (11).
- **Targeted Label Purity:** 100% of rows evaluated for attack-specific SHAP have `label == 1` and matching `attack_type`.
- **Control-Plane Exclusion:** Exactly 3 control-plane attacks (`PLC Command Injection`, `Unauthorized Command`, `Setpoint Manipulation`) have 0 sensor-level samples. In strict accordance with Phase 3 Change 3.1 domain design, **zero synthetic or fake sensor samples were manufactured**.

### Documented Limitation:
Attacks targeting specific actuators (e.g. `Sensor Spoofing` $N=11$, `Valve Stuck` $N=19$) have limited sample representation in the test set compared to network-wide attacks ($N \approx 380$). Their top feature rankings must be treated as indicative rather than asymptotic population estimates.

---

## 11. AUDIT 9 — HUMAN-READABLE FAITHFULNESS

**Status:** `PASS`

20 real local explanations generated across diverse test cases were audited against the underlying numerical SHAP tensors:
1. **Directional Faithfulness:** 100% of features in `top_attack_contributors` have strictly positive SHAP values ($\phi > 0$).
2. **Opposition Faithfulness:** 100% of features in `top_normal_contributors` have strictly negative SHAP values ($\phi < 0$).
3. **Probability Coherence:** $P(\text{Attack}) + P(\text{Normal}) = 1.0000$ across all samples.
4. **Feature Integrity:** All referenced features in summaries and tables exist in `ALL_32_FEATURES`.
5. **Contextual Distinction:** The ground-truth recorded label is consistently reported under `Recorded Context` and is never claimed to be an output inferred by the model.

---

## 12. AUDIT 10 — LANGUAGE SAFETY & CONTROL ROOM POLICY

**Status:** `PASS`

An automated scan of all text generated by `HumanReadableExplainer` across the test samples yielded:
- **Prohibited Causal Claims:** **0 instances** of `"caused by"`, `"caused the attack"`, `"proves"`, `"root cause"`, `"definitely"`, or `"guarantees"`.
- **Unsafe Physical Control Commands:** **0 instances** of `"shut down"`, `"disconnect the plc"`, or `"stop production"`.
- **Advisory Alignment:** Operator interpretation consistently employs non-disruptive, advisory terminology: *"Review"*, *"Investigate"*, *"Verify"*, *"Inspect"*, *"Correlate with plant logs"*.

---

## 13. AUDIT 11 — DETERMINISM

**Status:** `PASS`

10 distinct test telemetry records were processed twice in independent passes:
- **Prediction Determinism:** Identical classifications (`ATTACK` vs. `NORMAL`).
- **Probability Determinism:** Difference $< 1.0 \times 10^{-12}$.
- **Margin Determinism:** Difference $< 1.0 \times 10^{-12}$.
- **Transformed SHAP (95) Determinism:** Difference $< 1.0 \times 10^{-12}$.
- **Aggregated SHAP (32) Determinism:** Difference $< 1.0 \times 10^{-12}$.
- **Narrative Text Determinism:** Bit-for-bit identical markdown and console string outputs.
- **Model State Invariance:** Cryptographic hash of `xgboost_h3_32.pkl` after duplicate execution remained identical (`3ba36c9dd2192d36182077f5f191708c279ac6020f17dd5d524429e5b63e6a58`).

---

## 14. AUDIT 12 — REPRESENTATIVE EXPLANATION CONSISTENCY

**Status:** `PASS`

Explanations were regenerated from scratch for the 6 representative records and compared against the persisted Phase 6.4/6.5/6.6 artifacts:
- **Record #3203 (DoS Attack):** Pred: `ATTACK`, $P = 99.36\%$, Top Driver: `plant_duplicate_ratio_19` $\rightarrow$ **Consistent (`True`)**
- **Record #10977 (Replay Attack):** Pred: `ATTACK`, $P = 99.99\%$, Top Driver: `rolling_global_td_std_10` $\rightarrow$ **Consistent (`True`)**
- **Record #48510 (Sensor Freeze Attack):** Pred: `ATTACK`, $P = 99.94\%$, Top Driver: `plant_duplicate_ratio_19` $\rightarrow$ **Consistent (`True`)**
- **Record #75660 (Motor Overload Attack):** Pred: `ATTACK`, $P = 99.66\%$, Top Driver: `percentage_change` $\rightarrow$ **Consistent (`True`)**
- **Record #88360 (Slow Drift Attack):** Pred: `ATTACK`, $P = 99.99\%$, Top Driver: `plant_duplicate_ratio_19` $\rightarrow$ **Consistent (`True`)**
- **Record #93364 (Nominal Normal):** Pred: `NORMAL`, $P = 0.01\%$, Top Normal Driver: `plant_duplicate_ratio_19` $\rightarrow$ **Consistent (`True`)**

Zero numerical or qualitative drift was detected.

---

## 15. AUDIT 13 — REGRESSION TESTING

**Status:** `PASS`

All automated test suites in the repository were executed:
1. `backend/ml/tests/test_human_explainer.py`: **13/13 tests pass**
2. `backend/ml/tests/test_attack_specific_shap.py`: **11/11 tests pass**
3. `backend/ml/tests/test_local_shap_explainer.py`: **11/11 tests pass**
4. `backend/ml/tests/test_ml_pipeline.py`: **8/8 tests pass**
   - **Total ML Test Suite:** **43/43 tests pass (100% OK)**
5. `backend/tests/` (Industrial telemetry & locality labeling): **26/26 tests pass (100% OK)**
6. `git diff --check`: **Clean (0 errors, 0 whitespace violations)**

---

## 16. AUDIT 14 — FILE & ARTIFACT INTEGRITY

**Status:** `PASS`

All 17 required Phase 6 source files, research reports, and publication figures were verified to exist in the repository:
- `backend/ml/explainability/shap_local_explainer.py`
- `backend/ml/explainability/attack_explainer.py`
- `backend/ml/explainability/human_explainer.py`
- `reports/phase6/PHASE_6_1_ARCHITECTURE_AUDIT.md`
- `reports/phase6/PHASE_6_2_SHAP_FOUNDATION_REPORT.md`
- `reports/phase6/PHASE_6_3_GLOBAL_SHAP_REPORT.md`
- `reports/phase6/PHASE_6_4_LOCAL_SHAP_REPORT.md`
- `reports/phase6/PHASE_6_5_ATTACK_SPECIFIC_SHAP_REPORT.md`
- `reports/phase6/PHASE_6_6_HUMAN_READABLE_EXPLANATIONS_REPORT.md`
- `reports/phase6/attack_specific/phase6_attack_specific_shap.csv`
- `reports/phase6/attack_specific/phase6_attack_specific_top10.csv`
- `reports/phase6/attack_specific/phase6_cross_attack_feature_frequency.csv`
- `reports/phase6/attack_specific/phase6_attack_specific_heatmap.png`
- `reports/phase6/attack_specific/phase6_attack_specific_rankings.png`
- `reports/phase6/attack_specific/phase6_attack_specific_representatives.json`
- `reports/phase6/human_readable/representative_human_explanations.json`
- `reports/phase6/human_readable/representative_human_explanations.md`

Missing required files: **0**.

---

## 17. AUDIT 15 — REPRODUCIBILITY ENVIRONMENT

**Status:** `PASS`

The explainability pipeline runs completely self-contained within the project virtual environment without external APIs or hidden state:
- **Operating System:** macOS Darwin (arm64)
- **Python Runtime:** `3.14.6`
- **Core ML & Explainability Dependencies:**
  - `shap`: `0.52.0`
  - `xgboost`: `3.3.0`
  - `scikit-learn`: `1.9.0`
  - `pandas`: `3.0.3`
  - `numpy`: `2.5.0`
  - `joblib`: `1.5.3`
  - `matplotlib`: `3.11.0`

---

## 18. AUDIT 16 — FROZEN-PHASE REGRESSION & PRESERVATION

**Status:** `PASS`

- **Phase 4.1 Benchmark Preservation:** The 99.65% test accuracy benchmark remains documented strictly as the **Stratified Multi-Attack Benchmark** in `reports/phase4_1/PHASE_4_1_OPTIMIZATION_REPORT.md`.
- **Phase 5 H3-32 Ablation Preservation:** The 4 ablated features (`value_change`, `abs_value_change`, `rolling_range_5`, `rolling_mean_10`) remain completely excluded from the 32 input features of `xgboost_h3_32.pkl`.
- **Zero Retraining:** The model was not touched, re-tuned, or re-calibrated.

---

## 19. SCIENTIFIC FINDINGS & LIMITATIONS

The audit documents the following domain limitations:
1. **Simulated Telemetry Environment:** The dataset is derived from an industrial IoT digital-twin simulation. In live production environments with asynchronous network packet jitter, the exact numerical rankings of inter-arrival timing features will fluctuate.
2. **Timing Cadence Reliance:** Features like `plant_duplicate_ratio_19` and `rolling_time_delta_5` dominate multiple attack types because the simulation publishes telemetry on fixed per-sensor cadences that cyber-attacks disrupt. This is genuine model reliance and is reported transparently.
3. **Small Sample Sizes for Specific Actuators:** `Sensor Spoofing` ($N=11$) and `Valve Stuck` ($N=19$) have limited sample support in the test split. Their rankings are empirical observations rather than definitive general distributions.
4. **Control-Plane Disconnect:** PLC attacks have zero sensor-level labels because they target control registers rather than sensor telemetry. Sensor-level ML models cannot detect pure control-plane attacks; dedicated PLC register monitoring is required.

---

## 20. FINAL VERDICT

```
================================================================================
FINAL VERDICT: A — PASS / READY FOR 6.8
================================================================================
```

### Comprehensive Justification:
1. **Model Immutability:** SHA-256 confirmed byte-for-byte unchanged throughout all phases.
2. **Zero Leakage:** Read-only inference strictly verified across all explainability classes.
3. **Mathematical Rigor:** TreeExplainer additive reconstruction verified ($MAE = 2.39 \times 10^{-6}$); 95 $\rightarrow$ 32 one-hot aggregation mismatch $< 2.05 \times 10^{-6}$.
4. **Domain Integrity:** Zero fabricated control-plane records; 14 active attacks honestly characterized.
5. **Human Safety:** Complete absence of causal overclaiming and unsafe control-room commands.
6. **Reproducibility:** 100% deterministic outputs; 69/69 project unit tests pass cleanly.

Phase 6.7 audit is officially complete. The system is ready to proceed to **Phase 6.8: Final Packaging & Integration Architecture**.
