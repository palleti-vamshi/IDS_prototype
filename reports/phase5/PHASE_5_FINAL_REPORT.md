# LightX-IDS — Phase 5 Final Report
## False Positive Reduction & Robustness

**Status:** COMPLETE
**Final feature candidate:** H3-32
**Decision:** FREEZE H3-32 for Phase 6
**Dataset:** `dataset/lightx_ids_dataset.csv` (100,000 records)
**Evaluation seeds:** 42–51
**Phase 1–3 status:** Frozen
**Phase 4 / 4.1 status:** Frozen

---

## 1. Objective

Phase 5 evaluated false-positive behavior and temporal robustness of the Phase 4 LightX-IDS XGBoost pipeline.

The goal was not to maximize accuracy alone. The experiments prioritized:

- false-positive rate (FPR)
- false positives (FP)
- false negatives (FN)
- attack recall
- F1
- temporal generalization
- seed robustness
- preservation of the conventional 100K benchmark

All Stage 5–8 experiments were read-only with respect to the dataset and labels.

---

## 2. Final Feature Decision

The final H3 candidate removes four physical-dynamics features from the 36-feature Phase 4 baseline:

- `value_change`
- `abs_value_change`
- `rolling_range_5`
- `rolling_mean_10`

This produces the **H3-32** feature configuration.

The selection was based on targeted ablation, hybrid feature selection, multi-protocol validation, and finally a 10-seed robustness study.

The four removed features were not removed because they were universally useless. Rather, their contribution was associated with temporal distribution sensitivity, particularly under strict chronological evaluation.

---

## 3. Evaluation Protocols

### Stratified 100K

The conventional 80/10/10 stratified benchmark was retained to verify that Phase 5 did not materially damage the Phase 4 benchmark.

### Controlled Temporal

- Train: records 1–89,000
- Validation: records 89,001–90,000
- Test: records 90,001–100,000

This protocol specifically controls the Slow Drift temporal transition while retaining Slow Drift examples in training.

### Strict Chronological

- Train: records 1–80,000
- Validation: records 80,001–90,000
- Test: records 90,001–100,000

This is the hardest temporal generalization protocol and exposes the effect of unseen temporal/attack distribution shifts.

Thresholds are selected using validation F1 only. Test data is not used for threshold selection.

---

## 4. Stage 8 — 10-Seed Final Robustness

Seeds: **42, 43, 44, 45, 46, 47, 48, 49, 50, 51**

### 4.1 Stratified 100K

| Metric | Baseline-36 | H3-32 |
|---|---:|---:|
| F1 | 99.47 ± 0.03% | **99.47 ± 0.03%** |
| Recall | 99.52 ± 0.13% | **99.57 ± 0.13%** |
| FPR | 0.45 ± 0.07% | 0.47 ± 0.08% |
| FP | 25.3 ± 4.2 | 26.8 ± 4.7 |
| FN | 20.9 ± 5.8 | **18.6 ± 5.6** |

Interpretation: H3 preserves the conventional benchmark. The F1 difference is negligible (+0.01 percentage points), while mean FN decreases.

---

### 4.2 Controlled Temporal

| Metric | Baseline-36 | H3-32 |
|---|---:|---:|
| F1 | 92.48 ± 1.75% | **93.33 ± 2.68%** |
| Recall | 99.74 ± 0.03% | **99.77 ± 0.05%** |
| FPR | 3.43 ± 0.86% | **3.03 ± 1.30%** |
| FP | 282.3 ± 71.2 | **249.6 ± 107.4** |
| FN | 4.5 ± 0.5 | **4.1 ± 0.9** |

Mean changes:

- F1: **+0.853 pp**
- Recall: **+0.023 pp**
- FPR: **−0.397 pp**
- FP: **−32.7**
- FN: **−0.4**

Important limitation: the improvement is seed-sensitive. H3 improved F1 in 4/10 seeds and reduced FP in 4/10 seeds. Therefore the result must be reported as an average robustness improvement, not as a guaranteed per-seed FP reduction.

---

### 4.3 Strict Chronological

| Metric | Baseline-36 | H3-32 |
|---|---:|---:|
| F1 | 53.33 ± 2.72% | **59.53 ± 3.64%** |
| Recall | 46.99 ± 3.16% | **54.80 ± 5.05%** |
| FPR | 6.22 ± 0.25% | **6.20 ± 0.12%** |
| FP | 512.5 ± 20.4 | **510.5 ± 9.6** |
| FN | 933.0 ± 55.6 | **795.6 ± 88.9** |

Mean changes:

- F1: **+6.208 pp**
- Recall: **+7.807 pp**
- FPR: **−0.024 pp**
- FP: **−2.0**
- FN: **−137.4**

Most important robustness result:

- H3 improved F1 in **10/10 seeds**
- H3 improved recall in **10/10 seeds**

This provides the strongest evidence that H3 improves temporal generalization rather than merely optimizing a single random seed.

---

## 5. False-Positive Findings

Earlier Phase 5 diagnostics showed that the principal FP problem is concentrated around the transition following Slow Drift.

The first FP repeatedly appears at record **91761** in controlled temporal experiments.

Stage 7 further showed that H3's cross-seed instability is primarily concentrated in normal samples:

- overall binary prediction disagreement: 2.92%
- normal-row disagreement: 3.51%
- attack-row disagreement: 0.17%

Several normal records around the transition were classified as attack by all five Stage 7 H3 seeds with probabilities near 0.998–0.999.

These records span multiple devices and sensor types. Therefore the remaining FP problem is better interpreted as a broader temporal/plant-state distribution shift than as a single defective sensor.

---

## 6. Why H3 Is Frozen

H3 satisfies the final selection requirements:

1. **No material degradation of the conventional benchmark**
2. **Improved average controlled-temporal F1 and FPR**
3. **Strong improvement under strict chronological evaluation**
4. **Strict chronological F1 improved in 10/10 seeds**
5. **Strict chronological recall improved in 10/10 seeds**
6. **Mean strict chronological FN decreased by 137.4**
7. **No dataset or label changes were required**

Therefore:

> **H3-32 is frozen as the Phase 5 final feature configuration.**

The controlled-temporal FP improvement remains seed-sensitive and must be presented with that limitation.

---

## 7. Research Interpretation

The Phase 5 evidence suggests that several physical-dynamics features can become overly sensitive to temporal distribution changes.

In particular, removing `value_change`, `abs_value_change`, `rolling_range_5`, and `rolling_mean_10` reduces the model's dependence on short-term physical-dynamics patterns that are not equally stable across temporal protocols.

The strongest evidence appears under strict chronological evaluation, where H3 consistently improves attack recall and F1 across all ten seeds.

This supports the interpretation that the feature reduction improves robustness to temporal distribution shift rather than simply improving the random stratified benchmark.

---

## 8. Important Limitations

Phase 5 does **not** establish perfect real-world generalization.

Known limitations remain:

- The LightX dataset is a software-simulated industrial environment.
- Strict chronological performance remains substantially lower than the stratified benchmark.
- Slow Drift has a known simulation-duration inconsistency documented in Phase 3.
- The controlled-temporal FP benefit is seed-sensitive.
- Some highly confident normal FPs remain concentrated around temporal state transitions.
- External validation on a genuinely independent industrial dataset is still required for stronger claims of real-world generalization.

These limitations should be retained in the final research paper.

---

## 9. Phase 5 Final Status

**PHASE 5: COMPLETE**

Final configuration:

**Baseline-36 → H3-32**

Removed:

```text
value_change
abs_value_change
rolling_range_5
rolling_mean_10
```

Final decision:

**FREEZE H3-32**

Next phase:

**Phase 6 — Explainability**

The frozen Phase 5 configuration should be used as the feature definition for subsequent explainability experiments. No further feature search should be performed unless Phase 6 reveals a concrete reproducibility or interpretability problem.
