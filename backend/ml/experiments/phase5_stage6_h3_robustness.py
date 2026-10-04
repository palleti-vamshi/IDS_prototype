"""
LightX-IDS Phase 5 — Stage 6: H3 Robustness Validation

Leading candidate H3:
Remove:
  - value_change
  - abs_value_change
  - rolling_range_5
  - rolling_mean_10

Purpose:
Validate H3 before any production/configuration change.

Protocols:
  A) STRATIFIED_100K
  B) CONTROLLED_TEMPORAL
  C) STRICT_CHRONOLOGICAL

Multi-seed:
  42, 43, 44, 45, 46

Important:
- Read-only.
- No dataset/label modification.
- No config.py modification.
- Threshold selected on validation only.
- H3 is compared against the unchanged 36-feature baseline.
"""

from pathlib import Path
import sys, time
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ml.config import LIGHTX_100K, NUMERIC_COLUMNS, CATEGORICAL_COLUMNS
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.ml.feature_engineering.feature_selector import FeatureSelector

SEEDS = [42, 43, 44, 45, 46]
ATTACK_NAME = "Slow Drift Attack"

H3_REMOVED = {
    "value_change",
    "abs_value_change",
    "rolling_range_5",
    "rolling_mean_10",
}

BASE_PARAMS = dict(
    n_estimators=400,
    learning_rate=0.05,
    max_depth=10,
    min_child_weight=2,
    subsample=0.90,
    colsample_bytree=0.90,
    reg_alpha=0.10,
    reg_lambda=3.0,
    objective="binary:logistic",
    eval_metric="logloss",
    tree_method="hist",
    n_jobs=-1,
)

def threshold_search(model, X, y):
    p = model.predict_proba(X)[:, 1]
    best_t, best_f1 = 0.50, -1.0
    for t in np.round(np.arange(0.10, 0.901, 0.05), 2):
        pred = (p >= t).astype(int)
        score = f1_score(y, pred, zero_division=0)
        if score > best_f1:
            best_t, best_f1 = float(t), float(score)
    return best_t, best_f1

def evaluate(X_train, y_train, X_val, y_val, X_test, y_test,
             removed, seed):
    num = [
        c for c in NUMERIC_COLUMNS
        if c in X_train.columns and c not in removed
    ]
    cat = [c for c in CATEGORICAL_COLUMNS if c in X_train.columns]

    pre = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), num),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            )),
        ]), cat),
    ])

    params = BASE_PARAMS.copy()
    params["random_state"] = seed

    pipe = Pipeline([
        ("preprocess", pre),
        ("model", XGBClassifier(**params)),
    ])

    start = time.perf_counter()
    pipe.fit(X_train[num + cat], y_train)
    train_sec = time.perf_counter() - start

    threshold, val_f1 = threshold_search(
        pipe, X_val[num + cat], y_val
    )

    probs = pipe.predict_proba(X_test[num + cat])[:, 1]
    preds = (probs >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test, preds, labels=[0, 1]
    ).ravel()

    return {
        "features": len(num) + len(cat),
        "threshold": threshold,
        "val_f1": val_f1,
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision_score(y_test, preds, zero_division=0),
        "recall": recall_score(y_test, preds, zero_division=0),
        "f1": f1_score(y_test, preds, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probs),
        "pr_auc": average_precision_score(y_test, probs),
        "fpr": fp / (fp + tn) if (fp + tn) else 0.0,
        "fnr": fn / (fn + tp) if (fn + tp) else 0.0,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "train_sec": train_sec,
        "probs": probs,
    }

def prepare_stream(df):
    fg = FeatureGenerator()
    return fg.generate_causal_stream_features(df)

def transform_split(stream, tr_idx, va_idx, te_idx):
    train = stream.iloc[tr_idx].copy()
    val = stream.iloc[va_idx].copy()
    test = stream.iloc[te_idx].copy()

    y_train = train.pop("label")
    y_val = val.pop("label")
    y_test = test.pop("label")

    fg = FeatureGenerator()
    fg.fit(train)

    Xtr_raw = fg.transform(train)
    Xva_raw = fg.transform(val)
    Xte_raw = fg.transform(test)

    selector = FeatureSelector()
    Xtr, ytr = selector.split(
        Xtr_raw.assign(label=y_train.values)
    )
    Xva, yva = selector.split(
        Xva_raw.assign(label=y_val.values)
    )
    Xte, yte = selector.split(
        Xte_raw.assign(label=y_test.values)
    )

    return train, val, test, Xtr, ytr, Xva, yva, Xte, yte

def stratified_indices(stream, seed):
    indices = np.arange(len(stream))

    train_idx, test_idx = train_test_split(
        indices,
        test_size=0.20,
        stratify=stream["label"],
        random_state=seed,
    )

    val_idx, test_idx = train_test_split(
        test_idx,
        test_size=0.50,
        stratify=stream.iloc[test_idx]["label"],
        random_state=seed,
    )

    return train_idx, val_idx, test_idx

def fixed_temporal_indices():
    return (
        np.arange(0, 89000),
        np.arange(89000, 90000),
        np.arange(90000, 100000),
    )

def fixed_strict_indices():
    return (
        np.arange(0, 80000),
        np.arange(80000, 90000),
        np.arange(90000, 100000),
    )

def main():
    print("=" * 105)
    print("LIGHTX-IDS PHASE 5 — STAGE 6 H3 ROBUSTNESS VALIDATION")
    print("=" * 105)
    print("H3 removes:", ", ".join(sorted(H3_REMOVED)))
    print("Seeds:", SEEDS)

    df = pd.read_csv(LIGHTX_100K).sort_values(
        "record_id"
    ).reset_index(drop=True)

    stream = prepare_stream(df)

    results = []

    for seed in SEEDS:
        protocols = {
            "STRATIFIED_100K": stratified_indices(stream, seed),
            "CONTROLLED_TEMPORAL": fixed_temporal_indices(),
            "STRICT_CHRONOLOGICAL": fixed_strict_indices(),
        }

        for protocol, (tr_idx, va_idx, te_idx) in protocols.items():
            print("\n" + "-" * 105)
            print(f"SEED={seed} | {protocol}")
            print("-" * 105)

            (
                train_meta, val_meta, test_meta,
                Xtr, ytr, Xva, yva, Xte, yte
            ) = transform_split(stream, tr_idx, va_idx, te_idx)

            for candidate, removed in [
                ("BASELINE_36", set()),
                ("H3_32", H3_REMOVED),
            ]:
                result = evaluate(
                    Xtr, ytr, Xva, yva, Xte, yte,
                    removed, seed
                )

                attack_mask = test_meta["attack_type"].eq(
                    ATTACK_NAME
                ).to_numpy()

                slow_recall = (
                    float(np.mean(
                        result["probs"][attack_mask] >= result["threshold"]
                    ))
                    if attack_mask.any()
                    else float("nan")
                )

                row = {
                    "seed": seed,
                    "protocol": protocol,
                    "candidate": candidate,
                    "features": result["features"],
                    "threshold": result["threshold"],
                    "val_f1": result["val_f1"],
                    "accuracy": result["accuracy"],
                    "precision": result["precision"],
                    "recall": result["recall"],
                    "f1": result["f1"],
                    "roc_auc": result["roc_auc"],
                    "pr_auc": result["pr_auc"],
                    "fpr": result["fpr"],
                    "fnr": result["fnr"],
                    "tn": result["tn"],
                    "fp": result["fp"],
                    "fn": result["fn"],
                    "tp": result["tp"],
                    "slow_drift_recall": slow_recall,
                    "train_sec": result["train_sec"],
                }
                results.append(row)

                print(
                    f"{candidate:14s} "
                    f"F1={row['f1']*100:6.2f}%  "
                    f"Acc={row['accuracy']*100:6.2f}%  "
                    f"Recall={row['recall']*100:6.2f}%  "
                    f"FPR={row['fpr']*100:5.2f}%  "
                    f"FP={row['fp']:4d}  "
                    f"FN={row['fn']:4d}  "
                    f"Thr={row['threshold']:.2f}"
                )

    out = pd.DataFrame(results)

    print("\n" + "=" * 105)
    print("STAGE 6 — MULTI-SEED MEAN ± STD")
    print("=" * 105)

    for protocol in out["protocol"].unique():
        print(f"\n--- {protocol} ---")
        subset = out[out["protocol"] == protocol]

        summary = subset.groupby("candidate").agg(
            accuracy_mean=("accuracy", "mean"),
            accuracy_std=("accuracy", "std"),
            precision_mean=("precision", "mean"),
            precision_std=("precision", "std"),
            recall_mean=("recall", "mean"),
            recall_std=("recall", "std"),
            f1_mean=("f1", "mean"),
            f1_std=("f1", "std"),
            roc_mean=("roc_auc", "mean"),
            roc_std=("roc_auc", "std"),
            pr_mean=("pr_auc", "mean"),
            pr_std=("pr_auc", "std"),
            fpr_mean=("fpr", "mean"),
            fpr_std=("fpr", "std"),
            fnr_mean=("fnr", "mean"),
            fnr_std=("fnr", "std"),
            fp_mean=("fp", "mean"),
            fp_std=("fp", "std"),
            fn_mean=("fn", "mean"),
            fn_std=("fn", "std"),
            slow_recall_mean=("slow_drift_recall", "mean"),
            slow_recall_std=("slow_drift_recall", "std"),
            train_sec_mean=("train_sec", "mean"),
        )

        print(summary.to_string())

    print("\n" + "=" * 105)
    print("STAGE 6 — PER-SEED H3 DELTA")
    print("=" * 105)

    for protocol in out["protocol"].unique():
        b = out[
            (out.protocol == protocol) &
            (out.candidate == "BASELINE_36")
        ].set_index("seed")

        h = out[
            (out.protocol == protocol) &
            (out.candidate == "H3_32")
        ].set_index("seed")

        delta = pd.DataFrame(index=SEEDS)
        delta["delta_f1_pp"] = (h["f1"] - b["f1"]) * 100
        delta["delta_recall_pp"] = (h["recall"] - b["recall"]) * 100
        delta["delta_fpr_pp"] = (h["fpr"] - b["fpr"]) * 100
        delta["delta_fp"] = h["fp"] - b["fp"]
        delta["delta_fn"] = h["fn"] - b["fn"]

        print(f"\n--- {protocol} ---")
        print(delta.to_string())

    print("\nNo files were modified.")
    print("H3 is NOT frozen by this script.")

if __name__ == "__main__":
    main()
