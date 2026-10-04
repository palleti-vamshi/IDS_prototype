"""
LightX-IDS Controlled Slow Drift Temporal Experiment

RESEARCH / DIAGNOSTIC ONLY.

This script:
- DOES NOT modify the dataset
- DOES NOT modify Phase 4.1 code
- DOES NOT modify labels
- DOES NOT save trained models
- DOES NOT overwrite Phase 4.1 reports

Purpose:
Compare temporal performance when Slow Drift is:
1. completely unseen during training
2. partially seen during training

Controlled protocol:
    TRAIN: records 1..89000
    VAL:   records 89001..90000
    TEST:  records 90001..100000

This deliberately uses a non-standard split size because the
experiment is designed around the Slow Drift campaign boundary.
"""

from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)

# ---------------------------------------------------------------------
# Repository root / imports
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ml.config import (
    LIGHTX_100K,
    NUMERIC_COLUMNS,
    CATEGORICAL_COLUMNS,
)

from backend.ml.feature_engineering.feature_generator import (
    FeatureGenerator,
)

from backend.ml.feature_engineering.feature_selector import (
    FeatureSelector,
)

from backend.ml.preprocessing.transformer import (
    DatasetTransformer,
)

from backend.ml.preprocessing.pipeline import (
    MLPipeline,
)




# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

DATASET = LIGHTX_100K

TRAIN_END = 89000
VAL_END = 90000

ATTACK_NAME = "Slow Drift Attack"

THRESHOLD_MIN = 0.10
THRESHOLD_MAX = 0.90
THRESHOLD_STEP = 0.05


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def print_attack_distribution(name, frame):
    print(f"\n{name}")
    print("-" * 70)

    print(f"Rows: {len(frame):,}")

    distribution = (
        frame["attack_type"]
        .value_counts(dropna=False)
    )

    print(distribution.to_string())

    slow_count = (
        frame["attack_type"]
        .eq(ATTACK_NAME)
        .sum()
    )

    print(
        f"\nSlow Drift Attack samples: "
        f"{slow_count:,}"
    )


def optimize_threshold(
    pipeline,
    X_val,
    y_val,
):
    """
    Select threshold using validation F1 only.
    Test data is never used here.
    """

    probabilities = pipeline.predict_proba(
        X_val
    )[:, 1]

    thresholds = np.round(
        np.arange(
            THRESHOLD_MIN,
            THRESHOLD_MAX + 0.001,
            THRESHOLD_STEP,
        ),
        2,
    )

    best_threshold = 0.50
    best_f1 = -1.0

    rows = []

    for threshold in thresholds:

        predictions = (
            probabilities >= threshold
        ).astype(int)

        score = f1_score(
            y_val,
            predictions,
            zero_division=0,
        )

        rows.append(
            (
                float(threshold),
                float(score),
            )
        )

        if score > best_f1:

            best_f1 = float(score)
            best_threshold = float(threshold)

    return (
        best_threshold,
        best_f1,
        probabilities,
        rows,
    )


def evaluate_test(
    pipeline,
    X_test,
    y_test,
    threshold,
):

    probabilities = pipeline.predict_proba(
        X_test
    )[:, 1]

    predictions = (
        probabilities >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    ).ravel()

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities,
    )

    pr_auc = average_precision_score(
        y_test,
        probabilities,
    )

    fpr = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0.0
    )

    fnr = (
        fn / (fn + tp)
        if (fn + tp) > 0
        else 0.0
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "fpr": fpr,
        "fnr": fnr,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "probabilities": probabilities,
        "predictions": predictions,
    }


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    print("=" * 90)
    print("LIGHTX-IDS PHASE 5 CANONICAL CONTROLLED TEMPORAL BASELINE")
    print("=" * 90)

    print(f"\nDataset: {DATASET}")
    print(f"Train: records 1..{TRAIN_END:,}")
    print(
        f"Validation: records "
        f"{TRAIN_END + 1:,}..{VAL_END:,}"
    )
    print(
        f"Test: records "
        f"{VAL_END + 1:,}..100,000"
    )

    print(
        "\nIMPORTANT:"
        "\nThis is the Phase 5 canonical baseline protocol."
        "\nPhase 4.1 remains unchanged."
        "\nHistorical target: 97.63% accuracy / 93.68% F1 / 233 FP."
    )

    # -----------------------------------------------------------------
    # Load dataset
    # -----------------------------------------------------------------

    print("\n[1] Loading dataset...")

    df = pd.read_csv(DATASET)

    df = df.sort_values(
        "record_id"
    ).reset_index(drop=True)

    print(
        f"Loaded {len(df):,} records."
    )

    # -----------------------------------------------------------------
    # Generate causal stream features
    # -----------------------------------------------------------------

    print(
        "\n[2] Generating causal stream features..."
    )

    feature_generator = FeatureGenerator()

    df_stream = (
        feature_generator
        .generate_causal_stream_features(df)
    )

    print(
        f"Generated stream features: "
        f"{len(df_stream.columns)} columns."
    )

    # -----------------------------------------------------------------
    # Controlled chronological split
    # -----------------------------------------------------------------

    print(
        "\n[3] Creating controlled temporal split..."
    )

    train_df = df_stream.iloc[
        :TRAIN_END
    ].copy()

    val_df = df_stream.iloc[
        TRAIN_END:VAL_END
    ].copy()

    test_df = df_stream.iloc[
        VAL_END:
    ].copy()

    print_attack_distribution(
        "TRAIN",
        train_df,
    )

    print_attack_distribution(
        "VALIDATION",
        val_df,
    )

    print_attack_distribution(
        "TEST",
        test_df,
    )

    # -----------------------------------------------------------------
    # Extract labels
    # -----------------------------------------------------------------

    y_train = train_df["label"].copy()
    y_val = val_df["label"].copy()
    y_test = test_df["label"].copy()

    X_train_raw = train_df.drop(
        columns=["label"]
    )

    X_val_raw = val_df.drop(
        columns=["label"]
    )

    X_test_raw = test_df.drop(
        columns=["label"]
    )

    # -----------------------------------------------------------------
    # Fit training-only statistics
    # -----------------------------------------------------------------

    print(
        "\n[4] Fitting feature generator on TRAIN only..."
    )

    feature_generator.fit(
        X_train_raw
    )

    X_train_features = (
        feature_generator.transform(
            X_train_raw
        )
    )

    X_val_features = (
        feature_generator.transform(
            X_val_raw
        )
    )

    X_test_features = (
        feature_generator.transform(
            X_test_raw
        )
    )

    # -----------------------------------------------------------------
    # Feature selection
    # -----------------------------------------------------------------

    selector = FeatureSelector()

    X_train, y_train = selector.split(
        X_train_features.assign(
            label=y_train.values
        )
    )

    X_val, y_val = selector.split(
        X_val_features.assign(
            label=y_val.values
        )
    )

    X_test, y_test = selector.split(
        X_test_features.assign(
            label=y_test.values
        )
    )

    print(
        f"\nML feature count: "
        f"{len(X_train.columns)}"
    )

    # -----------------------------------------------------------------
    # Feature alignment
    # -----------------------------------------------------------------

    if list(X_train.columns) != list(
        X_val.columns
    ):
        raise RuntimeError(
            "TRAIN and VALIDATION feature columns differ."
        )

    if list(X_train.columns) != list(
        X_test.columns
    ):
        raise RuntimeError(
            "TRAIN and TEST feature columns differ."
        )

    # -----------------------------------------------------------------
    # Build preprocessing
    # -----------------------------------------------------------------

    active_num = [
        c
        for c in NUMERIC_COLUMNS
        if c in X_train.columns
    ]

    active_cat = [
        c
        for c in CATEGORICAL_COLUMNS
        if c in X_train.columns
    ]

    transformer = (
        DatasetTransformer(
            numeric_features=active_num,
            categorical_features=active_cat,
        ).build()
    )

    # -----------------------------------------------------------------
    # XGBoost
    # -----------------------------------------------------------------

    print(
        "\n[5] Training XGBoost..."
    )

    # IMPORTANT: This configuration is the frozen historical controlled
    # temporal protocol. Do NOT replace it with ModelFactory defaults.
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

    pipeline = (
        MLPipeline(
            transformer=transformer
        ).build(model)
    )

    start = time.perf_counter()
    pipeline.fit(X_train, y_train)
    training_time = time.perf_counter() - start

    print(
        f"Training time: {training_time:.3f}s"
    )

    # -----------------------------------------------------------------
    # Validation threshold
    # -----------------------------------------------------------------

    print(
        "\n[6] Selecting threshold on VALIDATION only..."
    )

    (
        threshold,
        validation_f1,
        _,
        threshold_rows,
    ) = optimize_threshold(
        pipeline,
        X_val,
        y_val,
    )

    print(
        f"Validation-best threshold: "
        f"{threshold:.2f}"
    )

    print(
        f"Validation F1: "
        f"{validation_f1:.6f}"
    )

    # -----------------------------------------------------------------
    # Final test
    # -----------------------------------------------------------------

    print(
        "\n[7] Evaluating TEST with frozen threshold..."
    )

    metrics = evaluate_test(
        pipeline,
        X_test,
        y_test,
        threshold,
    )

    print("\n" + "=" * 90)
    print("CONTROLLED TEMPORAL RESULT")
    print("=" * 90)

    print(
        f"Accuracy  : {metrics['accuracy'] * 100:.2f}%"
    )

    print(
        f"Precision : {metrics['precision'] * 100:.2f}%"
    )

    print(
        f"Recall    : {metrics['recall'] * 100:.2f}%"
    )

    print(
        f"F1        : {metrics['f1'] * 100:.2f}%"
    )

    print(
        f"ROC-AUC   : {metrics['roc_auc']:.5f}"
    )

    print(
        f"PR-AUC    : {metrics['pr_auc']:.5f}"
    )

    print(
        f"FPR       : {metrics['fpr'] * 100:.2f}%"
    )

    print(
        f"FNR       : {metrics['fnr'] * 100:.2f}%"
    )

    print(
        f"Threshold : {threshold:.2f}"
    )

    print(
        f"\nTN={metrics['tn']}"
        f" FP={metrics['fp']}"
        f" FN={metrics['fn']}"
        f" TP={metrics['tp']}"
    )

    # -----------------------------------------------------------------
    # Slow Drift-specific test performance
    # -----------------------------------------------------------------

    test_metadata = test_df[
        [
            "record_id",
            "attack_type",
            "label",
        ]
    ].copy()

    test_metadata["prediction"] = (
        metrics["predictions"]
    )

    test_metadata["probability"] = (
        metrics["probabilities"]
    )

    slow_test = test_metadata[
        test_metadata["attack_type"]
        == ATTACK_NAME
    ]

    normal_test = test_metadata[
        test_metadata["label"] == 0
    ]

    print(
        "\n" + "-" * 90
    )

    print(
        "SLOW DRIFT TEST ANALYSIS"
    )

    print("-" * 90)

    if len(slow_test) > 0:

        slow_recall = (
            slow_test["prediction"] == 1
        ).mean()

        print(
            f"Slow Drift test samples: "
            f"{len(slow_test):,}"
        )

        print(
            f"Slow Drift recall: "
            f"{slow_recall * 100:.2f}%"
        )

        print(
            f"Slow Drift missed: "
            f"{(slow_test['prediction'] == 0).sum():,}"
        )

    if len(normal_test) > 0:

        normal_fpr = (
            normal_test["prediction"] == 1
        ).mean()

        print(
            f"Normal test samples: "
            f"{len(normal_test):,}"
        )

        print(
            f"Normal false-positive rate: "
            f"{normal_fpr * 100:.2f}%"
        )

    # -----------------------------------------------------------------
    # Final interpretation
    # -----------------------------------------------------------------

    print(
        "\n" + "=" * 90
    )

    print(
        "INTERPRETATION"
    )

    print("=" * 90)

    print(
        "\nThis result must NOT replace the Phase 4.1 benchmark."
    )

    print(
        "It is a controlled research experiment designed "
        "to determine whether exposing the model to early "
        "Slow Drift improves recognition of later Slow Drift."
    )

    print(
        "\nNO DATASET WAS MODIFIED."
    )

    print(
        "NO LABELS WERE MODIFIED."
    )

    print(
        "NO PHASE 4.1 FILES WERE MODIFIED."
    )

    print(
        "\nExperiment complete."
    )


if __name__ == "__main__":
    main()