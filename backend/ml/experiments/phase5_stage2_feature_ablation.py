"""
LightX-IDS Phase 5 — Stage 2 Feature-Group Ablation

READ-ONLY EXPERIMENT.
Uses the canonical Phase 5 controlled-temporal split and frozen
historical XGBoost hyperparameters. Only the feature group is changed.

Groups:
A_FULL
B_NO_TIMING
C_NO_COMMUNICATION
D_NO_PHYSICAL_DYNAMICS
E_NO_PLANT_WIDE
F_NO_SENSOR_AWARE

For each model, reports:
accuracy, precision, recall, F1, ROC-AUC, PR-AUC, FPR, FNR,
threshold, TN/FP/FN/TP, and Slow Drift recall.

No dataset or Phase 4 source files are modified.
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

TRAIN_END = 89000
VAL_END = 90000
ATTACK_NAME = "Slow Drift Attack"

GROUPS = {
    "A_FULL_40": set(),
    "B_NO_TIMING": {
        "time_delta", "rolling_time_delta_5",
        "rolling_time_delta_std_5", "is_negative_time_delta",
        "global_time_delta", "rolling_global_td_10",
        "rolling_global_td_std_10", "packet_rate_10",
    },
    "C_NO_COMMUNICATION": {
        "device_seq_gap", "seq_gap_dev", "rolling_seq_std_5",
    },
    "D_NO_PHYSICAL_DYNAMICS": {
        "value_change", "abs_value_change", "value_accel",
        "rolling_mean_3", "rolling_std_3",
        "rolling_mean_5", "rolling_std_5",
        "rolling_mean_10", "rolling_std_10",
        "rolling_mean", "rolling_std",
        "rolling_max", "rolling_min", "rolling_range_5",
        "percentage_change",
    },
    "E_NO_PLANT_WIDE": {
        "plant_duplicate_ratio_19",
    },
    "F_NO_SENSOR_AWARE": {
        "device_mean_deviation", "z_score",
        "rel_volatility", "stability_anomaly",
    },
}

def select_threshold(model, X, y):
    p = model.predict_proba(X)[:, 1]
    best_t, best_f1 = 0.50, -1
    for t in np.round(np.arange(0.10, 0.901, 0.05), 2):
        f = f1_score(y, (p >= t).astype(int), zero_division=0)
        if f > best_f1:
            best_t, best_f1 = float(t), float(f)
    return best_t, best_f1

def evaluate(model, X, y, threshold):
    p = model.predict_proba(X)[:, 1]
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    return {
        "accuracy": accuracy_score(y,pred),
        "precision": precision_score(y,pred,zero_division=0),
        "recall": recall_score(y,pred,zero_division=0),
        "f1": f1_score(y,pred,zero_division=0),
        "roc_auc": roc_auc_score(y,p),
        "pr_auc": average_precision_score(y,p),
        "fpr": fp/(fp+tn) if fp+tn else 0,
        "fnr": fn/(fn+tp) if fn+tp else 0,
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }

def main():
    print("="*90)
    print("LIGHTX-IDS PHASE 5 — STAGE 2 FEATURE-GROUP ABLATION")
    print("="*90)

    df = pd.read_csv(LIGHTX_100K).sort_values("record_id").reset_index(drop=True)

    fg = FeatureGenerator()
    stream = fg.generate_causal_stream_features(df)

    train = stream.iloc[:TRAIN_END].copy()
    val = stream.iloc[TRAIN_END:VAL_END].copy()
    test = stream.iloc[VAL_END:].copy()

    y_train = train.pop("label")
    y_val = val.pop("label")
    y_test = test.pop("label")

    fg.fit(train)
    X_train = fg.transform(train)
    X_val = fg.transform(val)
    X_test = fg.transform(test)

    selector = FeatureSelector()
    X_train, y_train = selector.split(X_train.assign(label=y_train.values))
    X_val, y_val = selector.split(X_val.assign(label=y_val.values))
    X_test, y_test = selector.split(X_test.assign(label=y_test.values))

    base_num = [c for c in NUMERIC_COLUMNS if c in X_train.columns]
    base_cat = [c for c in CATEGORICAL_COLUMNS if c in X_train.columns]

    results = []

    for name, removed in GROUPS.items():
        num = [c for c in base_num if c not in removed]
        cat = base_cat[:]  # categorical features remain fixed

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

        model = XGBClassifier(
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
            random_state=42,
            n_jobs=-1,
        )

        pipe = Pipeline([("preprocess", pre), ("model", model)])

        start = time.perf_counter()
        pipe.fit(X_train[num+cat], y_train)
        train_time = time.perf_counter() - start

        threshold, val_f1 = select_threshold(pipe, X_val[num+cat], y_val)
        metrics = evaluate(pipe, X_test[num+cat], y_test, threshold)

        # Test Slow Drift recall separately.
        test_attack = test.copy()
        test_attack["actual"] = y_test.values
        attack_mask = test_attack["attack_type"].eq(ATTACK_NAME).to_numpy()
        attack_probs = pipe.predict_proba(X_test[num+cat])[:,1][attack_mask]
        attack_recall = float(np.mean(attack_probs >= threshold))

        row = {
            "group": name,
            "features": len(num)+len(cat),
            "threshold": threshold,
            "val_f1": val_f1,
            "train_sec": train_time,
            "slow_drift_recall": attack_recall,
            **metrics,
        }
        results.append(row)

        print(f"\n{name}")
        print(f"Features: {len(num)+len(cat)}")
        print(f"Threshold: {threshold:.2f}")
        print(f"Accuracy: {metrics['accuracy']*100:.2f}%")
        print(f"Precision: {metrics['precision']*100:.2f}%")
        print(f"Recall: {metrics['recall']*100:.2f}%")
        print(f"F1: {metrics['f1']*100:.2f}%")
        print(f"ROC-AUC: {metrics['roc_auc']:.5f}")
        print(f"PR-AUC: {metrics['pr_auc']:.5f}")
        print(f"FPR: {metrics['fpr']*100:.2f}%")
        print(f"FNR: {metrics['fnr']*100:.2f}%")
        print(f"TN={metrics['tn']} FP={metrics['fp']} FN={metrics['fn']} TP={metrics['tp']}")
        print(f"Slow Drift recall: {attack_recall*100:.2f}%")

    out = pd.DataFrame(results)
    print("\n" + "="*90)
    print("STAGE 2 SUMMARY")
    print("="*90)
    display_cols = [
        "group","features","threshold","accuracy","precision","recall","f1",
        "fpr","fnr","fp","fn","slow_drift_recall"
    ]
    print(out[display_cols].to_string(index=False))

    print("\nSTAGE 2 COMPLETE — READ-ONLY ABLATION")
    print("No dataset, labels, Phase 4 files, or saved models were modified.")

if __name__ == "__main__":
    main()
