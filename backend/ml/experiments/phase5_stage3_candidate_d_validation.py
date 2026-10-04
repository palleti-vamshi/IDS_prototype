"""
LightX-IDS Phase 5 — Stage 3 Candidate-D Validation

Candidate D:
Remove the physical-dynamics feature group identified by Stage 2.

Two systems:
  BASELINE: canonical 36 selected ML features
  CANDIDATE_D: baseline minus physical-dynamics numeric features

Three evaluation protocols:
  1) Stratified 100K benchmark: 80/10/10 stratified, seed 42
  2) Controlled temporal: train 1..89000, val 89001..90000, test 90001..100000
  3) Strict chronological: train 1..80000, val 80001..90000,
     test 90001..100000

Important:
- Dataset is never modified.
- Labels are never modified.
- Candidate D changes only the selected feature group.
- Threshold is selected on validation only.
- Strict test is untouched.
- Historical Phase 4.1 benchmark remains a historical reference; it is not
  overwritten by this experiment.
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

SEED = 42
ATTACK_NAME = "Slow Drift Attack"

PHYSICAL_DYNAMICS = {
    "value_change", "abs_value_change", "value_accel",
    "rolling_mean_3", "rolling_std_3",
    "rolling_mean_5", "rolling_std_5",
    "rolling_mean_10", "rolling_std_10",
    "rolling_mean", "rolling_std",
    "rolling_max", "rolling_min",
    "rolling_range_5", "percentage_change",
}

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

def fit_system(X_train, y_train, X_val, y_val, X_test, y_test, removed):
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

    model = XGBClassifier(**XGB_PARAMS)
    pipe = Pipeline([("preprocess", pre), ("model", model)])

    start = time.perf_counter()
    pipe.fit(X_train[num + cat], y_train)
    train_time = time.perf_counter() - start

    threshold, val_f1 = threshold_search(pipe, X_val[num + cat], y_val)

    probs = pipe.predict_proba(X_test[num + cat])[:, 1]
    preds = (probs >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_test, preds, labels=[0, 1]).ravel()

    metrics = {
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
        "train_sec": train_time,
        "features": len(num) + len(cat),
    }

    return pipe, metrics, probs

def prepare_raw_features(stream, train_idx, val_idx, test_idx):
    train = stream.iloc[train_idx].copy()
    val = stream.iloc[val_idx].copy()
    test = stream.iloc[test_idx].copy()

    y_train = train.pop("label")
    y_val = val.pop("label")
    y_test = test.pop("label")

    fg = FeatureGenerator()
    fg.fit(train)

    X_train = fg.transform(train)
    X_val = fg.transform(val)
    X_test = fg.transform(test)

    selector = FeatureSelector()
    X_train, y_train = selector.split(X_train.assign(label=y_train.values))
    X_val, y_val = selector.split(X_val.assign(label=y_val.values))
    X_test, y_test = selector.split(X_test.assign(label=y_test.values))

    return train, val, test, X_train, y_train, X_val, y_val, X_test, y_test

def print_result(protocol, name, metrics):
    print(f"\n{name}")
    print(f"Features  : {metrics['features']}")
    print(f"Threshold : {metrics['threshold']:.2f}")
    print(f"Accuracy  : {metrics['accuracy']*100:.2f}%")
    print(f"Precision : {metrics['precision']*100:.2f}%")
    print(f"Recall    : {metrics['recall']*100:.2f}%")
    print(f"F1        : {metrics['f1']*100:.2f}%")
    print(f"ROC-AUC   : {metrics['roc_auc']:.5f}")
    print(f"PR-AUC    : {metrics['pr_auc']:.5f}")
    print(f"FPR       : {metrics['fpr']*100:.2f}%")
    print(f"FNR       : {metrics['fnr']*100:.2f}%")
    print(f"TN={metrics['tn']} FP={metrics['fp']} FN={metrics['fn']} TP={metrics['tp']}")
    print(f"Training  : {metrics['train_sec']:.3f}s")

def main():
    print("=" * 90)
    print("LIGHTX-IDS PHASE 5 — STAGE 3 CANDIDATE-D VALIDATION")
    print("=" * 90)

    df = pd.read_csv(LIGHTX_100K).sort_values("record_id").reset_index(drop=True)
    fg0 = FeatureGenerator()
    stream = fg0.generate_causal_stream_features(df)

    protocols = {
        "STRATIFIED_100K": None,
        "CONTROLLED_TEMPORAL": (np.arange(0, 89000), np.arange(89000, 90000), np.arange(90000, 100000)),
        "STRICT_CHRONOLOGICAL": (np.arange(0, 80000), np.arange(80000, 90000), np.arange(90000, 100000)),
    }

    all_rows = []

    # Stratified split is performed on raw stream rows with seed 42.
    rng_train, rng_test = train_test_split(
        np.arange(len(stream)),
        test_size=0.20,
        stratify=stream["label"],
        random_state=SEED,
    )
    rng_val, rng_test = train_test_split(
        rng_test,
        test_size=0.50,
        stratify=stream.iloc[rng_test]["label"],
        random_state=SEED,
    )
    protocols["STRATIFIED_100K"] = (rng_train, rng_val, rng_test)

    for protocol, indices in protocols.items():
        print("\n" + "=" * 90)
        print(protocol)
        print("=" * 90)

        tr_idx, va_idx, te_idx = indices
        train_meta, val_meta, test_meta, Xtr, ytr, Xva, yva, Xte, yte = prepare_raw_features(
            stream, tr_idx, va_idx, te_idx
        )

        for name, removed in [
            ("BASELINE", set()),
            ("CANDIDATE_D_NO_PHYSICAL_DYNAMICS", PHYSICAL_DYNAMICS),
        ]:
            _, metrics, probs = fit_system(Xtr, ytr, Xva, yva, Xte, yte, removed)

            # Slow Drift recall when the attack exists in this test.
            attack_mask = test_meta["attack_type"].eq(ATTACK_NAME).to_numpy()
            if attack_mask.any():
                slow_recall = float(np.mean(probs[attack_mask] >= metrics["threshold"]))
            else:
                slow_recall = float("nan")

            metrics["slow_drift_recall"] = slow_recall
            metrics["protocol"] = protocol
            metrics["model"] = name
            all_rows.append(metrics)
            print_result(protocol, name, metrics)
            if not np.isnan(slow_recall):
                print(f"Slow Drift recall: {slow_recall*100:.2f}%")
            else:
                print("Slow Drift recall: N/A (no Slow Drift in this test split)")

    out = pd.DataFrame(all_rows)

    print("\n" + "=" * 90)
    print("CANDIDATE D COMPARISON SUMMARY")
    print("=" * 90)

    cols = [
        "protocol","model","features","threshold",
        "accuracy","precision","recall","f1",
        "fpr","fnr","fp","fn","slow_drift_recall"
    ]
    print(out[cols].to_string(index=False))

    print("\nNo files were modified.")
    print("This experiment does NOT declare Candidate D final; it only validates it across protocols.")

if __name__ == "__main__":
    main()
