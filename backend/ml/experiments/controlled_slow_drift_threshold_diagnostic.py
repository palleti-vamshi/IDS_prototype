"""
LightX-IDS Controlled Slow Drift Threshold Diagnostic

RESEARCH / DIAGNOSTIC ONLY.

This script:
- DOES NOT modify the dataset
- DOES NOT modify Phase 4.1 code
- DOES NOT modify labels
- DOES NOT save trained models
- DOES NOT overwrite Phase 4.1 reports

Purpose:
Determine whether the very low threshold selected in the original
controlled temporal experiment was caused by a validation set
containing only Slow Drift attacks.

Original controlled experiment:
    TRAIN:      records 1..89,000
    VALIDATION: records 89,001..90,000
    TEST:       records 90,001..100,000

Problem:
    Validation contained:
        1,000 Slow Drift
        0 Normal

Therefore F1 threshold optimization had no normal examples against
which false positives could be penalized.

This diagnostic keeps the same training and untouched test set,
but creates a MIXED VALIDATION SET containing:

    1,000 early Slow Drift samples
    1,000 normal samples

The threshold is selected ONLY on this mixed validation set.

The final test remains:
    records 90,001..100,000

This is NOT a replacement for the Phase 4.1 benchmark.

It is a threshold-calibration diagnostic.
"""

from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)


# ============================================================================
# REPOSITORY / IMPORTS
# ============================================================================

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

from backend.ml.models.model_factory import (
    ModelFactory,
)

from backend.ml.training.trainer import (
    ModelTrainer,
)


# ============================================================================
# CONFIGURATION
# ============================================================================

DATASET = LIGHTX_100K

# Same controlled temporal training boundary.
TRAIN_END = 89000

# Original Slow Drift validation boundary.
VAL_END = 90000

# Slow Drift attack name in the actual dataset.
ATTACK_NAME = "Slow Drift Attack"

# Number of Slow Drift samples used for threshold calibration.
MIXED_SLOW_DRIFT_COUNT = 1000

# Number of normal samples used for threshold calibration.
MIXED_NORMAL_COUNT = 1000

# Threshold search range.
THRESHOLD_MIN = 0.10
THRESHOLD_MAX = 0.90
THRESHOLD_STEP = 0.05


# ============================================================================
# UTILITY: ATTACK DISTRIBUTION
# ============================================================================

def print_attack_distribution(name, frame):
    """
    Print row count, attack distribution, and Slow Drift count.
    """

    print(f"\n{name}")
    print("-" * 70)

    print(
        f"Rows: {len(frame):,}"
    )

    distribution = (
        frame["attack_type"]
        .value_counts(dropna=False)
    )

    print(
        distribution.to_string()
    )

    slow_count = (
        frame["attack_type"]
        .eq(ATTACK_NAME)
        .sum()
    )

    print(
        f"\nSlow Drift Attack samples: "
        f"{slow_count:,}"
    )


# ============================================================================
# UTILITY: THRESHOLD OPTIMIZATION
# ============================================================================

def optimize_threshold(
    pipeline,
    X_val,
    y_val,
):
    """
    Select threshold using validation F1 only.

    IMPORTANT:
    Test data is never used for threshold selection.
    """

    probabilities = (
        pipeline
        .predict_proba(X_val)[:, 1]
    )

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

        precision = precision_score(
            y_val,
            predictions,
            zero_division=0,
        )

        recall = recall_score(
            y_val,
            predictions,
            zero_division=0,
        )

        rows.append(
            {
                "threshold": float(threshold),
                "f1": float(score),
                "precision": float(precision),
                "recall": float(recall),
            }
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


# ============================================================================
# UTILITY: TEST EVALUATION
# ============================================================================

def evaluate_test(
    pipeline,
    X_test,
    y_test,
    threshold,
):
    """
    Evaluate untouched test data using the validation-frozen threshold.
    """

    probabilities = (
        pipeline
        .predict_proba(X_test)[:, 1]
    )

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


# ============================================================================
# MAIN
# ============================================================================

def main():

    print("=" * 90)
    print(
        "LIGHTX-IDS CONTROLLED SLOW DRIFT "
        "THRESHOLD DIAGNOSTIC"
    )
    print("=" * 90)

    print(
        f"\nDataset: {DATASET}"
    )

    print(
        f"Training records: 1..{TRAIN_END:,}"
    )

    print(
        f"Original validation region: "
        f"{TRAIN_END + 1:,}..{VAL_END:,}"
    )

    print(
        "Test records: "
        f"{VAL_END + 1:,}..100,000"
    )

    print(
        "\nMIXED VALIDATION:"
    )

    print(
        f"Slow Drift: "
        f"{MIXED_SLOW_DRIFT_COUNT:,}"
    )

    print(
        f"Normal: "
        f"{MIXED_NORMAL_COUNT:,}"
    )

    print(
        "\nIMPORTANT:"
    )

    print(
        "This is a diagnostic experiment."
    )

    print(
        "Phase 4.1 remains unchanged."
    )

    print(
        "The authoritative dataset remains unchanged."
    )


    # ========================================================================
    # 1. LOAD DATASET
    # ========================================================================

    print(
        "\n[1] Loading dataset..."
    )

    df = pd.read_csv(
        DATASET
    )

    df = (
        df
        .sort_values("record_id")
        .reset_index(drop=True)
    )

    print(
        f"Loaded {len(df):,} records."
    )


    # ========================================================================
    # 2. GENERATE CAUSAL STREAM FEATURES
    # ========================================================================

    print(
        "\n[2] Generating causal stream features..."
    )

    feature_generator = (
        FeatureGenerator()
    )

    df_stream = (
        feature_generator
        .generate_causal_stream_features(df)
    )

    print(
        f"Generated stream features: "
        f"{len(df_stream.columns)} columns."
    )


    # ========================================================================
    # 3. CONTROLLED TEMPORAL TRAIN / VAL / TEST BOUNDARIES
    # ========================================================================

    print(
        "\n[3] Creating controlled temporal regions..."
    )

    train_df = (
        df_stream
        .iloc[:TRAIN_END]
        .copy()
    )

    original_val_df = (
        df_stream
        .iloc[TRAIN_END:VAL_END]
        .copy()
    )

    test_df = (
        df_stream
        .iloc[VAL_END:]
        .copy()
    )


    print_attack_distribution(
        "TRAIN",
        train_df,
    )

    print_attack_distribution(
        "ORIGINAL VALIDATION REGION",
        original_val_df,
    )

    print_attack_distribution(
        "TEST",
        test_df,
    )


    # ========================================================================
    # 4. TRAIN LABEL / FEATURE EXTRACTION
    # ========================================================================

    print(
        "\n[4] Preparing TRAIN..."
    )

    y_train = (
        train_df["label"]
        .copy()
    )

    X_train_raw = (
        train_df
        .drop(columns=["label"])
    )


    # ========================================================================
    # 5. TEST LABEL / FEATURE EXTRACTION
    # ========================================================================

    print(
        "\n[5] Preparing untouched TEST..."
    )

    y_test = (
        test_df["label"]
        .copy()
    )

    X_test_raw = (
        test_df
        .drop(columns=["label"])
    )


    # ========================================================================
    # 6. FIT FEATURE GENERATOR ON TRAIN ONLY
    # ========================================================================

    print(
        "\n[6] Fitting feature generator on TRAIN only..."
    )

    feature_generator.fit(
        X_train_raw
    )

    X_train_features = (
        feature_generator
        .transform(X_train_raw)
    )

    X_test_features = (
        feature_generator
        .transform(X_test_raw)
    )


    # ========================================================================
    # 7. FEATURE SELECTION
    # ========================================================================

    print(
        "\n[7] Applying feature selection..."
    )

    selector = FeatureSelector()

    X_train, y_train = (
        selector.split(
            X_train_features.assign(
                label=y_train.values
            )
        )
    )

    X_test, y_test = (
        selector.split(
            X_test_features.assign(
                label=y_test.values
            )
        )
    )

    print(
        f"ML feature count: "
        f"{len(X_train.columns)}"
    )


    # ========================================================================
    # 8. FEATURE SCHEMA
    # ========================================================================

    if list(X_train.columns) != list(
        X_test.columns
    ):
        raise RuntimeError(
            "TRAIN and TEST feature columns differ."
        )


    # ========================================================================
    # 9. BUILD PREPROCESSOR
    # ========================================================================

    print(
        "\n[8] Building preprocessing pipeline..."
    )

    active_num = [
        column
        for column in NUMERIC_COLUMNS
        if column in X_train.columns
    ]

    active_cat = [
        column
        for column in CATEGORICAL_COLUMNS
        if column in X_train.columns
    ]

    transformer = (
        DatasetTransformer(
            numeric_features=active_num,
            categorical_features=active_cat,
        )
        .build()
    )


    # ========================================================================
    # 10. CREATE XGBOOST PIPELINE
    # ========================================================================

    print(
        "\n[9] Building XGBoost pipeline..."
    )

    factory = ModelFactory()

    model = (
        factory
        .get("xgboost")
    )

    pipeline = (
        MLPipeline(
            transformer=transformer
        )
        .build(model)
    )


    # ========================================================================
    # 11. TRAIN XGBOOST
    # ========================================================================

    print(
        "\n[10] Training XGBoost..."
    )

    trainer = ModelTrainer()

    start = time.perf_counter()

    pipeline, training_time = (
        trainer.train(
            pipeline,
            X_train,
            y_train,
            model_name=(
                "xgboost_controlled_slow_drift_threshold"
            ),
        )
    )

    elapsed = (
        time.perf_counter()
        - start
    )

    print(
        f"Training time: "
        f"{training_time:.3f}s"
    )

    print(
        f"Wall-clock time: "
        f"{elapsed:.3f}s"
    )


    # ========================================================================
    # 12. BUILD MIXED VALIDATION SET
    # ========================================================================

    print(
        "\n[11] Building mixed validation set..."
    )

    # ------------------------------------------------------------------------
    # Early Slow Drift samples
    # ------------------------------------------------------------------------

    slow_val = (
        original_val_df[
            original_val_df["attack_type"]
            == ATTACK_NAME
        ]
        .copy()
    )

    if len(slow_val) < MIXED_SLOW_DRIFT_COUNT:

        raise RuntimeError(
            "Not enough Slow Drift validation "
            "records for mixed validation."
        )

    slow_val = (
        slow_val
        .iloc[:MIXED_SLOW_DRIFT_COUNT]
        .copy()
    )


    # ------------------------------------------------------------------------
    # Normal validation samples
    # ------------------------------------------------------------------------
    #
    # Select deterministic normal records from the historical normal
    # population before the Slow Drift campaign.
    #
    # This does NOT alter the test set.
    # ------------------------------------------------------------------------

    normal_pool = (
        df_stream[
            (df_stream["label"] == 0)
            &
            (
                df_stream["record_id"]
                < 87965
            )
        ]
        .copy()
    )

    if len(normal_pool) < MIXED_NORMAL_COUNT:

        raise RuntimeError(
            "Not enough normal records "
            "for mixed validation."
        )

    # Deterministic selection:
    # take the latest 1000 normal records
    # before the Slow Drift campaign.
    normal_val = (
        normal_pool
        .iloc[-MIXED_NORMAL_COUNT:]
        .copy()
    )


    # ------------------------------------------------------------------------
    # Combine
    # ------------------------------------------------------------------------

    mixed_val = (
        pd.concat(
            [
                normal_val,
                slow_val,
            ],
            axis=0,
        )
        .sort_values("record_id")
        .reset_index(drop=True)
    )

    print(
        f"\nMixed validation rows: "
        f"{len(mixed_val):,}"
    )

    print(
        "\nMixed validation distribution:"
    )

    print(
        mixed_val["attack_type"]
        .value_counts(
            dropna=False
        )
        .to_string()
    )


    # ========================================================================
    # 13. TRANSFORM MIXED VALIDATION
    # ========================================================================

    print(
        "\n[12] Transforming mixed validation..."
    )

    X_mixed_raw = (
        mixed_val
        .drop(columns=["label"])
    )

    y_mixed = (
        mixed_val["label"]
        .copy()
    )

    X_mixed_features = (
        feature_generator
        .transform(X_mixed_raw)
    )

    X_mixed, y_mixed = (
        selector.split(
            X_mixed_features.assign(
                label=y_mixed.values
            )
        )
    )


    # ========================================================================
    # 14. VERIFY FEATURE SCHEMA
    # ========================================================================

    if list(X_train.columns) != list(
        X_mixed.columns
    ):
        raise RuntimeError(
            "TRAIN and MIXED VALIDATION "
            "feature columns differ."
        )

    if list(X_train.columns) != list(
        X_test.columns
    ):
        raise RuntimeError(
            "TRAIN and TEST "
            "feature columns differ."
        )


    # ========================================================================
    # 15. VALIDATION THRESHOLD OPTIMIZATION
    # ========================================================================

    print(
        "\n[13] Selecting threshold on MIXED VALIDATION only..."
    )

    (
        threshold,
        validation_f1,
        validation_probabilities,
        threshold_rows,
    ) = optimize_threshold(
        pipeline,
        X_mixed,
        y_mixed,
    )

    print(
        "\nThreshold search:"
    )

    threshold_table = (
        pd.DataFrame(
            threshold_rows
        )
        .sort_values(
            "threshold"
        )
    )

    print(
        threshold_table
        .to_string(index=False)
    )

    print(
        f"\nMixed-validation best threshold: "
        f"{threshold:.2f}"
    )

    print(
        f"Mixed-validation F1: "
        f"{validation_f1:.6f}"
    )


    # ========================================================================
    # 16. VALIDATION CONFUSION MATRIX
    # ========================================================================

    validation_predictions = (
        validation_probabilities
        >= threshold
    ).astype(int)

    val_tn, val_fp, val_fn, val_tp = (
        confusion_matrix(
            y_mixed,
            validation_predictions,
            labels=[0, 1],
        )
        .ravel()
    )

    val_fpr = (
        val_fp / (val_fp + val_tn)
        if (val_fp + val_tn) > 0
        else 0.0
    )

    val_fnr = (
        val_fn / (val_fn + val_tp)
        if (val_fn + val_tp) > 0
        else 0.0
    )

    print(
        "\nMixed-validation confusion matrix:"
    )

    print(
        f"TN={val_tn}"
        f" FP={val_fp}"
        f" FN={val_fn}"
        f" TP={val_tp}"
    )

    print(
        f"Validation FPR: "
        f"{val_fpr * 100:.2f}%"
    )

    print(
        f"Validation FNR: "
        f"{val_fnr * 100:.2f}%"
    )


    # ========================================================================
    # 17. FINAL TEST
    # ========================================================================

    print(
        "\n[14] Evaluating UNTOUCHED TEST..."
    )

    metrics = evaluate_test(
        pipeline,
        X_test,
        y_test,
        threshold,
    )


    # ========================================================================
    # 18. OVERALL TEST RESULT
    # ========================================================================

    print(
        "\n" + "=" * 90
    )

    print(
        "MIXED-VALIDATION THRESHOLD TEST RESULT"
    )

    print(
        "=" * 90
    )

    print(
        f"Accuracy  : "
        f"{metrics['accuracy'] * 100:.2f}%"
    )

    print(
        f"Precision : "
        f"{metrics['precision'] * 100:.2f}%"
    )

    print(
        f"Recall    : "
        f"{metrics['recall'] * 100:.2f}%"
    )

    print(
        f"F1        : "
        f"{metrics['f1'] * 100:.2f}%"
    )

    print(
        f"ROC-AUC   : "
        f"{metrics['roc_auc']:.5f}"
    )

    print(
        f"PR-AUC    : "
        f"{metrics['pr_auc']:.5f}"
    )

    print(
        f"FPR       : "
        f"{metrics['fpr'] * 100:.2f}%"
    )

    print(
        f"FNR       : "
        f"{metrics['fnr'] * 100:.2f}%"
    )

    print(
        f"Threshold : "
        f"{threshold:.2f}"
    )

    print(
        f"\nTN={metrics['tn']}"
        f" FP={metrics['fp']}"
        f" FN={metrics['fn']}"
        f" TP={metrics['tp']}"
    )


    # ========================================================================
    # 19. SLOW DRIFT-SPECIFIC TEST ANALYSIS
    # ========================================================================

    test_metadata = (
        test_df[
            [
                "record_id",
                "attack_type",
                "label",
            ]
        ]
        .copy()
    )

    test_metadata["prediction"] = (
        metrics["predictions"]
    )

    test_metadata["probability"] = (
        metrics["probabilities"]
    )


    slow_test = (
        test_metadata[
            test_metadata["attack_type"]
            == ATTACK_NAME
        ]
        .copy()
    )

    normal_test = (
        test_metadata[
            test_metadata["label"]
            == 0
        ]
        .copy()
    )


    print(
        "\n" + "-" * 90
    )

    print(
        "SLOW DRIFT TEST ANALYSIS"
    )

    print(
        "-" * 90
    )


    if len(slow_test) > 0:

        slow_recall = (
            slow_test["prediction"]
            == 1
        ).mean()

        slow_missed = (
            slow_test["prediction"]
            == 0
        ).sum()

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
            f"{slow_missed:,}"
        )


    if len(normal_test) > 0:

        normal_fpr = (
            normal_test["prediction"]
            == 1
        ).mean()

        normal_false_positives = (
            normal_test["prediction"]
            == 1
        ).sum()

        print(
            f"Normal test samples: "
            f"{len(normal_test):,}"
        )

        print(
            f"Normal false-positive rate: "
            f"{normal_fpr * 100:.2f}%"
        )

        print(
            f"Normal false positives: "
            f"{normal_false_positives:,}"
        )


    # ========================================================================
    # 20. COMPARISON WITH PREVIOUS CONTROLLED EXPERIMENT
    # ========================================================================

    print(
        "\n" + "=" * 90
    )

    print(
        "COMPARISON WITH PREVIOUS CONTROLLED EXPERIMENT"
    )

    print(
        "=" * 90
    )

    print(
        "\nPrevious controlled experiment:"
    )

    print(
        "Validation = 1,000 Slow Drift"
    )

    print(
        "Validation normal samples = 0"
    )

    print(
        "Threshold = 0.10"
    )

    print(
        "Test Accuracy = 97.63%"
    )

    print(
        "Test FPR = 2.83%"
    )

    print(
        "Slow Drift Recall = 99.77%"
    )

    print(
        "\nCurrent diagnostic:"
    )

    print(
        f"Validation = "
        f"{MIXED_SLOW_DRIFT_COUNT:,} Slow Drift"
    )

    print(
        f"Validation = "
        f"{MIXED_NORMAL_COUNT:,} Normal"
    )

    print(
        f"Threshold = "
        f"{threshold:.2f}"
    )

    print(
        f"Test Accuracy = "
        f"{metrics['accuracy'] * 100:.2f}%"
    )

    print(
        f"Test FPR = "
        f"{metrics['fpr'] * 100:.2f}%"
    )

    print(
        f"Slow Drift Recall = "
        f"{(
            (
                slow_test["prediction"] == 1
            ).mean()
            if len(slow_test) > 0
            else 0.0
        ) * 100:.2f}%"
    )


    # ========================================================================
    # 21. FINAL INTERPRETATION
    # ========================================================================

    print(
        "\n" + "=" * 90
    )

    print(
        "INTERPRETATION"
    )

    print(
        "=" * 90
    )

    print(
        "\nThis experiment does NOT replace the Phase 4.1 benchmark."
    )

    print(
        "It only evaluates the effect of using a mixed "
        "validation distribution for threshold calibration."
    )

    print(
        "\nThe TEST partition was not used for threshold selection."
    )

    print(
        "The TEST partition remains records "
        f"{VAL_END + 1:,}..100,000."
    )

    print(
        "\nNo dataset rows were modified."
    )

    print(
        "No labels were modified."
    )

    print(
        "No Phase 4.1 files were modified."
    )

    print(
        "No Phase 4.1 benchmark was overwritten."
    )

    print(
        "\nDiagnostic complete."
    )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()