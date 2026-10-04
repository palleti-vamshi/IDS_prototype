# LIGHTX-IDS — PHASE 6.2 SHAP FOUNDATION REPORT
## Official Model Persistence, SHAP TreeExplainer Verification, and Additive Fidelity

**Project:** LightX-IDS: Lightweight Explainable Real-Time Intrusion Detection System for Industrial IoT Networks  
**Repository:** `IDS_prototype`  
**Development Branch:** `antigravity-development`  
**Phase:** 6.2 — SHAP Foundation, Official H3-32 Model Persistence & Compatibility Verification  
**Authoritative Dataset:** `dataset/lightx_ids_dataset_100k.csv` (100,000 records × 13 raw columns)  
**Persisted Model Artifact:** `backend/ml/saved_models/xgboost_h3_32.pkl` (2.48 MB)  
**Test Suite Status:** 34 / 34 PASSED (100%)  
**Final Phase 6.2 Verdict:** **A — PASS / READY FOR 6.3**  

---

## 1. SHAP Installation

SHAP was cleanly installed into the project virtual environment (`./venv/bin/python`) via:
```bash
./venv/bin/pip install shap
```
Dependencies resolved and installed without conflicts:
- `shap` (0.52.0)
- `numba` (0.68.0)
- `llvmlite` (0.50.0)
- `cloudpickle` (3.1.2)
- `slicer` (0.0.8)
- `tqdm` (4.70.1)

Existing packages (`numpy`, `scipy`, `scikit-learn`, `pandas`, `xgboost`, `joblib`) remained intact with zero unexpected version upgrades.

---

## 2. Version Information

Verification executed directly inside `./venv/bin/python`:

| Component | Verified Version | Environment Details |
|---|:---:|---|
| **Python** | 3.14.6 | `main, Jun 10 2026, 10:03:53 [Clang 21.0.0 (clang-2100.0.123.102)]` |
| **SHAP** | 0.52.0 | Native ARM64 macOS wheel (`abi3`) |
| **XGBoost** | 3.3.0 | Hist gradient boosting, tree-method |
| **Scikit-Learn** | 1.9.0 | Preprocessing Pipeline & ColumnTransformer |
| **Pandas** | 3.0.3 | Series & DataFrame causal indexing |
| **NumPy** | 2.5.0 | Array matrix operations |
| **Joblib** | 1.5.3 | Model pipeline serialization |

---

## 3. H3-32 Reproduction

The authoritative 100,000-record dataset was processed in strict physical packet arrival order (`record_id` ascending).
- **Causal Feature Generation:** `FeatureGenerator.generate_causal_stream_features()` computed all backward-looking rolling features (`center=False`) along the stream.
- **H3-32 Feature Pruning:** The four sensitive short-term physical features frozen in Phase 5 were cleanly excluded:
  1. `value_change`
  2. `abs_value_change`
  3. `rolling_range_5`
  4. `rolling_mean_10`
- **Resulting Active Features:** Exactly **32 input features** (25 continuous/discrete numeric + 7 categorical).

---

## 4. Training Protocol

- **Dataset Split:** Authoritative stratified 80/10/10 split with frozen `random_state = 42`:
  - **Train:** 80,000 records
  - **Validation:** 9,999 records
  - **Test:** 10,001 records
- **Leakage Prevention:**
  - `FeatureGenerator.fit()` was executed strictly on the 80,000 training records to compute device baselines (`device_mean`, `device_std`, `dup_rate`).
  - Preprocessing transformers (`SimpleImputer`, `StandardScaler`, `OneHotEncoder`) were fit strictly on the 80,000 training records.
  - Zero validation or test data influenced feature parameters or tree split decisions.
- **Model Hyperparameters:** Frozen Phase 5 XGBoost architecture:
  - `n_estimators = 400`
  - `learning_rate = 0.05`
  - `max_depth = 10`
  - `min_child_weight = 2`
  - `subsample = 0.90`
  - `colsample_bytree = 0.90`
  - `reg_alpha = 0.10`
  - `reg_lambda = 3.0`
  - `objective = "binary:logistic"`
  - `tree_method = "hist"`
  - `random_state = 42`

---

## 5. Model Persistence

The trained Scikit-Learn `Pipeline` (comprising the fitted `ColumnTransformer` preprocessor and the fitted `XGBClassifier`) was persisted to:
```text
backend/ml/saved_models/xgboost_h3_32.pkl
```
- **Serialization Tool:** `joblib.dump()`
- **Artifact Size:** 2.48 MB
- **Untouched Baseline Verification:** The original Phase 4 baseline model (`backend/ml/saved_models/xgboost.pkl`, 2.40 MB, dated Oct 4 00:45) was preserved completely intact.

---

## 6. Reload Verification

The persisted model was immediately reloaded from disk (`joblib.load('backend/ml/saved_models/xgboost_h3_32.pkl')`):
- **Object Type:** `sklearn.pipeline.Pipeline`
- **Named Steps:** `['preprocessor', 'classifier']`
  - `preprocessor`: `sklearn.compose._column_transformer.ColumnTransformer`
  - `classifier`: `xgboost.sklearn.XGBClassifier`
- **Integrity Check:**
  - Loaded pipeline is fully functional and ready for inference.
  - Calling `pipeline.predict()` and `pipeline.predict_proba()` produces identical predictions to the in-memory trained estimator.

---

## 7. 32-Feature Verification

The input feature space of `xgboost_h3_32.pkl` was verified against the Phase 5 frozen contract:

### 25 Numeric Features:
`value`, `value_accel`, `time_delta`, `rolling_time_delta_5`, `rolling_time_delta_std_5`, `is_negative_time_delta`, `global_time_delta`, `rolling_global_td_10`, `rolling_global_td_std_10`, `packet_rate_10`, `is_duplicate_value`, `device_seq_gap`, `seq_gap_dev`, `rolling_seq_std_5`, `rolling_mean_3`, `rolling_std_3`, `rolling_mean_5`, `rolling_std_5`, `rolling_std_10`, `plant_duplicate_ratio_19`, `percentage_change`, `device_mean_deviation`, `z_score`, `rel_volatility`, `stability_anomaly`.

### 7 Categorical Features:
`topic`, `device_id`, `sensor_code`, `sensor_type`, `unit`, `status`, `source`.

- **Total Input Features:** $25 + 7 = \mathbf{32}$.
- **Verification:** All 4 removed features (`value_change`, `abs_value_change`, `rolling_range_5`, `rolling_mean_10`) are confirmed **completely absent**.

---

## 8. Transformed Feature Space Verification

When the 32 raw features pass through `preprocessor.transform()`, the feature space expands as follows:
- **Continuous Numeric Columns:** 25 columns (scaled via `StandardScaler`).
- **One-Hot Encoded Categorical Columns:** 70 binary dummy indicators:
  - `topic`: 11 distinct MQTT topics
  - `device_id`: 19 distinct machine sensor devices
  - `sensor_code`: 19 distinct sensor asset codes
  - `sensor_type`: 10 physical measurement domains
  - `unit`: 9 physical units
  - `status`: 1 operational status (`RUNNING`)
  - `source`: 1 industrial source (`simulator`)
- **Total Transformed Feature Columns:** $25 + 70 = \mathbf{95}$ features across the full 80,000-record training set.
  *(Note: A small sub-sample of 1,000 rows lacks 1 rare unit category and yields 94 columns; on the authoritative 80,000 training distribution, the space is exactly 95).*
- All transformed column names are preserved via `preprocessor.get_feature_names_out()` with clean human-readable names.

---

## 9. SHAP TreeExplainer Compatibility

Compatibility was verified using the two-stage pipeline extraction architecture:
```python
preprocessor = reloaded.named_steps["preprocessor"]
classifier = reloaded.named_steps["classifier"]

# Transform sample records
X_trans = preprocessor.transform(X_sample)
feature_names = preprocessor.get_feature_names_out()
X_df = pd.DataFrame(X_trans, columns=feature_names)

# Initialize TreeExplainer
explainer = shap.TreeExplainer(classifier)
shap_values = explainer(X_df)
```
- **Explainer Initialization:** Succeeded with zero errors or warnings.
- **Base Value (Expected Margin $\phi_0$):** `[-0.27542807]` (reflecting the background training log-odds of attack vs. normal).

---

## 10. SHAP Output Format and Shape

Tested on a 5-packet evaluation batch from the untouched test set:
- **Output Object Type:** `shap._explanation.Explanation`
- **SHAP Values Matrix Shape:** `(5, 95)`
  - Dimension 0: 5 evaluation records
  - Dimension 1: 95 transformed feature attributions
- **Feature Name Alignment:** `shap_values.feature_names` exactly aligns with `transformed_names`.

---

## 11. Additive Fidelity Verification

In log-odds margin space, Shapley values must satisfy the mathematical efficiency axiom:
$$\phi_0 + \sum_{j=1}^{95} \phi_j = f(x) = \text{model.predict}(X, \text{output\_margin}=\text{True})$$

Empirical verification across all 5 test samples:

| Sample Index | Model Raw Margin $f(x)$ | SHAP Reconstructed Margin $\phi_0 + \sum \phi_j$ | Absolute Difference $|f(x) - \hat{f}(x)|$ | Status |
|:---:|:---:|:---:|:---:|:---:|
| **Sample 0** | `-9.234085` | `-9.234089` | $3.81 \times 10^{-6}$ | **EXACT PASS** |
| **Sample 1** | `-1.155673` | `-1.155673` | $3.58 \times 10^{-7}$ | **EXACT PASS** |
| **Sample 2** | `-5.919176` | `-5.919181` | $4.77 \times 10^{-6}$ | **EXACT PASS** |
| **Sample 3** | `-8.982094` | `-8.982094` | $0.00 \times 10^{0}$  | **EXACT PASS** |
| **Sample 4** | `-9.255891` | `-9.255890` | $9.54 \times 10^{-7}$ | **EXACT PASS** |

**Conclusion:** Additive fidelity holds with maximum error $< 5 \times 10^{-6}$, which is well within standard single-precision floating-point roundoff tolerances.

---

## 12. Regression Test Results

Existing test suites were executed to ensure zero regressions:

1. **Machine Learning Suite (`backend/ml/tests/test_ml_pipeline.py`):**
   - `test_dataset_path_100k`: PASS
   - `test_dataset_splitter_proportions`: PASS
   - `test_dataset_temporal_splitter`: PASS
   - `test_feature_generator_fit_leakage_safety`: PASS
   - `test_feature_selector_no_label_leakage`: PASS
   - `test_model_factory_models_available`: PASS
   - `test_sensor_code_configuration`: PASS
   - `test_threshold_optimizer_validation_only`: PASS
   - **Result: 8 / 8 PASSED (100%)**

2. **Industrial Backend & Locality Suite (`backend/tests/`):**
   - Locality-Aware Labeling (21 tests): PASS
   - Factory Machine & Sensor Integration (5 tests): PASS
   - **Result: 26 / 26 PASSED (100%)**

**Total Test Suite: 34 / 34 PASSED (100%)**.

---

## 13. Git Safety and Repository Status

- `git status` reports working directory clean with respect to tracked files.
- `backend/ml/saved_models/xgboost_h3_32.pkl` is safely stored in the gitignored model directory.
- `backend/ml/saved_models/xgboost.pkl` was not overwritten or touched.
- `git diff --check` passed with 0 errors.

---

## 14. Documented Limitations

1. **Margin-Space vs. Probability-Space:**
   The exact additive property ($\phi_0 + \sum \phi_j = f(x)$) holds strictly in **log-odds margin space**. Converting to probability space requires the non-linear logistic sigmoid $\sigma(f(x))$. In Phase 6.3, both margin contributions and probability impacts will be clearly articulated in explanation formatters.
2. **Categorical Feature Granularity:**
   Because one-hot encoding expands the 7 categorical features into 70 binary indicators, individual dummy columns have small distinct SHAP attributions. In Phase 6.3, `explanation_formatter.py` will implement domain aggregation to sum mutually exclusive one-hot categories for high-level operator reporting.

---

## Final Phase 6.2 Verdict

### **A — PASS / READY FOR 6.3**

**Justification:**
- SHAP 0.52.0 is installed and fully functional.
- The authoritative Phase 5 H3-32 model pipeline is persisted to disk as `backend/ml/saved_models/xgboost_h3_32.pkl`.
- Feature configuration strictly contains 25 numeric + 7 categorical features (32 total).
- Reload and SHAP `TreeExplainer` initialization pass with 100% success.
- Mathematical additive fidelity is verified with $< 5 \times 10^{-6}$ error.
- All 34/34 existing unit tests pass without regressions.
- The project is fully prepared for Phase 6.3 (Global and Local Explainers, Visualizations, and Industrial Formatting).
