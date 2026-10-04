"""
LightX-IDS Phase 5 — Stage 1 False-Positive Characterization

READ-ONLY RESEARCH DIAGNOSTIC.
Does not modify dataset, Phase 4 files, labels, or saved models.

Uses the Phase 5 canonical controlled-temporal protocol:
TRAIN 1..89,000
VAL   89,001..90,000
TEST  90,001..100,000

Purpose:
Characterize where the current reproducible baseline's false positives
come from before designing a mitigation.
"""

from pathlib import Path
import sys
import time
import numpy as np
import pandas as pd

from sklearn.metrics import f1_score, confusion_matrix
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
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


def threshold_search(model, X, y):
    p = model.predict_proba(X)[:, 1]
    best_t, best_f1 = 0.50, -1
    for t in np.round(np.arange(0.10, 0.901, 0.05), 2):
        f = f1_score(y, (p >= t).astype(int), zero_division=0)
        if f > best_f1:
            best_t, best_f1 = float(t), float(f)
    return best_t, best_f1


def main():
    print("=" * 90)
    print("LIGHTX-IDS PHASE 5 — STAGE 1 FALSE-POSITIVE CHARACTERIZATION")
    print("=" * 90)

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
    Xtr = fg.transform(train)
    Xva = fg.transform(val)
    Xte = fg.transform(test)

    selector = FeatureSelector()
    Xtr, y_train = selector.split(Xtr.assign(label=y_train.values))
    Xva, y_val = selector.split(Xva.assign(label=y_val.values))
    Xte, y_test = selector.split(Xte.assign(label=y_test.values))

    num = [c for c in NUMERIC_COLUMNS if c in Xtr.columns]
    cat = [c for c in CATEGORICAL_COLUMNS if c in Xtr.columns]

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
    pipe.fit(Xtr, y_train)
    print(f"Training time: {time.perf_counter() - start:.3f}s")

    threshold, val_f1 = threshold_search(pipe, Xva, y_val)
    probs = pipe.predict_proba(Xte)[:, 1]
    preds = (probs >= threshold).astype(int)

    test_meta = test.reset_index(drop=True).copy()
    test_meta["probability"] = probs
    test_meta["prediction"] = preds
    test_meta["actual"] = y_test.reset_index(drop=True)

    normal = test_meta[test_meta["actual"] == 0].copy()
    fp = normal[normal["prediction"] == 1].copy()
    correct = normal[normal["prediction"] == 0].copy()

    print("\nBASELINE")
    print(f"Validation threshold : {threshold:.2f}")
    print(f"Validation F1        : {val_f1:.6f}")
    print(f"Test normal          : {len(normal):,}")
    print(f"False positives      : {len(fp):,}")
    print(f"FPR                  : {len(fp)/len(normal)*100:.2f}%")

    print("\nA) FP CONCENTRATION BY POSITION AFTER SLOW DRIFT")
    fp_positions = (fp["record_id"] - 91760).clip(lower=1)
    for n in [100, 500, 1000, 2000]:
        count = int((fp_positions <= n).sum())
        print(f"First {n:>4} normal records: {count:>4} FP ({count/n*100:6.2f}%)")
    remaining = len(fp) - int((fp_positions <= 2000).sum())
    rem_n = len(normal) - 2000
    print(f"Remaining {rem_n:>4} normal records: {remaining:>4} FP ({remaining/rem_n*100:6.2f}%)")

    print("\nB) FP BY DEVICE")
    dev = normal.groupby("device_id").agg(
        total=("actual", "size"),
        fp=("prediction", "sum"),
    )
    dev["fpr_pct"] = dev["fp"] / dev["total"] * 100
    print(dev.sort_values(["fpr_pct", "fp"], ascending=False).to_string())

    print("\nC) FP BY SENSOR TYPE")
    st = normal.groupby("sensor_type").agg(
        total=("actual", "size"),
        fp=("prediction", "sum"),
    )
    st["fpr_pct"] = st["fp"] / st["total"] * 100
    print(st.sort_values(["fpr_pct", "fp"], ascending=False).to_string())

    print("\nD) PROBABILITY DISTRIBUTION")
    for name, s in [
        ("Correct normal", correct["probability"]),
        ("False positive", fp["probability"]),
    ]:
        if len(s):
            print(
                f"{name:16s} n={len(s):4d} "
                f"mean={s.mean():.6f} median={s.median():.6f} "
                f"p90={s.quantile(.90):.6f} p99={s.quantile(.99):.6f} "
                f"max={s.max():.6f}"
            )

    print("\nE) HIGHEST-CONFIDENCE FALSE POSITIVES")
    cols = [c for c in [
        "record_id", "device_id", "sensor_type", "value",
        "time_delta", "rolling_time_delta_5",
        "rolling_time_delta_std_5", "global_time_delta",
        "rolling_global_td_10", "rolling_global_td_std_10",
        "packet_rate_10", "device_seq_gap", "seq_gap_dev",
        "rolling_seq_std_5", "plant_duplicate_ratio_19",
        "rolling_std_5", "rolling_range_5",
        "device_mean_deviation", "z_score", "stability_anomaly",
        "probability"
    ] if c in fp.columns]
    print(fp.sort_values("probability", ascending=False)[cols].head(25).to_string(index=False))

    print("\nF) FP VS CORRECT-NORMAL FEATURE MEANS")
    candidates = [
        "time_delta", "rolling_time_delta_5", "rolling_time_delta_std_5",
        "global_time_delta", "rolling_global_td_10",
        "rolling_global_td_std_10", "packet_rate_10",
        "device_seq_gap", "seq_gap_dev", "rolling_seq_std_5",
        "plant_duplicate_ratio_19", "rolling_std_5", "rolling_range_5",
        "device_mean_deviation", "z_score", "rel_volatility",
        "stability_anomaly", "value_change", "abs_value_change",
    ]
    rows = []
    for c in candidates:
        if c in fp.columns:
            a = correct[c].astype(float)
            b = fp[c].astype(float)
            rows.append((c, a.mean(), b.mean(), b.mean()-a.mean()))
    comp = pd.DataFrame(rows, columns=["feature","correct_normal_mean","fp_mean","difference"])
    print(comp.reindex(comp["difference"].abs().sort_values(ascending=False).index).to_string(index=False))

    print("\nG) FP TIMELINE")
    print(
        fp[["record_id","device_id","sensor_type","probability"]]
        .sort_values("record_id")
        .head(50)
        .to_string(index=False)
    )

    print("\n" + "=" * 90)
    print("STAGE 1 COMPLETE — READ-ONLY DIAGNOSTIC")
    print("=" * 90)
    print("No dataset, labels, Phase 4 files, or saved models were modified.")


if __name__ == "__main__":
    main()