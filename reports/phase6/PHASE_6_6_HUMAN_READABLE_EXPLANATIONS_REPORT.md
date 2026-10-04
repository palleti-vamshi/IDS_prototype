# LIGHTX-IDS PHASE 6.6: HUMAN-READABLE EXPLANATIONS REPORT

**Project:** LightX-IDS: Lightweight Explainable Real-Time Intrusion Detection System for Industrial IoT Networks  
**Author:** Antigravity Autonomous Agent (Pair Programming with Vamshi)  
**Date:** October 4, 2026  
**Branch:** `antigravity-development`  
**Phase:** 6.6 — Human-Readable Explanations  
**Status:** COMPLETE  
**Authoritative Frozen Model:** `backend/ml/saved_models/xgboost_h3_32.pkl`  
**Authoritative Dataset:** `dataset/lightx_ids_dataset_100k.csv` (Seed 42 Test Split)

---

## 1. OBJECTIVE

The objective of **Phase 6.6** is to bridge the semantic gap between complex mathematical attributions and operational decision-making in Industrial IoT (IIoT) control rooms. 

While Phase 6.4 established the mathematical infrastructure for local instance-level SHAP attributions and Phase 6.5 mapped attack-specific model reliance patterns, raw log-odds numbers (e.g. $\phi = +3.3264$, margin $= +5.046$) cannot be directly interpreted by plant engineers or operational security analysts during live operations.

Phase 6.6 introduces `HumanReadableExplainer`, an explainability translation layer that consumes numerical SHAP explanations and generates concise, scientifically defensible, human-readable natural language explanations answering six fundamental questions:
1. **What did the model predict?** (ATTACK vs. NORMAL)
2. **How confident is the model?** (Controlled probability and qualitative confidence categories)
3. **Which features contributed toward the prediction?** (Ranked positive/negative drivers with plain-English descriptions)
4. **Which features pushed toward the opposite class?** (Counterbalancing evidence transparently surfaced)
5. **What attack type is associated with the sample?** (Ground truth preserved without falsely claiming model inference)
6. **What should an operator understand and do?** (Safe, actionable, non-disruptive investigative guidance)

### Strict Non-Causality & Safety Policy
SHAP values describe **model attribution across decision boundaries**, not physical causality.
- **Strictly Enforced Wording:**
  - *"The model relied strongly on..."*
  - *"This feature contributed toward the attack prediction."*
  - *"The observed pattern was associated with..."*
  - *"The model's decision was influenced by..."*
- **Strictly Prohibited Causal Language:**
  - *"The sensor caused the attack."*
  - *"This feature proves the attack."*
  - *"The motor is definitely overloaded."*
  - *"The attack was caused by packet delay."*
  - *"SHAP proves the root cause."*
- **Safety Policy:** The explainer **never** issues destructive operational commands (e.g. *"shut down the machine"*, *"disconnect the PLC"*, *"stop production"*). Guidance is strictly investigatory (*"Review"*, *"Investigate"*, *"Verify"*, *"Inspect"*, *"Correlate with plant logs"*).

---

## 2. ARCHITECTURE

The explanation pipeline maintains a clean separation of concerns:

```
+-----------------------------------------------------------------------------------------+
|                                TELEMETRY INPUT / PACKET                                 |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                  Phase 6.4: LocalShapExplainer (TreeExplainer in Margin Space)           |
|                                                                                         |
|  - Preprocessor: 32 original features -> 95 transformed features                        |
|  - Classifier: XGBoost Margin f(x) = phi_0 + sum(phi_i)                                 |
|  - Aggregation: Sum transformed one-hot features back to parent original 32 features   |
|  - Additive Fidelity Check: max |f(x) - (phi_0 + sum phi)| < 1e-4                       |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v  (Structured SHAP Dictionary)
+-----------------------------------------------------------------------------------------+
|                    Phase 6.6: HumanReadableExplainer (Translation Layer)                |
|                                                                                         |
|  1. Feature Description Mapping: Controlled plain-English descriptions for 32 features  |
|  2. Confidence Categorization: Controlled linguistic mapping (not calibrated guarantee) |
|  3. Contribution Strength Classifier: Relative log-odds magnitude scoring               |
|  4. Ground-Truth Disambiguation: Clear demarcation between label and model inference    |
|  5. Borderline Logic: Transparent uncertainty disclosure for ambiguous telemetry        |
|  6. Narrative Synthesizer: 2-4 sentence executive summary                               |
|  7. Operator Guidance Generator: Safe, non-disruptive inspection recommendations        |
|  8. Dual Output Formatter: Structured JSON-compatible dict + Console formatted text    |
+-----------------------------------------------------------------------------------------+
```

---

## 3. FEATURE DESCRIPTION MAPPING

A controlled dictionary maps all 32 original features (25 numeric, 7 categorical) from the frozen H3-32 configuration to clear, scientifically accurate domain descriptions:

| Original Feature | Feature Type | Controlled Human-Readable Description |
| :--- | :---: | :--- |
| `value` | Numeric | current sensor value |
| `value_accel` | Numeric | sensor value acceleration |
| `time_delta` | Numeric | current inter-arrival time |
| `rolling_time_delta_5` | Numeric | recent inter-arrival timing pattern |
| `rolling_time_delta_std_5` | Numeric | recent timing variability |
| `is_negative_time_delta` | Numeric | negative timestamp anomaly indicator |
| `global_time_delta` | Numeric | network-wide inter-arrival time |
| `rolling_global_td_10` | Numeric | recent network-wide inter-arrival pattern |
| `rolling_global_td_std_10` | Numeric | recent network-wide timing variability |
| `packet_rate_10` | Numeric | recent packet rate |
| `is_duplicate_value` | Numeric | immediate duplicate value indicator |
| `device_seq_gap` | Numeric | sequence number gap |
| `seq_gap_dev` | Numeric | sequence gap deviation |
| `rolling_seq_std_5` | Numeric | sequence number jitter |
| `rolling_mean_3` | Numeric | short-term rolling mean |
| `rolling_std_3` | Numeric | short-term value variability |
| `rolling_mean_5` | Numeric | medium-term rolling mean |
| `rolling_std_5` | Numeric | medium-term value variability |
| `rolling_std_10` | Numeric | recent value variability |
| `plant_duplicate_ratio_19` | Numeric | plant-wide duplicate-value ratio |
| `percentage_change` | Numeric | recent percentage change in sensor value |
| `device_mean_deviation` | Numeric | deviation from device historical mean |
| `z_score` | Numeric | statistical z-score relative to baseline |
| `rel_volatility` | Numeric | relative value volatility |
| `stability_anomaly` | Numeric | sensor stability anomaly score |
| `topic` | Categorical | MQTT topic identity |
| `device_id` | Categorical | device identity |
| `sensor_code` | Categorical | sensor identity code |
| `sensor_type` | Categorical | sensor type |
| `unit` | Categorical | measurement unit |
| `status` | Categorical | sensor status |
| `source` | Categorical | telemetry source |

*Graceful Degradation:* Any unanticipated feature name defaults automatically to clean space-delimited text (`feature.replace('_', ' ')`).

---

## 4. CONFIDENCE LANGUAGE POLICY

Probability outputs from tree-based models like XGBoost are not inherently calibrated posterior probabilities. To prevent misleading operators regarding statistical certainty, `HumanReadableExplainer` applies a controlled linguistic classification policy:

| Model-Assigned $P(\text{Attack})$ | Controlled Linguistic Category | Scientific Interpretation |
| :---: | :--- | :--- |
| $\ge 90\%$ | `high model confidence` | Substantial accumulation of attack-directed evidence |
| $70\% \le P < 90\%$ | `moderate-to-high model confidence` | Strong balance of evidence toward attack |
| $50\% \le P < 70\%$ | `moderate model confidence` | Plurality of evidence toward attack, notable opposition |
| $30\% \le P < 50\%$ | `moderate evidence toward Normal` | Evidence favors normal nominal operations |
| $< 30\%$ | `low attack probability` | Negligible or absence of anomalous evidence |

**Disclaimed Rule:** The system reports *"The model assigned an $X\%$ attack probability"* rather than *"The system is $X\%$ certain an attack occurred."*

---

## 5. SHAP-TO-LANGUAGE TRANSLATION RULES

### Relative Contribution Strength
Feature contributions in margin log-odds space are categorized by absolute magnitude $|\phi|$:
- **Very strong** ($|\phi| \ge 2.0$): Dominant driver shifting prediction margin by $\ge 2.0$ log-odds units.
- **Strong** ($1.0 \le |\phi| < 2.0$): Major contributor exerting noticeable influence.
- **Moderate** ($0.3 \le |\phi| < 1.0$): Secondary contributor reinforcing the decision.
- **Weak** ($|\phi| < 0.3$): Minor background contribution.

### Attribution Sentences
- **Attack-directed ($\phi > 0$):**  
  `"The {description} contributed {adverb} toward the Attack prediction (SHAP: +{val:.4f})."`
- **Normal-directed ($\phi < 0$):**  
  `"The {description} contributed {adverb} toward the Normal prediction (SHAP: {val:.4f})."`

---

## 6. REPRESENTATIVE EXPLANATIONS

Using the frozen test split ($N=10,001$, seed 42), explanations were programmatically generated for the authoritative representative records.

### Case 1: DoS Attack (Record #3203)
- **Ground Truth Context:** The dataset records this sample as DoS Attack.
- **Prediction:** `ATTACK` ($P(\text{Attack}) = 99.36\%$, `high model confidence`)
- **Model Margin:** $+5.0460$ (Base value: $-0.2719$)
- **Summary:**  
  *Attack detected with a 99.36% model-assigned attack probability (high model confidence). The prediction was driven primarily by plant-wide duplicate-value ratio and recent inter-arrival timing pattern. These features contributed strongly toward the Attack prediction, while MQTT topic identity contributed toward the Normal side.*
- **Top Attack Contributors:**
  1. `plant_duplicate_ratio_19` (plant-wide duplicate-value ratio): $+3.3264$ (**very strong**, raw: $0.3158$)
  2. `rolling_time_delta_5` (recent inter-arrival timing pattern): $+0.8334$ (**moderate**, raw: $0.0630\text{ s}$)
  3. `rolling_time_delta_std_5` (recent timing variability): $+0.7326$ (**moderate**, raw: $0.0025$)
- **Top Normal Contributor:**
  1. `topic` (MQTT topic identity): $-0.1110$ (**weak**, raw: `factory/line1/pressure`)
- **Operator Guidance:**  
  *The model detected an abnormal telemetry pattern characterized by plant-wide duplicate-value ratio and recent inter-arrival timing pattern. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.*

### Case 2: Replay Attack (Record #10977)
- **Ground Truth Context:** The dataset records this sample as Replay Attack.
- **Prediction:** `ATTACK` ($P(\text{Attack}) = 99.99\%$, `high model confidence`)
- **Model Margin:** $+9.1711$ (Base value: $-0.2719$)
- **Summary:**  
  *Attack detected with a 99.99% model-assigned attack probability (high model confidence). The prediction was driven primarily by recent network-wide timing variability and recent packet rate. These features contributed strongly toward the Attack prediction, while short-term rolling mean contributed toward the Normal side.*
- **Top Attack Contributors:**
  1. `rolling_global_td_std_10` (recent network-wide timing variability): $+4.4048$ (**very strong**, raw: $2.3475$)
  2. `packet_rate_10` (recent packet rate): $+1.8355$ (**strong**, raw: $-6.5934$)
  3. `rolling_time_delta_std_5` (recent timing variability): $+1.5541$ (**strong**, raw: $1.5694$)
- **Top Normal Contributor:**
  1. `rolling_mean_3` (short-term rolling mean): $-0.0531$ (**weak**, raw: $0.1000$)

### Case 3: Sensor Freeze Attack (Record #48510)
- **Ground Truth Context:** The dataset records this sample as Sensor Freeze Attack.
- **Prediction:** `ATTACK` ($P(\text{Attack}) = 99.94\%$, `high model confidence`)
- **Model Margin:** $+7.4103$ (Base value: $-0.2719$)
- **Top Attack Contributors:**
  1. `plant_duplicate_ratio_19` (plant-wide duplicate-value ratio): $+5.5510$ (**very strong**, raw: $1.0000$)
  2. `rolling_time_delta_5` (recent inter-arrival timing pattern): $+1.4363$ (**strong**, raw: $0.1688\text{ s}$)

### Case 4: Motor Overload Attack (Record #75660)
- **Ground Truth Context:** The dataset records this sample as Motor Overload Attack.
- **Prediction:** `ATTACK` ($P(\text{Attack}) = 99.66\%$, `high model confidence`)
- **Model Margin:** $+5.6721$ (Base value: $-0.2719$)
- **Summary:**  
  *Attack detected with a 99.66% model-assigned attack probability (high model confidence). The prediction was driven primarily by recent percentage change in sensor value and plant-wide duplicate-value ratio. These features contributed strongly toward the Attack prediction, while recent inter-arrival timing pattern contributed toward the Normal side.*
- **Top Attack Contributors (Physical Dominance):**
  1. `percentage_change` (recent percentage change in sensor value): $+1.7844$ (**strong**, raw: $+0.00063$)
  2. `plant_duplicate_ratio_19` (plant-wide duplicate-value ratio): $+1.1052$ (**strong**, raw: $0.6316$)
  3. `rel_volatility` (relative value volatility): $+0.6408$ (**moderate**, raw: $0.0109$)
  4. `packet_rate_10` (recent packet rate): $+0.4972$ (**moderate**, raw: $41.87$)
  5. `rolling_std_10` (recent value variability): $+0.4485$ (**moderate**, raw: $0.0908$)

### Case 5: Slow Drift Attack (Record #88360)
- **Ground Truth Context:** The dataset records this sample as Slow Drift Attack.
- **Prediction:** `ATTACK` ($P(\text{Attack}) = 99.99\%$, `high model confidence`)
- **Model Margin:** $+9.0006$ (Base value: $-0.2719$)
- **Top Attack Contributors:**
  1. `plant_duplicate_ratio_19` (plant-wide duplicate-value ratio): $+5.1410$ (**very strong**, raw: $0.1579$)
  2. `time_delta` (current inter-arrival time): $+0.8796$ (**moderate**, raw: $0.3178\text{ s}$)

---

## 7. NORMAL PREDICTION EXPLANATION

The explainer operates symmetrically for normal, non-anomalous telemetry.

### Case 6: Normal Telemetry (Record #93364)
- **Ground Truth Context:** Recorded attack type: not provided (Nominal test record).
- **Prediction:** `NORMAL` ($P(\text{Attack}) = 0.01\%$, `low attack probability`)
- **Model Margin:** $-9.2341$ (Base value: $-0.2719$)
- **Borderline Flag:** `False`
- **Summary:**  
  *The model assigned a 0.01% attack probability (low attack probability) and predicted Normal. The strongest contributions pushed toward the Normal class, particularly plant-wide duplicate-value ratio and recent inter-arrival timing pattern. Minor evidence toward Attack came from recent network-wide inter-arrival pattern, but was outweighed by normal indications.*
- **Top Normal-Directed Contributors (-):**
  1. `plant_duplicate_ratio_19` (plant-wide duplicate-value ratio): $-4.1898$ (**very strong**, raw: $0.8421$)
  2. `rolling_time_delta_5` (recent inter-arrival timing pattern): $-3.1309$ (**very strong**, raw: $0.3246\text{ s}$)
  3. `rolling_time_delta_std_5` (recent timing variability): $-0.7790$ (**moderate**, raw: $0.0250$)
- **Top Attack-Directed Contributor (+):**
  1. `rolling_global_td_10` (recent network-wide inter-arrival pattern): $+0.0974$ (**weak**, raw: $5.2 \times 10^{-6}\text{ s}$)
- **Operator Guidance:**  
  *Operator interpretation: Telemetry patterns fall within nominal operating boundaries. The model did not detect an anomalous pattern in this sample. Standard monitoring continues.*

---

## 8. BORDERLINE / UNCERTAIN CASE HANDLING

When telemetry produces conflicting evidence where $0.30 \le P(\text{Attack}) \le 0.70$, `HumanReadableExplainer` flags `is_borderline = True` and suppresses overconfident assertions.

### Borderline Demonstration (Mock Ambiguous Sample, $P=52.3\%$)
- **Assigned Attack Probability:** $52.30\%$ (`moderate model confidence`)
- **Borderline Flag:** `True`
- **Summary:**  
  *The model's prediction is relatively uncertain (assigned attack probability: 52.30%, moderate model confidence), with evidence distributed between Attack and Normal. While recent timing variability provided evidence toward Attack, recent network-wide inter-arrival pattern contributed toward Normal. The final prediction is ATTACK based on the decision threshold.*
- **Operator Guidance:**  
  *Operator interpretation: Telemetry exhibits borderline characteristics with conflicting evidence between attack and normal patterns. Monitor subsequent packets on this telemetry stream for persistent anomalies before initiating operational investigations.*

---

## 9. SCIENTIFIC & OPERATIONAL LIMITATIONS

All generated explanations embed four mandatory disclosures:
1. **Model Attribution, Not Physical Causality:** SHAP isolates the mathematical influence of features on model decision boundaries. A feature with high positive SHAP was relied upon by the model, but did not physically initiate the cyber-attack.
2. **Qualitative Labels:** Confidence categories are qualitative communication brackets, not calibrated Bayesian posterior probabilities.
3. **No Independent Ground-Truth Inference:** SHAP explanations explain why a sample is flagged as an attack; they do not infer or verify the specific attack label (e.g., DoS vs. Spoofing).
4. **Advisory Guidance:** Control room guidance is purely investigatory. Automated control room actuators must not trigger physical shutdowns solely based on ML telemetry alerts without secondary validation.

---

## 10. LANGUAGE SAFETY & CAUSAL AUDIT

An automated audit test (`test_10_scientific_safety_audit_no_causal_language` in `backend/ml/tests/test_human_explainer.py`) scans all generated text fields (summaries, operator guidance, sentences) against prohibited causal terms:
- `"caused by"`
- `"caused the attack"`
- `"proves"`
- `"root cause"`
- `"definitely"`
- `"guarantees"`

**Audit Result:**  
**100% COMPLIANT.** Zero prohibited terms detected in any narrative field.

---

## 11. UNIT TESTS & VERIFICATION

A comprehensive test suite was established in `backend/ml/tests/test_human_explainer.py`.

### Test Execution Summary
- **Command:**  
  `PYTHONPATH=. ./venv/bin/python -m unittest backend/ml/tests/test_human_explainer.py -v`
- **Output:**
  ```
  test_01_attack_explanation_generation ... ok
  test_02_normal_explanation_generation ... ok
  test_03_borderline_prediction_handling ... ok
  test_04_probability_formatting ... ok
  test_05_positive_shap_direction ... ok
  test_06_negative_shap_direction ... ok
  test_07_feature_description_lookup ... ok
  test_08_unknown_feature_handling ... ok
  test_09_attack_type_correctly_distinguished ... ok
  test_10_scientific_safety_audit_no_causal_language ... ok
  test_11_structured_output_fields ... ok
  test_12_summary_generated_and_concise ... ok
  test_13_operator_interpretation_safe_and_actionable ... ok

  Ran 13 tests in 0.102s
  OK
  ```

### Full Project Regression Suite
1. `backend/ml/tests` (Full ML Suite): **43/43 tests pass (OK)**
2. `backend/tests` (Full Backend Suite): **26/26 tests pass (OK)**
3. `git diff --check`: **Clean (0 errors)**

---

## 12. FINAL VERDICT

```
================================================================================
FINAL VERDICT: A — PASS / READY FOR 6.7
================================================================================
```

### Justification:
1. **Exact Translation:** Consumes pre-computed SHAP attributions from `LocalShapExplainer` without loss of mathematical fidelity.
2. **Rigorous Non-Causality:** Validated by automated language audits; zero causal overclaiming.
3. **Safety Compliant:** Operator guidance is strictly investigatory and avoids dangerous physical shutdown commands.
4. **Symmetric Explanations:** Clean, scientifically grounded explanations generated for Attack, Normal, and Borderline telemetry.
5. **Zero Tampering:** Frozen Phase 5 model and Phase 1–5 code remain completely untouched.
6. **Full Test Coverage:** 13 new unit tests pass; all 69 project-wide unit tests pass without regression.

Phase 6.6 is complete and ready for **Phase 6.7: Validation & Audit**.
