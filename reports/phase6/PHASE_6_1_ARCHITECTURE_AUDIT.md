# LIGHTX-IDS — PHASE 6.1 ARCHITECTURE AND COMPATIBILITY AUDIT
## Explainable AI (XAI) Integration Assessment for Industrial IoT Intrusion Detection

**Project:** LightX-IDS: Lightweight Explainable Real-Time Intrusion Detection System for Industrial IoT Networks  
**Repository:** `IDS_prototype`  
**Current Development Branch:** `antigravity-development`  
**Phase:** 6.1 — Architecture, Compatibility, and Explainer Design Audit  
**Authoritative Dataset:** `dataset/lightx_ids_dataset_100k.csv` (100,000 records × 13 raw columns)  
**Frozen Model Baseline:** Phase 5 Feature Configuration **H3-32** (25 Numeric, 7 Categorical)  
**Status:** COMPLETE AUDIT — NO IMPLEMENTATION CODE WRITTEN  
**Final Audit Verdict:** **B — READY WITH MINOR PREPARATION**  

---

## 1. Current Machine Learning Architecture

The LightX-IDS machine learning framework is structured into modular layers designed for causal real-time edge processing:

```text
dataset/lightx_ids_dataset_100k.csv (Packet arrival order)
  │
  ├── 1. Ingestion & Validation: DatasetLoader (backend/ml/preprocessing/loader.py)
  ├── 2. Causal Feature Engineering: FeatureGenerator (backend/ml/feature_engineering/feature_generator.py)
  │      └── Computes stream-level rolling features backwards in time (center=False)
  │      └── Fits device steady-state baselines strictly on training set (zero leakage)
  ├── 3. Feature Selection: FeatureSelector (backend/ml/feature_engineering/feature_selector.py)
  │      └── Drops record_id, timestamp, sequence_number, attack_type, and target labels
  ├── 4. Preprocessing & Encoding: DatasetTransformer (backend/ml/preprocessing/transformer.py)
  │      └── ColumnTransformer:
  │          - Numeric Pipeline: SimpleImputer(strategy='median') + StandardScaler()
  │          - Categorical Pipeline: SimpleImputer(strategy='most_frequent') + OneHotEncoder(sparse_output=False)
  ├── 5. Estimator Pipeline: MLPipeline (backend/ml/preprocessing/pipeline.py)
  │      └── sklearn.pipeline.Pipeline(steps=[('preprocessor', transformer), ('classifier', model)])
  ├── 6. Training & Evaluation: ModelTrainer & EvaluationManager (backend/ml/training/trainer.py, backend/ml/evaluation/)
  └── 7. Persistence: ModelManager (backend/ml/training/model_manager.py)
         └── Serializes pipeline to backend/ml/saved_models/<model_name>.pkl
```

---

## 2. Frozen Phase 5 Pipeline

Phase 5 investigated and audited false positive reduction on the LightX-IDS pipeline. The audit ([PHASE_5_AUDIT_REPORT.md](file:///Users/vamshi_07/Documents/IDS_prototype/reports/phase5/PHASE_5_AUDIT_REPORT.md)) formally declared:
- **Status:** **PASS WITH DOCUMENTED LIMITATIONS (Category B)**.
- **Authoritative Configuration:** **H3-32**.
- **Ablation Decision:** The baseline 36-feature pipeline contained 4 short-term differential physical features that caused false alarms during post-attack recovery transients:
  1. `value_change` ($v_t - v_{t-1}$)
  2. `abs_value_change` ($|v_t - v_{t-1}|$)
  3. `rolling_range_5` ($\max(v_{t-4..t}) - \min(v_{t-4..t})$)
  4. `rolling_mean_10` ($\frac{1}{10}\sum_{k=0}^9 v_{t-k}$)
- Removing these 4 features yields the frozen 32-feature set (25 numeric + 7 categorical).
- Under 10 random seeds (42–51), H3-32 maintained 99.47% stratified F1, reduced controlled temporal false positives by 11.58% on average, and improved strict chronological attack recall by **+7.81 percentage points** across 10/10 seeds.

---

## 3. Exact Final 32-Feature Path

The 32 features that enter the Phase 5 H3-32 estimator are derived as follows:

### A. 25 Numeric Features
1. `value` (Sensor reading payload)
2. `value_accel` (Second derivative of value change)
3. `time_delta` (Inter-arrival time from preceding packet on same device)
4. `rolling_time_delta_5` (Backward 5-packet rolling mean inter-arrival time)
5. `rolling_time_delta_std_5` (Backward 5-packet rolling std of inter-arrival time)
6. `is_negative_time_delta` (Binary flag for out-of-order packet timing)
7. `global_time_delta` (Global inter-arrival time across entire factory bus)
8. `rolling_global_td_10` (Backward 10-packet rolling mean global inter-arrival time)
9. `rolling_global_td_std_10` (Backward 10-packet rolling std of global inter-arrival time)
10. `packet_rate_10` (Inverse rolling global inter-arrival time: $10 / \sum \Delta t$)
11. `is_duplicate_value` (Binary flag indicating identical consecutive reading)
12. `device_seq_gap` (Discrepancy in device sequence number increment: $\Delta seq - 1$)
13. `seq_gap_dev` (Absolute deviation from expected unit sequence gap)
14. `rolling_seq_std_5` (Backward 5-packet rolling standard deviation of sequence gap)
15. `rolling_mean_3` (Backward 3-packet moving average of sensor reading)
16. `rolling_std_3` (Backward 3-packet standard deviation of sensor reading)
17. `rolling_mean_5` (Backward 5-packet moving average of sensor reading)
18. `rolling_std_5` (Backward 5-packet standard deviation of sensor reading)
19. `rolling_std_10` (Backward 10-packet standard deviation of sensor reading)
20. `plant_duplicate_ratio_19` (Proportion of 19 sensors currently repeating values)
21. `percentage_change` (Relative percentage change: $\Delta v / (v_{t-1} + \epsilon)$)
22. `device_mean_deviation` (Deviation from training-set device mean: $v_t - \mu_{train}$)
23. `z_score` (Standardized z-score relative to training-set device: $(v_t - \mu_{train}) / \sigma_{train}$)
24. `rel_volatility` (Ratio of short-term volatility to training baseline: $rolling\_std\_5 / \sigma_{train}$)
25. `stability_anomaly` (Product of duplicate flag and training-set non-duplicate rate)

### B. 7 Categorical Features
1. `topic` (MQTT publication topic, e.g., `factory/line1/temperature`)
2. `device_id` (Machine sensor device ID, e.g., `mtr_001_temperature_sensor`)
3. `sensor_code` (Standardized asset tag, e.g., `MTR-001-TMP`)
4. `sensor_type` (Physical measurement domain: temperature, pressure, vibration, current, etc.)
5. `unit` (Engineering unit: C, PSI, mm/s, A, V, RPM, %, etc.)
6. `status` (Operational status flag: NORMAL, WARNING, CRITICAL)
7. `source` (Industrial data source: SIMULATED)

---

## 4. Model Storage and Training Path

### Current Repository State:
- Models are persisted in: `backend/ml/saved_models/`
- Serialization format: `joblib` (`.pkl`) alongside descriptive JSON metadata (`.json`).
- Current persisted models:
  - `backend/ml/saved_models/xgboost.pkl` (2.5 MB)
  - `backend/ml/saved_models/random_forest.pkl` (51.2 MB)
  - `backend/ml/saved_models/decision_tree.pkl` (37 KB)
  - `backend/ml/saved_models/logistic_regression.pkl` (10 KB)

### Important Finding:
The existing `backend/ml/saved_models/xgboost.pkl` is the **Phase 4 baseline model** (trained on all 29 numeric features + 7 categorical features = 36 input features / 99 transformed columns).

In Phase 5, Praveen ran all feature ablation experiments in read-only diagnostic scripts (`backend/ml/experiments/phase5_stage8_h3_final_robustness.py`), explicitly avoiding modifying the production model on disk:
`READ-ONLY: no dataset, labels, config.py, or production model changes.`

### Requirement for Phase 6:
Because the Phase 5 decision was to **freeze H3-32**, Phase 6 needs the trained H3-32 model.
The model can either be:
1. Formally persisted via `ModelManager().save(...)` as `xgboost_h3_32.pkl` (or updated `xgboost.pkl`).
2. Instantiated and fit on-the-fly using the frozen 80,000 training set and Seed 42 within a dedicated loader.
Persisting it cleanly as `xgboost_h3_32.pkl` or `xgboost.pkl` is the superior production approach.

---

## 5. Preprocessing Path

The preprocessing pipeline is constructed by `DatasetTransformer`:
```python
preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), numeric_features),
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), categorical_features),
    ],
    remainder="drop",
    verbose_feature_names_out=False
)
```

### Preprocessing Matrix Properties:
- Input: `pandas.DataFrame` of 32 columns.
- Output: Dense 2D `numpy.ndarray` (or DataFrame) of **94 to 95 columns** (25 standardized continuous numeric columns + 69 or 70 binary one-hot indicator columns for topics, devices, sensors, units, statuses).
- Because `sparse_output=False`, the matrix is a standard dense float64/float32 array, which is directly consumable by XGBoost and SHAP.

---

## 6. SHAP Compatibility Assessment

### A. Can SHAP directly explain the `sklearn.pipeline.Pipeline`?
**NO.**
`shap.TreeExplainer` requires access to the underlying tree ensemble structure (`xgb.core.Booster` or `XGBClassifier`). It cannot parse `ColumnTransformer`, `StandardScaler`, or `OneHotEncoder`. Passing the outer `Pipeline` directly to `shap.TreeExplainer` raises:
`Exception: <class 'sklearn.pipeline.Pipeline'> is not currently supported by TreeExplainer!`

### B. Can `shap.Explainer` or `shap.KernelExplainer` explain the `Pipeline` as a black box?
While `KernelExplainer(pipeline.predict_proba, background_data)` can technically treat any function as a black box, it is **unsuitable** for LightX-IDS:
- Exponential/polynomial complexity with respect to feature count ($M \approx 95$).
- Explaining a single packet takes several seconds; explaining a test set of 10,000 packets would take tens of hours.
- TreeExplainer evaluates exact Shapley values in polynomial time ($O(TLD^2)$, where $T$ is trees, $L$ is leaves, $D$ is depth), computing explanations for thousands of packets in fractions of a second.

### C. The Optimal Architectural Solution: Two-Stage Explainer
The proper, robust architectural pattern for LightX-IDS is:
1. Extract the fitted preprocessor and the fitted classifier:
   ```python
   preprocessor = pipeline.named_steps["preprocessor"]
   classifier = pipeline.named_steps["classifier"]
   ```
2. Transform input features using the preprocessor:
   ```python
   X_transformed = preprocessor.transform(X_raw_32)
   feature_names = preprocessor.get_feature_names_out()
   X_df = pd.DataFrame(X_transformed, columns=feature_names)
   ```
3. Pass `classifier` and `X_df` into `shap.TreeExplainer`:
   ```python
   explainer = shap.TreeExplainer(classifier)
   shap_values = explainer(X_df)
   ```
This provides exact Shapley values at C++ execution speed with perfect feature name binding.

---

## 7. Dependency Status

Audited on the active Python runtime (`./venv/bin/python`):

| Package | Installed Version | Required for SHAP | Status | Notes |
|---|:---:|:---:|:---:|---|
| **Python** | 3.14.6 | >= 3.9 | **OK** | Apple Silicon ARM64 (darwin) |
| **XGBoost** | 3.3.0 | Compatible | **OK** | Native TreeExplainer support |
| **Scikit-Learn** | 1.9.0 | Compatible | **OK** | Preprocessing pipeline |
| **Pandas** | 3.0.3 | Compatible | **OK** | DataFrame manipulation |
| **NumPy** | 2.5.0 | Compatible | **OK** | Array operations |
| **Joblib** | 1.5.3 | Compatible | **OK** | Pipeline deserialization |
| **SHAP** | **NOT INSTALLED** | `>= 0.44.0` | **ACTION REQUIRED** | Package must be installed |

### Package Installation Feasibility:
A pip dry-run (`./venv/bin/pip install --dry-run shap`) confirmed that `shap-0.52.0-cp312-abi3-macosx_11_0_arm64.whl` and its dependencies (`numba`, `llvmlite`, `slicer`, `tqdm`, `cloudpickle`) are available as pre-compiled binary wheels for the local system architecture.

---

## 8. Feature-Name Mapping Strategy

To prevent raw anonymous designations like `x0`, `x1`, `x2`, the explainer must implement a deterministic feature naming contract.

### Two Levels of Explanation Resolution:

#### Level 1: Transformed Feature Resolution (Exact SHAP)
Because `DatasetTransformer` specifies `verbose_feature_names_out=False`, `preprocessor.get_feature_names_out()` generates clean, human-readable column tags:
- Numeric features retain exact names: `packet_rate_10`, `time_delta`, `device_seq_gap`, `z_score`.
- One-hot categorical features retain exact token prefixes: `sensor_code_MTR-001-TMP`, `topic_factory/line1/pressure`, `device_id_pmp_001_vibration_sensor`.

#### Level 2: Industrial Domain Aggregation (Operator-Level Grouping)
In an industrial SCADA dashboard or security operations center (SOC), an operator does not want to inspect 19 distinct one-hot dummy variables for sensor codes. They want to know:
- "How much did the **device identity** contribute?"
- "How much did **packet timing** contribute?"
- "How much did **physical sensor magnitude** contribute?"

The explanation engine can aggregate one-hot categorical SHAP values back to their parent high-level semantic feature by summing Shapley values over columns belonging to the same category:
$$\phi_{\text{sensor\_code}} = \sum_{c \in \text{onehot}(\text{sensor\_code})} \phi_c$$
Because Shapley values are strictly additive, the sum of Shapley values for mutually exclusive one-hot categories is mathematically equal to the joint contribution of that categorical feature.

---

## 9. Global Explanation Strategy

Global explainability reveals overall model logic across the entire industrial network:

1. **Evaluation Set:** Compute SHAP values over the untouched 10,000-record test set (or a stratified background sample of 1,000–2,000 records for fast reporting).
2. **Mean Absolute SHAP ($I_j$):**
   $$I_j = \frac{1}{N} \sum_{i=1}^N |\phi_{i, j}|$$
3. **Artifacts to Generate:**
   - `global_feature_importance.csv`: Ranked table of features by mean $|\text{SHAP}|$.
   - `summary_beeswarm_plot.png`: Distribution of feature impact showing directionality (high vs. low values driving attack probability).
   - `global_bar_plot.png`: Standard bar chart of top 20 most influential features.
4. **Physical Verification:** Confirm whether global feature rankings align with physical reality:
   - Communication/timing attacks (DoS, Replay, Delay) should be dominated by `packet_rate_10`, `time_delta`, and `device_seq_gap`.
   - Kinetic/process attacks (Motor Overload, False Data Injection, Sensor Freeze) should be dominated by `z_score`, `stability_anomaly`, and `value`.

---

## 10. Local Explanation Strategy

Local explainability explains a single industrial telemetry packet at index $k$:

1. **Input:** A single telemetry record (raw dictionary or pandas Series).
2. **Preprocessing:** Transform the single record through `preprocessor.transform([record])`.
3. **Inference:**
   - Output probability: $P(\text{Attack}) = \sigma(f(x))$.
   - Binary decision: $y_{pred} = \mathbb{I}(P \ge \tau^*)$.
4. **SHAP Decomposition:**
   - Base value (expected margin over training distribution): $\phi_0$.
   - Feature contributions: $[\phi_1, \phi_2, \dots, \phi_M]$.
5. **Top Contributor Ranking:**
   - Top positive contributors (features pushing toward **ATTACK**).
   - Top negative contributors (features pushing toward **NORMAL**).
6. **Local Artifacts:**
   - Waterfall plot (`waterfall_plot.png`).
   - Structured JSON response for SCADA API integration.

---

## 11. SHAP Output Interpretation: Margin Space vs. Probability Space

It is critical not to conflate raw margins with probabilities in research publications.

### A. Raw Margin Space (Log-Odds Space)
In XGBoost binary logistic regression (`objective="binary:logistic"`):
- The model outputs a raw margin: $f(x) \in (-\infty, +\infty)$.
- Default `TreeExplainer(model).shap_values(X)` calculates Shapley values in **raw margin units**.
- **Exact Additivity:**
  $$\phi_0 + \sum_{j=1}^M \phi_j = f(x)$$
  where $\phi_0$ is `explainer.expected_value` (the average log-odds margin of the background dataset).

### B. Probability Space
- The output probability is the logistic sigmoid of the margin:
  $$P(\text{Attack}) = \frac{1}{1 + e^{-f(x)}} = \frac{1}{1 + e^{-(\phi_0 + \sum_{j=1}^M \phi_j)}}$$
- **Non-Linearity Note:** Because the sigmoid transformation is strictly non-linear, Shapley values calculated in probability space do not sum linearly to the final probability without non-linear interaction terms or interventional background sampling.
- **Protocol Decision:**
  - Compute exact SHAP values in the **log-odds margin space** to guarantee exact mathematical additivity.
  - Present both the margin contribution and the final converted probability $P(\text{Attack})$ to operators, explicitly documenting the conversion.

---

## 12. Leakage and Causality Considerations

1. **Zero Leakage:**
   - The SHAP explainer must be initialized using the **frozen, pre-trained model**.
   - If a background summary distribution is used (e.g., `shap.kmeans` or `shap.sample`), it must be drawn **exclusively from the 80,000 training records**.
   - Never sample background references from the validation or test sets.
2. **Causal Stream Integrity:**
   - Explanations for packet $t$ are derived solely from features available at or before packet $t$.
   - SHAP computes attributions on causal features; it does not introduce any backward or forward dependencies.

---

## 13. Proposed Phase 6 Directory Structure

To maintain pristine separation from completed phases, Phase 6 code should reside inside a dedicated package:

```text
backend/ml/explainability/
├── __init__.py                      # Package exports (LightXExplainer, etc.)
├── shap_explainer.py                # Core wrapper around TreeExplainer and Pipeline
├── global_explanation.py            # Global summary, mean |SHAP|, bar/beeswarm generation
├── local_explanation.py             # Single-packet explanation, top positive/negative drivers
├── explanation_formatter.py         # Translates raw SHAP math into industrial security reasoning
└── attack_explainer.py              # Attack-specific signature profiles (DoS, Replay, Drift)

backend/ml/tests/
└── test_explainability.py           # Unit tests verifying fidelity, additivity, and feature mapping

reports/phase6/
├── PHASE_6_1_ARCHITECTURE_AUDIT.md  # This authoritative audit report
└── PHASE_6_EXPLAINABILITY_REPORT.md # Final experimental results and plots
```

---

## 14. Risks and Limitations

1. **Dependency Risk (`shap` installation):**
   - The virtual environment currently lacks `shap`. While pip dry-run confirms that binary wheels exist for ARM64 macOS, actual installation requires running `pip install shap`.
2. **Model Persistence Gap:**
   - `backend/ml/saved_models/xgboost.pkl` is currently the Phase 4 36-feature baseline. To explain Phase 5 H3-32, the official H3-32 model must be formally saved to disk as an authoritative artifact.
3. **One-Hot Sparsity:**
   - Categorical one-hot features generate ~70 binary columns. Individual dummy columns may have small individual SHAP values. Without semantic grouping in `explanation_formatter.py`, explanations may appear fragmented to industrial operators.

---

## 15. Exact Implementation Plan for Phase 6.2

When authorized to begin Phase 6.2 implementation, follow this exact sequence:

1. **Step 1 — Environment Preparation:**
   - Install `shap` in the virtual environment via `./venv/bin/pip install shap`.
   - Verify import and versions without disturbing existing dependencies.
2. **Step 2 — Persist Official Phase 5 H3-32 Model:**
   - Train the H3-32 XGBoost pipeline on the frozen 80,000 training set (Seed 42) and save it via `ModelManager` as `backend/ml/saved_models/xgboost_h3_32.pkl`.
3. **Step 3 — Build Core Explainer Module (`backend/ml/explainability/`):**
   - Implement `shap_explainer.py` to extract `preprocessor` and `classifier`, transform data, bind feature names from `get_feature_names_out()`, and initialize `TreeExplainer`.
   - Implement additivity check: $\left| (\phi_0 + \sum \phi_j) - f(x) \right| < 10^{-4}$.
4. **Step 4 — Implement Global Explainer (`global_explanation.py`):**
   - Compute mean absolute SHAP values across test samples.
   - Output `global_feature_importance.csv` and summary plots.
5. **Step 5 — Implement Local Explainer & Industrial Formatter:**
   - Build per-packet local explanation methods returning top-k positive and negative contributing features.
   - Map technical features into human-readable industrial language (e.g. `packet_rate_10` $\rightarrow$ "High MQTT message ingestion rate").
6. **Step 6 — Implement Test Suite (`test_explainability.py`):**
   - Write automated unit tests verifying:
     - Mathematical additivity
     - Correct feature name preservation (no `x0`, `x1`)
     - Leakage prevention (explainer uses frozen model)
7. **Step 7 — Verification & Documentation:**
   - Run regression suites to ensure 100% pass rate.
   - Produce final `reports/phase6/PHASE_6_EXPLAINABILITY_REPORT.md`.

---

## Final Verdict

### **B — READY WITH MINOR PREPARATION**

**Justification:**
- The pipeline architecture (`ColumnTransformer` + `XGBClassifier`) is mathematically and functionally well-suited for exact `TreeExplainer` integration.
- Feature names are cleanly retrievable via `preprocessor.get_feature_names_out()`.
- The two minor prerequisites before coding are:
  1. Installing the `shap` package in `./venv/bin/python`.
  2. Persisting the official Phase 5 H3-32 model pipeline to `backend/ml/saved_models/`.
- No architectural redesign, pipeline rewrite, or retraining of previous phases is needed.
