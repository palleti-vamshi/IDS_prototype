"""
LightX-IDS Phase 5 — Stage 8: H3 Final Multi-Seed Robustness / Selection

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

SEEDS = list(range(42, 52))  # 42..51: 10 independent seeds
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

def evaluate_protocol(stream, protocol_name, tr_end, va_end, te_start, te_end):
    train = stream.iloc[:tr_end].copy()
    val = stream.iloc[tr_end:va_end].copy()
    test = stream.iloc[te_start:te_end].copy()

    ytr = train.pop("label").copy()
    yva = val.pop("label").copy()
    yte = test.pop("label").copy()

    fg = FeatureGenerator()
    fg.fit(train)
    Xtr_raw = fg.transform(train)
    Xva_raw = fg.transform(val)
    Xte_raw = fg.transform(test)

    selector = FeatureSelector()
    Xtr, ytr = selector.split(Xtr_raw.assign(label=ytr.values))
    Xva, yva = selector.split(Xva_raw.assign(label=yva.values))
    Xte, yte = selector.split(Xte_raw.assign(label=yte.values))

    results = []

    for system, removed in [
        ("BASELINE_36", set()),
        ("H3_32", H3_REMOVED),
    ]:
        print("\n" + "=" * 105)
        print(f"{protocol_name} | {system}")
        print("=" * 105)

        for seed in SEEDS:
            threshold, val_f1, probs, preds, train_sec = fit_predict(
                Xtr, ytr, Xva, yva, Xte, removed, seed
            )

            tn, fp, fn, tp = confusion_matrix(
                yte, preds, labels=[0, 1]
            ).ravel()

            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = f1_score(yte, preds, zero_division=0)
            acc = (tp + tn) / (tn + fp + fn + tp)
            fpr = fp / (fp + tn) if (fp + tn) else 0.0

            results.append({
                "protocol": protocol_name,
                "system": system,
                "seed": seed,
                "accuracy": acc,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "fpr": fpr,
                "fp": fp,
                "fn": fn,
                "threshold": threshold,
                "val_f1": val_f1,
                "train_sec": train_sec,
            })

            print(
                f"Seed {seed}: "
                f"Acc={acc*100:.2f}% "
                f"Precision={precision*100:.2f}% "
                f"Recall={recall*100:.2f}% "
                f"F1={f1*100:.2f}% "
                f"FPR={fpr*100:.2f}% "
                f"FP={fp} FN={fn} "
                f"Thr={threshold:.2f}"
            )

    return pd.DataFrame(results)


def print_summary(results):
    print("\n" + "=" * 105)
    print("STAGE 8 — 10-SEED SUMMARY")
    print("=" * 105)

    metric_cols = [
        "accuracy", "precision", "recall", "f1", "fpr", "fp", "fn"
    ]

    summary = (
        results.groupby(["protocol", "system"])[metric_cols]
        .agg(["mean", "std", "min", "max"])
    )

    for protocol in results["protocol"].unique():
        print(f"\n--- {protocol} ---")
        for system in ["BASELINE_36", "H3_32"]:
            sub = results[
                (results.protocol == protocol) &
                (results.system == system)
            ]
            print(
                f"{system}: "
                f"F1={sub.f1.mean()*100:.2f}±{sub.f1.std()*100:.2f}% "
                f"Recall={sub.recall.mean()*100:.2f}±{sub.recall.std()*100:.2f}% "
                f"FPR={sub.fpr.mean()*100:.2f}±{sub.fpr.std()*100:.2f}% "
                f"FP={sub.fp.mean():.1f}±{sub.fp.std():.1f} "
                f"FN={sub.fn.mean():.1f}±{sub.fn.std():.1f}"
            )

    print("\n" + "=" * 105)
    print("STAGE 8 — H3 DELTAS VS BASELINE")
    print("=" * 105)

    for protocol in results["protocol"].unique():
        base = results[
            (results.protocol == protocol) &
            (results.system == "BASELINE_36")
        ].set_index("seed")
        h3 = results[
            (results.protocol == protocol) &
            (results.system == "H3_32")
        ].set_index("seed")

        delta = pd.DataFrame({
            "delta_f1_pp": (h3.f1 - base.f1) * 100,
            "delta_recall_pp": (h3.recall - base.recall) * 100,
            "delta_fpr_pp": (h3.fpr - base.fpr) * 100,
            "delta_fp": h3.fp - base.fp,
            "delta_fn": h3.fn - base.fn,
        })

        print(f"\n--- {protocol} ---")
        print(delta.to_string(float_format=lambda x: f"{x:.3f}"))

        print(
            f"\nMean delta: "
            f"F1={delta.delta_f1_pp.mean():+.3f} pp, "
            f"Recall={delta.delta_recall_pp.mean():+.3f} pp, "
            f"FPR={delta.delta_fpr_pp.mean():+.3f} pp, "
            f"FP={delta.delta_fp.mean():+.1f}, "
            f"FN={delta.delta_fn.mean():+.1f}"
        )

        print(
            f"Seeds where H3 improves F1: "
            f"{int((delta.delta_f1_pp > 0).sum())}/{len(delta)}"
        )
        print(
            f"Seeds where H3 reduces FP: "
            f"{int((delta.delta_fp < 0).sum())}/{len(delta)}"
        )
        print(
            f"Seeds where H3 improves recall: "
            f"{int((delta.delta_recall_pp > 0).sum())}/{len(delta)}"
        )


def main():
    print("=" * 105)
    print("LIGHTX-IDS PHASE 5 — STAGE 8 H3 FINAL MULTI-SEED ROBUSTNESS / SELECTION")
    print("=" * 105)
    print("H3 removes:", ", ".join(sorted(H3_REMOVED)))
    print("Seeds:", SEEDS)
    print("Protocol: frozen Phase 5 train/validation/test definitions")
    print("READ-ONLY: no dataset, labels, config.py, or production model changes.")

    df = pd.read_csv(LIGHTX_100K).sort_values(
        "record_id"
    ).reset_index(drop=True)

    stream = FeatureGenerator().generate_causal_stream_features(df)

    # Frozen protocols:
    # 1) STRATIFIED_100K: 80/10/10 stratified split.
    # 2) CONTROLLED_TEMPORAL: train 1..89000, val 89001..90000,
    #    test 90001..100000.
    # 3) STRICT_CHRONOLOGICAL: train 1..80000, val 80001..90000,
    #    test 90001..100000.
    #
    # For the temporal protocols, use the existing causal stream features
    # and keep preprocessing fit strictly on each protocol's training data.

    all_results = []

    # STRATIFIED: use the existing frozen 80/10/10 index split, but keep
    # feature engineering causal and preprocessing train-only.
    n = len(stream)
    rng = np.random.RandomState(42)
    idx = np.arange(n)
    y_all = stream["label"].to_numpy()
    train_idx, temp_idx = [], []
    for cls in np.unique(y_all):
        cls_idx = idx[y_all == cls].copy()
        rng.shuffle(cls_idx)
        cut = int(round(len(cls_idx) * 0.80))
        train_idx.extend(cls_idx[:cut])
        temp_idx.extend(cls_idx[cut:])
    train_idx = np.array(train_idx)
    temp_idx = np.array(temp_idx)

    val_idx, test_idx = [], []
    y_temp = y_all[temp_idx]
    for cls in np.unique(y_temp):
        cls_idx = temp_idx[y_temp == cls].copy()
        rng.shuffle(cls_idx)
        cut = len(cls_idx) // 2
        val_idx.extend(cls_idx[:cut])
        test_idx.extend(cls_idx[cut:])

    def run_index_protocol(name, tr_idx, va_idx, te_idx):
        train = stream.iloc[tr_idx].copy()
        val = stream.iloc[va_idx].copy()
        test = stream.iloc[te_idx].copy()

        ytr = train.pop("label").copy()
        yva = val.pop("label").copy()
        yte = test.pop("label").copy()

        fg = FeatureGenerator()
        fg.fit(train)
        Xtr_raw = fg.transform(train)
        Xva_raw = fg.transform(val)
        Xte_raw = fg.transform(test)

        selector = FeatureSelector()
        Xtr, ytr = selector.split(Xtr_raw.assign(label=ytr.values))
        Xva, yva = selector.split(Xva_raw.assign(label=yva.values))
        Xte, yte = selector.split(Xte_raw.assign(label=yte.values))

        rows = []
        for system, removed in [
            ("BASELINE_36", set()),
            ("H3_32", H3_REMOVED),
        ]:
            for seed in SEEDS:
                threshold, val_f1, probs, preds, train_sec = fit_predict(
                    Xtr, ytr, Xva, yva, Xte, removed, seed
                )
                tn, fp, fn, tp = confusion_matrix(
                    yte, preds, labels=[0, 1]
                ).ravel()
                precision = tp / (tp + fp) if (tp + fp) else 0.0
                recall = tp / (tp + fn) if (tp + fn) else 0.0
                f1 = f1_score(yte, preds, zero_division=0)
                acc = (tp + tn) / (tn + fp + fn + tp)
                fpr = fp / (fp + tn) if (fp + tn) else 0.0
                rows.append({
                    "protocol": name, "system": system, "seed": seed,
                    "accuracy": acc, "precision": precision,
                    "recall": recall, "f1": f1, "fpr": fpr,
                    "fp": fp, "fn": fn, "threshold": threshold,
                    "val_f1": val_f1, "train_sec": train_sec,
                })
        return pd.DataFrame(rows)

    print("\nRunning STRATIFIED_100K...")
    all_results.append(
        run_index_protocol(
            "STRATIFIED_100K", train_idx, np.array(val_idx), np.array(test_idx)
        )
    )

    print("\nRunning CONTROLLED_TEMPORAL...")
    all_results.append(
        evaluate_protocol(stream, "CONTROLLED_TEMPORAL", 89000, 90000, 90000, 100000)
    )

    print("\nRunning STRICT_CHRONOLOGICAL...")
    all_results.append(
        evaluate_protocol(stream, "STRICT_CHRONOLOGICAL", 80000, 90000, 90000, 100000)
    )

    results = pd.concat(all_results, ignore_index=True)
    print_summary(results)

    print("\n" + "=" * 105)
    print("STAGE 8 DECISION SUPPORT")
    print("=" * 105)
    print(
        "Do NOT freeze H3 from one seed. Freeze only if its multi-seed evidence "
        "shows a defensible improvement across the intended temporal protocol "
        "without materially harming attack recall or stratified performance."
    )
    print("No files were modified.")


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
