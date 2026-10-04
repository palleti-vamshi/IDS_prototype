"""
LightX-IDS Phase 5 — Stage 7: H3 Controlled-Temporal Seed / FP Stability

Purpose:
Explain why H3's controlled-temporal FP reduction varies strongly by seed.

This is READ-ONLY:
- no dataset changes
- no label changes
- no config.py changes
- no model artifacts written

Protocol:
  Controlled temporal only:
    train 1..89000
    validation 89001..90000
    test 90001..100000

Seeds:
  42, 43, 44, 45, 46

Systems:
  BASELINE_36
  H3_32

For every seed/system:
  - validation-selected threshold
  - total FP/FN
  - FP concentration in early post-transition windows
  - FP confidence distribution
  - top FP devices/sensor types
  - FP probability agreement/disagreement across seeds

The final section compares H3 predictions across seeds on the SAME test rows,
which helps distinguish a true feature effect from random tree-selection effects.
"""

from pathlib import Path
import sys
import time
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import f1_score, confusion_matrix
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ml.config import LIGHTX_100K, NUMERIC_COLUMNS, CATEGORICAL_COLUMNS
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.ml.feature_engineering.feature_selector import FeatureSelector

SEEDS = [42, 43, 44, 45, 46]
H3_REMOVED = {
    "value_change",
    "abs_value_change",
    "rolling_range_5",
    "rolling_mean_10",
}

XGB_BASE = dict(
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
        score = f1_score(y, (p >= t).astype(int), zero_division=0)
        if score > best_f1:
            best_t, best_f1 = float(t), float(score)
    return best_t, best_f1

def prepare_split(stream):
    tr_idx = np.arange(0, 89000)
    va_idx = np.arange(89000, 90000)
    te_idx = np.arange(90000, 100000)

    train = stream.iloc[tr_idx].copy()
    val = stream.iloc[va_idx].copy()
    test = stream.iloc[te_idx].copy()

    # Keep a metadata copy WITH labels for FP/window diagnostics.
    test_meta = test.copy()

    ytr = train["label"].copy()
    yva = val["label"].copy()
    yte = test["label"].copy()

    train = train.drop(columns=["label"])
    val = val.drop(columns=["label"])
    test = test.drop(columns=["label"])

    fg = FeatureGenerator()
    fg.fit(train)

    Xtr_raw = fg.transform(train)
    Xva_raw = fg.transform(val)
    Xte_raw = fg.transform(test)

    selector = FeatureSelector()
    Xtr, ytr = selector.split(Xtr_raw.assign(label=ytr.values))
    Xva, yva = selector.split(Xva_raw.assign(label=yva.values))
    Xte, yte = selector.split(Xte_raw.assign(label=yte.values))

    return train, val, test_meta, Xtr, ytr, Xva, yva, Xte, yte

def fit_predict(Xtr, ytr, Xva, yva, Xte, removed, seed):
    num = [
        c for c in NUMERIC_COLUMNS
        if c in Xtr.columns and c not in removed
    ]
    cat = [c for c in CATEGORICAL_COLUMNS if c in Xtr.columns]

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

    params = XGB_BASE.copy()
    params["random_state"] = seed

    pipe = Pipeline([
        ("preprocess", pre),
        ("model", XGBClassifier(**params)),
    ])

    start = time.perf_counter()
    pipe.fit(Xtr[num + cat], ytr)
    train_sec = time.perf_counter() - start

    threshold, val_f1 = threshold_search(pipe, Xva[num + cat], yva)
    probs = pipe.predict_proba(Xte[num + cat])[:, 1]
    preds = (probs >= threshold).astype(int)

    return threshold, val_f1, probs, preds, train_sec

def window_stats(test_meta, probs, preds, threshold):
    normal = test_meta["label"].to_numpy() == 0
    fp_mask = normal & (preds == 1)

    record_ids = test_meta["record_id"].to_numpy()
    first_id = int(record_ids[0])

    offsets = record_ids - first_id

    windows = [
        ("first_100", 0, 100),
        ("first_500", 0, 500),
        ("first_1000", 0, 1000),
        ("first_2000", 0, 2000),
        ("remaining", 2000, len(test_meta)),
    ]

    rows = []
    for name, lo, hi in windows:
        m = fp_mask & (offsets >= lo) & (offsets < hi)
        normal_m = normal & (offsets >= lo) & (offsets < hi)
        n = int(normal_m.sum())
        fp = int(m.sum())
        rows.append({
            "window": name,
            "normal_n": n,
            "fp": fp,
            "fpr": fp / n if n else 0.0,
            "fp_share": fp / fp_mask.sum() if fp_mask.sum() else 0.0,
        })
    return rows

def main():
    print("=" * 105)
    print("LIGHTX-IDS PHASE 5 — STAGE 7 H3 CONTROLLED-TEMPORAL FP STABILITY")
    print("=" * 105)
    print("H3 removes:", ", ".join(sorted(H3_REMOVED)))
    print("Seeds:", SEEDS)

    df = pd.read_csv(LIGHTX_100K).sort_values(
        "record_id"
    ).reset_index(drop=True)

    stream_fg = FeatureGenerator()
    stream = stream_fg.generate_causal_stream_features(df)

    (
        train_meta, val_meta, test_meta,
        Xtr, ytr, Xva, yva, Xte, yte
    ) = prepare_split(stream)

    test_meta = test_meta.reset_index(drop=True)
    all_predictions = {
        "BASELINE_36": {},
        "H3_32": {},
    }
    all_windows = []

    for system, removed in [
        ("BASELINE_36", set()),
        ("H3_32", H3_REMOVED),
    ]:
        print("\n" + "=" * 105)
        print(system)
        print("=" * 105)

        for seed in SEEDS:
            threshold, val_f1, probs, preds, train_sec = fit_predict(
                Xtr, ytr, Xva, yva, Xte, removed, seed
            )

            tn, fp, fn, tp = confusion_matrix(
                yte, preds, labels=[0, 1]
            ).ravel()

            print(
                f"Seed {seed}: "
                f"F1={f1_score(yte, preds)*100:.2f}%  "
                f"FP={fp} FN={fn} "
                f"Thr={threshold:.2f} "
                f"ValF1={val_f1*100:.2f}%"
            )

            all_predictions[system][seed] = {
                "probs": probs,
                "preds": preds,
                "threshold": threshold,
            }

            # FP window concentration
            for row in window_stats(
                test_meta, probs, preds, threshold
            ):
                row.update({
                    "system": system,
                    "seed": seed,
                })
                all_windows.append(row)

            # Detailed FP metadata
            fp_mask = (
                (test_meta["label"].to_numpy() == 0) &
                (preds == 1)
            )
            fp_df = test_meta.loc[fp_mask].copy()
            fp_df["probability"] = probs[fp_mask]
            fp_df["offset"] = (
                fp_df["record_id"].to_numpy() -
                test_meta["record_id"].iloc[0]
            )

            if len(fp_df):
                print("  Top FP devices:")
                print(
                    fp_df["device_id"]
                    .value_counts()
                    .head(5)
                    .to_string()
                )
                print("  Top FP sensor types:")
                print(
                    fp_df["sensor_type"]
                    .value_counts()
                    .head(5)
                    .to_string()
                )
                print(
                    "  FP probability: "
                    f"mean={fp_df.probability.mean():.4f} "
                    f"median={fp_df.probability.median():.4f} "
                    f"p90={fp_df.probability.quantile(.90):.4f} "
                    f"max={fp_df.probability.max():.4f}"
                )
                print(
                    f"  First FP record: {int(fp_df.record_id.min())}"
                )

    print("\n" + "=" * 105)
    print("EARLY POST-TRANSITION FP CONCENTRATION")
    print("=" * 105)

    windows_df = pd.DataFrame(all_windows)
    for system in ["BASELINE_36", "H3_32"]:
        print(f"\n--- {system} ---")
        print(
            windows_df[windows_df.system == system]
            .pivot(index="seed", columns="window", values="fp")
            .to_string()
        )
        print("\nFPR by window:")
        print(
            windows_df[windows_df.system == system]
            .pivot(index="seed", columns="window", values="fpr")
            .to_string(float_format=lambda x: f"{x*100:.2f}%")
        )

    print("\n" + "=" * 105)
    print("CROSS-SEED PREDICTION STABILITY — H3")
    print("=" * 105)

    h3_probs = np.column_stack([
        all_predictions["H3_32"][s]["probs"] for s in SEEDS
    ])
    h3_preds = np.column_stack([
        all_predictions["H3_32"][s]["preds"] for s in SEEDS
    ])

    normal_mask = test_meta["label"].to_numpy() == 0
    attack_mask = ~normal_mask

    # Probability variability on the same test row across five independently
    # seeded models.
    row_prob_std = h3_probs.std(axis=1)
    print(
        f"H3 probability std across seeds: "
        f"mean={row_prob_std.mean():.4f} "
        f"median={np.median(row_prob_std):.4f} "
        f"p90={np.quantile(row_prob_std,.90):.4f} "
        f"p99={np.quantile(row_prob_std,.99):.4f} "
        f"max={row_prob_std.max():.4f}"
    )

    pred_disagreement = h3_preds.std(axis=1)
    print(
        "H3 binary prediction disagreement: "
        f"{np.mean(pred_disagreement > 0):.2%} of all test rows"
    )
    print(
        "H3 normal-row disagreement: "
        f"{np.mean(pred_disagreement[normal_mask] > 0):.2%}"
    )
    print(
        "H3 attack-row disagreement: "
        f"{np.mean(pred_disagreement[attack_mask] > 0):.2%}"
    )

    # How many seeds call each normal row an FP?
    normal_fp_votes = h3_preds[normal_mask].sum(axis=1)
    print("\nNormal rows by number of H3 FP votes (0..5):")
    print(
        pd.Series(normal_fp_votes)
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\n" + "=" * 105)
    print("MOST CONSISTENT H3 FALSE-POSITIVE ROWS")
    print("=" * 105)

    normal_positions = np.where(normal_mask)[0]
    vote5 = normal_fp_votes == len(SEEDS)

    if vote5.any():
        consistent = test_meta.iloc[
            normal_positions[vote5]
        ].copy()
        consistent["fp_votes"] = 5
        consistent["mean_probability"] = h3_probs[
            normal_positions[vote5]
        ].mean(axis=1)
        consistent["prob_std"] = h3_probs[
            normal_positions[vote5]
        ].std(axis=1)

        cols = [
            "record_id", "device_id", "sensor_type",
            "attack_type", "fp_votes",
            "mean_probability", "prob_std"
        ]
        print(
            consistent[cols]
            .sort_values("mean_probability", ascending=False)
            .head(25)
            .to_string(index=False)
        )
    else:
        print("No normal test row was predicted positive by all five H3 seeds.")

    print("\n" + "=" * 105)
    print("STAGE 7 INTERPRETATION SUPPORT")
    print("=" * 105)
    print(
        "Use this output to determine whether seed sensitivity is concentrated "
        "in transition windows, specific devices/sensors, or unstable model "
        "probabilities. No feature set is changed by this script."
    )
    print("No files were modified.")

if __name__ == "__main__":
    main()
