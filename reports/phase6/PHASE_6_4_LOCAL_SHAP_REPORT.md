# LIGHTX-IDS — PHASE 6.4 LOCAL SHAP EXPLANATIONS REPORT
## Single-Packet Attribution Engine, 32-Feature Aggregation, and Forensic Waterfall Verification

**Project:** LightX-IDS: Lightweight Explainable Real-Time Intrusion Detection System for Industrial IoT Networks  
**Repository:** `IDS_prototype`  
**Development Branch:** `antigravity-development`  
**Phase:** 6.4 — Local SHAP Explanations & Per-Packet Attribution  
**Authoritative Dataset:** `dataset/lightx_ids_dataset_100k.csv` (100,000 records × 13 raw columns)  
**Frozen Model Artifact:** `backend/ml/saved_models/xgboost_h3_32.pkl` (Frozen Phase 5 H3-32 Architecture)  
**Core Explainer Module:** `backend/ml/explainability/shap_local_explainer.py` (`LocalShapExplainer`)  
**New Unit Test Suite:** `backend/ml/tests/test_local_shap_explainer.py` (11/11 PASSED)  
**Total Test Suite Status:** **45 / 45 PASSED (100%)** (19 ML tests, 26 Industrial tests)  
**Demonstration Artifacts:** Generated under `reports/phase6/local/` (6 Waterfall plots, 1 structured JSON)  
**Final Phase 6.4 Verdict:** **A — PASS / READY FOR 6.5**  

---

## 1. Architecture

Phase 6.4 introduces the **Local Explanation Engine** for LightX-IDS. It provides real-time, packet-by-packet explainability, answering for security operators:
> *"Why did LightX-IDS classify this specific packet as an ATTACK or as NORMAL?"*

The system is encapsulated within [shap_local_explainer.py](file:///Users/vamshi_07/Documents/IDS_prototype/backend/ml/explainability/shap_local_explainer.py) (`LocalShapExplainer`). It integrates seamlessly with the existing machine learning pipeline without modifying any frozen components:

```text
Incoming Observation (Dict / Series / DataFrame Row with 32 H3-32 Features)
  │
  ├── 1. Feature Canonicalization & Validation:
  │      Ensures all 25 numeric and 7 categorical features are present.
  │
  ├── 2. Frozen Pipeline Preprocessing:
  │      Transforms 32 input features into 95-dimensional matrix via:
  │      pipeline.named_steps['preprocessor'].transform()
  │
  ├── 3. Model Inference:
  │      pipeline.named_steps['classifier'].predict(output_margin=True)
  │      Raw Margin f(x) ──► Sigmoid ──► Attack Probability P(Attack)
  │
  ├── 4. TreeExplainer Attribution Extraction:
  │      Decomposes f(x) into 95 Shapley values in log-odds margin space.
  │
  ├── 5. Additive Fidelity Verification:
  │      Asserts |f(x) - (base_value + Σ φ_j)| < 1e-4.
  │
  ├── 6. Domain-Level 32-Feature Aggregation:
  │      Sums one-hot categorical attributions back to parent features:
  │      topic, device_id, sensor_code, sensor_type, unit, status, source.
  │
  └── 7. Structured Diagnostic Output:
         - Top-k factors pushing toward ATTACK (+)
         - Top-k factors pushing toward NORMAL (−)
         - Waterfall visualization generation (Aggregated 32 & Transformed 95)
```

---

## 2. Local Explanation Methodology

1. **Input Flexibility:** Accepts a single packet telemetry observation as a Python `dict`, a pandas `Series`, or a single-row `DataFrame`.
2. **Pipeline Reusability:** Relies strictly on the fitted `preprocessor` from the frozen `xgboost_h3_32.pkl` model. No separate feature transformations, scalers, or encoders are created.
3. **Execution Speed:** Computes full local Shapley attribution and verification in **$< 4$ milliseconds** per packet on Apple Silicon, making it viable for on-demand alert triage and forensic inspection.

---

## 3. Feature Aggregation: 95-Transformed to 32-Original Space

The frozen pipeline expands 7 categorical features into 70 one-hot binary indicator columns, resulting in 95 total transformed columns ($25 \text{ numeric} + 70 \text{ one-hot}$). Exposing raw dummy columns like `device_id_cmp_001_pressure_sensor` or `sensor_code_MTR-001-TMP` as disjoint features fragments the explanation and confuses plant operators.

### Additive Categorical Formulation:
Because Shapley values are strictly additive across independent coordinates, the net contribution of categorical feature $C \in \{\text{topic}, \text{device\_id}, \text{sensor\_code}, \text{sensor\_type}, \text{unit}, \text{status}, \text{source}\}$ for packet $i$ is mathematically exact:
$$\phi_{i, C} = \sum_{j \in \text{onehot}(C)} \phi_{i, j}$$

Each of the 25 numeric features retains its exact single-column attribution:
$$\phi_{i, F} = \phi_{i, j_F}$$

This yields an exact, complete attribution vector of **32 original physical features** that preserves exact additivity:
$$\phi_0 + \sum_{k=1}^{32} \phi_{i, k} = \phi_0 + \sum_{j=1}^{95} \phi_{i, j} = f(x_i)$$

---

## 4. Prediction and Probability Handling

- **Raw Margin $f(x)$:** The unconstrained model log-odds output $f(x) \in (-\infty, +\infty)$ produced by `classifier.predict(X, output_margin=True)`.
- **Attack Probability $P(\text{Attack})$:** Calculated via the standard logistic sigmoid:
  $$P(\text{Attack}) = \sigma(f(x)) = \frac{1}{1 + e^{-f(x)}}$$
- **Normal Probability $P(\text{Normal})$:**
  $$P(\text{Normal}) = 1.0 - P(\text{Attack})$$
- **Binary Decision Rule:**
  $$\text{Prediction} = \begin{cases} \text{ATTACK}, & \text{if } P(\text{Attack}) \ge \tau^* \\ \text{NORMAL}, & \text{if } P(\text{Attack}) < \tau^* \end{cases}$$
  where $\tau^*$ is the frozen optimal operating threshold (default $0.35$).

---

## 5. SHAP Direction and Scientific Semantics

In binary classification with target `label = 1` (Attack):

- **Positive SHAP Value ($\phi_j > 0$):**
  - **Direction:** Pushes the model prediction **TOWARD ATTACK**.
  - **Operator Meaning:** The feature exhibited abnormal, elevated, or attack-associated characteristics for this packet.
- **Negative SHAP Value ($\phi_j < 0$):**
  - **Direction:** Pushes the model prediction **TOWARD NORMAL**.
  - **Operator Meaning:** The feature exhibited nominal, steady-state, or non-malicious characteristics, mitigating attack suspicion.

> [!IMPORTANT]
> **Scientific Non-Causal Semantics:**
> SHAP measures **model attribution**, not physical root cause. Explanations must always state:
> *"Feature $X$ contributed $+2.45$ toward the attack classification,"*
> rather than:
> *"Feature $X$ caused the attack."*

---

## 6. Additive Fidelity Verification

Every call to `explain_instance()` performs an automated internal sanity check:
$$\text{Fidelity Error} = \left| f(x) - \left( \phi_0 + \sum_{j=1}^{95} \phi_j \right) \right|$$

If the error exceeds $10^{-4}$, an exception is raised immediately. Across all test runs, the maximum observed error is **$< 5 \times 10^{-6}$**, confirming exact fidelity.

---

## 7. Representative Examples

Demonstrations were generated using test packets from the frozen evaluation split and archived in [representative_local_explanations.json](file:///Users/vamshi_07/Documents/IDS_prototype/reports/phase6/local/representative_local_explanations.json):

### Example 1: Normal Telemetry Packet (Record #93364)
- **Ground Truth:** Normal Telemetry
- **Model Prediction:** **NORMAL**
- **Probabilities:** $P(\text{Attack}) = \mathbf{0.01\%}$, $P(\text{Normal}) = \mathbf{99.99\%}$
- **Raw Margin:** $-9.2341$ (Base Value: $-0.2719$)
- **Fidelity Error:** $4.05 \times 10^{-6}$
- **Top Factors Pushing toward NORMAL (−):**
  1. `plant_duplicate_ratio_19`: **$-4.1898$** (Raw value: $0.842$, indicating diverse active plant readings)
  2. `rolling_time_delta_5`: **$-3.1309$** (Raw value: $0.325\,\text{s}$, consistent with unhurried normal polling)
  3. `rolling_time_delta_std_5`: **$-0.7790$** (Raw value: $0.025\,\text{s}$, stable mechanical jitter)
  4. `rolling_global_td_std_10`: **$-0.1607$**
  5. `topic`: **$-0.1540$** (Authorized topic: `factory/line1/temperature`)
- **Top Factors Pushing toward ATTACK (+):**
  1. `rolling_global_td_10`: $+0.0974$ (Minor background fluctuation)
  2. `z_score`: $+0.0969$

### Example 2: Network-Level Attack (Record #3203 — DoS Attack)
- **Ground Truth:** DoS Attack
- **Model Prediction:** **ATTACK**
- **Probabilities:** $P(\text{Attack}) = \mathbf{99.36\%}$, $P(\text{Normal}) = \mathbf{0.64\%}$
- **Raw Margin:** $+5.0460$ (Base Value: $-0.2719$)
- **Fidelity Error:** $4.05 \times 10^{-6}$
- **Top Factors Pushing toward ATTACK (+):**
  1. `plant_duplicate_ratio_19`: **$+3.3264$** (Raw value: $0.316$, severe multi-sensor duplicate collapse)
  2. `rolling_time_delta_5`: **$+0.8334$** (Raw value: $0.063\,\text{s}$, collapsed inter-arrival pacing)
  3. `rolling_time_delta_std_5`: **$+0.7326$** (Raw value: $0.0025\,\text{s}$, machine-like lack of jitter)
  4. `time_delta`: **$+0.6391$** (Rapid consecutive packet)
  5. `rolling_global_td_10`: **$+0.2765$**
- **Top Factors Pushing toward NORMAL (−):**
  1. `topic`: $-0.1110$ (Legitimate topic string exploited during flood)
  2. `device_mean_deviation`: $-0.1001$ (Physical sensor values remained near nominal)

### Example 3: Kinetic Physical Attack (Record #75660 — Motor Overload Attack)
- **Ground Truth:** Motor Overload Attack
- **Model Prediction:** **ATTACK**
- **Probabilities:** $P(\text{Attack}) = \mathbf{99.66\%}$, $P(\text{Normal}) = \mathbf{0.34\%}$
- **Raw Margin:** $+5.6721$ (Base Value: $-0.2719$)
- **Fidelity Error:** $3.10 \times 10^{-6}$
- **Top Factors Pushing toward ATTACK (+):**
  1. `percentage_change`: **$+1.7844$** (Sudden kinetic physical surge in motor current/vibration)
  2. `plant_duplicate_ratio_19`: **$+1.1052$**
  3. `rel_volatility`: **$+0.6408$** (Abnormal rise in short-term physical volatility)
  4. `packet_rate_10`: **$+0.4972$**
  5. `rolling_std_10`: **$+0.4485$** (High physical dispersion)
- **Top Factors Pushing toward NORMAL (−):**
  1. `rolling_time_delta_5`: **$-1.1036$** (Raw value: $0.258\,\text{s}$ — network timing was completely normal!)
  2. `time_delta`: **$-0.2385$**
  3. `topic`: **$-0.0422$**

*Key Research Insight:* For the Motor Overload attack, the communication timing features (`rolling_time_delta_5`) actually pushed **toward Normal**, while the kinetic derivative features (`percentage_change`, `rel_volatility`, `rolling_std_10`) decisively pushed **toward Attack**. This confirms that the model accurately diagnoses physical process tampering independently of communication anomalies.

---

## 8. Waterfall Plots

Representative waterfall plots generated and saved under `reports/phase6/local/`:

| Record ID | Ground Truth Class | Prediction | Aggregated 32-Feature Waterfall | Transformed 95-Feature Waterfall |
|:---:|:---:|:---:|:---:|:---:|
| **93364** | Normal | **NORMAL** ($P=0.01\%$) | [local_shap_record_93364.png](file:///Users/vamshi_07/Documents/IDS_prototype/reports/phase6/local/local_shap_record_93364.png) | [local_shap_record_93364_transformed95.png](file:///Users/vamshi_07/Documents/IDS_prototype/reports/phase6/local/local_shap_record_93364_transformed95.png) |
| **3203** | DoS Attack | **ATTACK** ($P=99.36\%$) | [local_shap_record_3203.png](file:///Users/vamshi_07/Documents/IDS_prototype/reports/phase6/local/local_shap_record_3203.png) | [local_shap_record_3203_transformed95.png](file:///Users/vamshi_07/Documents/IDS_prototype/reports/phase6/local/local_shap_record_3203_transformed95.png) |
| **75660** | Motor Overload | **ATTACK** ($P=99.66\%$) | [local_shap_record_75660.png](file:///Users/vamshi_07/Documents/IDS_prototype/reports/phase6/local/local_shap_record_75660.png) | [local_shap_record_75660_transformed95.png](file:///Users/vamshi_07/Documents/IDS_prototype/reports/phase6/local/local_shap_record_75660_transformed95.png) |

---

## 9. Test Suite Verification

Comprehensive test suites executed from a clean working environment:

```bash
PYTHONPATH=. ./venv/bin/python -m unittest discover -s backend/ml/tests -p "test_*.py" -v
PYTHONPATH=. ./venv/bin/python -m unittest discover -s backend/tests -p "test_*.py" -v
```

### Detailed Test Results:
1. **Local SHAP Explainer Tests (`backend/ml/tests/test_local_shap_explainer.py`):**
   - `test_01_model_loads_successfully`: **PASS**
   - `test_02_single_observation_input_formats`: **PASS** (Series, dict, DataFrame)
   - `test_03_prediction_validity`: **PASS**
   - `test_04_probability_bounds_and_sum`: **PASS** ($P \in [0, 1]$, sum = 1.0)
   - `test_05_shap_values_dimensionality`: **PASS** (95 transformed, 32 aggregated)
   - `test_06_top_k_output`: **PASS** (Correctly limits to top_k)
   - `test_07_positive_negative_directions`: **PASS** (Positive > 0, Negative < 0)
   - `test_08_original_feature_mapping`: **PASS** (All 32 original features accounted for)
   - `test_09_one_hot_categorical_aggregation`: **PASS** (One-hot sum == aggregated value)
   - `test_10_additive_fidelity`: **PASS** (Error < 1e-4)
   - `test_11_waterfall_plot_generation`: **PASS** (Valid non-empty image files)
   - **Local Explainer Suite:** **11 / 11 PASSED (100%)**

2. **Core ML Pipeline Tests (`backend/ml/tests/test_ml_pipeline.py`):**
   - 8 / 8 PASSED (100%)
   - **ML Subtotal:** **19 / 19 PASSED (100%)**

3. **Industrial Backend & Locality Tests (`backend/tests/`):**
   - 26 / 26 PASSED (100%)

**Total Project Tests:** **45 / 45 PASSED (100%)**.

---

## 10. Documented Limitations

1. **Local vs. Campaign Context:**
   Local explanations operate on individual packet telemetry. For multi-packet attacks (like Slow Drift or Intermittent bursts), looking at a single packet explains why *that specific packet* was flagged, but does not summarize the overarching campaign trajectory.
2. **Margin Space Interpretation:**
   SHAP values are linear in log-odds margin space. A SHAP value of $+1.5$ does not mean an increase of $1.5\%$ in probability; rather, it shifts the log-odds margin $f(x)$ upwards by $+1.5$, which has a non-linear effect on the sigmoid probability curve depending on the current operating point.
3. **Independent Features Assumption:**
   While TreeSHAP handles tree path conditionality, mutual dependencies among rolling features (`rolling_mean_3` and `rolling_mean_5`) can distribute attribution across correlated features.

---

## Final Phase 6.4 Verdict

### **A — PASS / READY FOR 6.5**

**Justification:**
- Successfully created a modular, production-ready local explanation engine in `backend/ml/explainability/shap_local_explainer.py`.
- Exact 32-feature aggregated attribution mapping implemented and verified.
- Additive fidelity holds with maximum error $< 5 \times 10^{-6}$.
- Publication-quality waterfall plots and structured JSON outputs generated.
- All 45/45 regression tests pass (100% pass rate).
- Zero modifications to Phase 1–5 source code; git status clean.
- Ready to proceed to Phase 6.5 (Attack-Specific Explanations & Threat Signatures) upon authorization.
