"""
LightX-IDS Phase 5 — Stage 4: Targeted Physical-Feature Analysis

Goal:
Identify which individual physical-dynamics features are responsible for:
1) controlled-temporal false positives, and
2) strict-chronological generalization.

Read-only experiment:
- Does NOT modify the dataset.
- Does NOT modify labels.
- Does NOT modify project source files.
- Uses the same canonical XGBoost protocol as Phase 5 Stage 3.
- Threshold is selected from validation only.

For each selected physical-dynamics feature:
    BASELINE = all 36 selected features
    ABLATION = baseline minus exactly ONE physical feature

Protocols:
    CONTROLLED_TEMPORAL:
      train rows 1..89000
      validation 89001..90000
      test 90001..100000

    STRICT_CHRONOLOGICAL:
      train rows 1..80000
      validation 80001..90000
      test 90001..100000

Interpretation:
A useful feature for Phase 5 should ideally reduce controlled FPs
without causing a substantial strict-chronological recall/F1 loss.
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
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ml.config import LIGHTX_100K, NUMERIC_COLUMNS, CATEGORICAL_COLUMNS
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.ml.feature_engineering.feature_selector import FeatureSelector

SEED = 42
ATTACK_NAME = "Slow Drift Attack"

# Physical-dynamics candidates used by Stage 3 Candidate D.
PHYSICAL_FEATURES = [
    "value_change",
    "abs_value_change",
    "value_accel",
    "rolling_mean_3",
    "rolling_std_3",
    "rolling_mean_5",
    "rolling_std_5",
    "rolling_mean_10",
    "rolling_std_10",
    "rolling_std",
    "rolling_max",
    "rolling_min",
    "rolling_range_5",
    "percentage_change",
]

XGB_PARAMS = dict(
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
    random_state=SEED,
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

def evaluate(X_train, y_train, X_val, y_val, X_test, y_test, removed):
    num = [c for c in NUMERIC_COLUMNS if c in X_train.columns and c not in removed]
    cat = [c for c in CATEGORICAL_COLUMNS if c in X_train.columns]

    pre = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), num),
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), cat),
    ])

    pipe = Pipeline([
        ("preprocess", pre),
        ("model", XGBClassifier(**XGB_PARAMS)),
    ])

    start = time.perf_counter()
    pipe.fit(X_train[num + cat], y_train)
    train_sec = time.perf_counter() - start

    threshold, val_f1 = threshold_search(pipe, X_val[num + cat], y_val)

    probs = pipe.predict_proba(X_test[num + cat])[:, 1]
    preds = (probs >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, preds, labels=[0, 1]).ravel()

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
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "train_sec": train_sec,
        "probs": probs,
    }

def prepare_split(stream, tr_idx, va_idx, te_idx):
    train = stream.iloc[tr_idx].copy()
    val = stream.iloc[va_idx].copy()
    test = stream.iloc[te_idx].copy()

    y_train = train.pop("label")
    y_val = val.pop("label")
    y_test = test.pop("label")

    # Feature generation is already causal in the stream. Selector is fit only
    # on the training partition and then applied consistently.
    fg = FeatureGenerator()
    fg.fit(train)

    X_train_raw = fg.transform(train)
    X_val_raw = fg.transform(val)
    X_test_raw = fg.transform(test)

    selector = FeatureSelector()
    X_train, y_train = selector.split(X_train_raw.assign(label=y_train.values))
    X_val, y_val = selector.split(X_val_raw.assign(label=y_val.values))
    X_test, y_test = selector.split(X_test_raw.assign(label=y_test.values))

    return train, val, test, X_train, y_train, X_val, y_val, X_test, y_test

def main():
    print("=" * 100)
    print("LIGHTX-IDS PHASE 5 — STAGE 4 TARGETED PHYSICAL-FEATURE ANALYSIS")
    print("=" * 100)

    df = pd.read_csv(LIGHTX_100K).sort_values("record_id").reset_index(drop=True)

    fg_stream = FeatureGenerator()
    stream = fg_stream.generate_causal_stream_features(df)

    protocols = {
        "CONTROLLED_TEMPORAL": (
            np.arange(0, 89000),
            np.arange(89000, 90000),
            np.arange(90000, 100000),
        ),
        "STRICT_CHRONOLOGICAL": (
            np.arange(0, 80000),
            np.arange(80000, 90000),
            np.arange(90000, 100000),
        ),
    }

    all_rows = []

    for protocol, (tr_idx, va_idx, te_idx) in protocols.items():
        print("\n" + "=" * 100)
        print(protocol)
        print("=" * 100)

        train_meta, val_meta, test_meta, Xtr, ytr, Xva, yva, Xte, yte = prepare_split(
            stream, tr_idx, va_idx, te_idx
        )

        available = [f for f in PHYSICAL_FEATURES if f in Xtr.columns]
        missing = [f for f in PHYSICAL_FEATURES if f not in Xtr.columns]

        print(f"Selected physical features available: {len(available)}")
        print("Available:", ", ".join(available))
        if missing:
            print("Not present after selection:", ", ".join(missing))

        experiments = [("BASELINE", None)] + [
            (f"ABLATE_{feature}", feature) for feature in available
        ]

        for name, feature in experiments:
            removed = {feature} if feature else set()
            result = evaluate(Xtr, ytr, Xva, yva, Xte, yte, removed)

            attack_mask = test_meta["attack_type"].eq(ATTACK_NAME).to_numpy()
            slow_recall = (
                float(np.mean(result["probs"][attack_mask] >= result["threshold"]))
                if attack_mask.any() else float("nan")
            )

            row = {
                "protocol": protocol,
                "experiment": name,
                "removed_feature": feature or "NONE",
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
            all_rows.append(row)

            print(
                f"{name:35s} "
                f"F1={row['f1']*100:6.2f}%  "
                f"FPR={row['fpr']*100:5.2f}%  "
                f"Recall={row['recall']*100:6.2f}%  "
                f"FP={row['fp']:4d}  FN={row['fn']:4d}  "
                f"Thr={row['threshold']:.2f}"
            )

    out = pd.DataFrame(all_rows)

    print("\n" + "=" * 100)
    print("STAGE 4 SUMMARY — CHANGE VS BASELINE")
    print("=" * 100)

    for protocol in protocols:
        base = out[(out.protocol == protocol) & (out.experiment == "BASELINE")].iloc[0]
        rows = out[(out.protocol == protocol) & (out.experiment != "BASELINE")].copy()

        rows["delta_fp"] = rows["fp"] - base["fp"]
        rows["fp_reduction_pct"] = (base["fp"] - rows["fp"]) / base["fp"] * 100.0
        rows["delta_f1_pp"] = (rows["f1"] - base["f1"]) * 100.0
        rows["delta_recall_pp"] = (rows["recall"] - base["recall"]) * 100.0
        rows["delta_fpr_pp"] = (rows["fpr"] - base["fpr"]) * 100.0

        print(f"\n--- {protocol} ---")
        print(
            rows[
                [
                    "removed_feature",
                    "fp",
                    "delta_fp",
                    "fp_reduction_pct",
                    "fn",
                    "delta_f1_pp",
                    "delta_recall_pp",
                    "delta_fpr_pp",
                    "slow_drift_recall",
                ]
            ].sort_values("fp_reduction_pct", ascending=False).to_string(index=False)
        )

    print("\nNo files were modified.")
    print("This is an analysis experiment; no feature set is declared final by this script.")

if __name__ == "__main__":
    main()