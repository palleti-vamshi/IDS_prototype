"""
LightX-IDS Temporal False-Positive Diagnostic

READ-ONLY RESEARCH DIAGNOSTIC.

Purpose:
Identify what makes the 233 normal records in the controlled
temporal test look like attacks.

This script:
- Does not modify the dataset.
- Does not modify Phase 4.1.
- Does not modify labels.
- Does not overwrite reports.
- Does not tune the model.
- Reproduces the controlled temporal experiment.
- Uses the mixed-validation threshold of 0.10.
- Analyzes only NORMAL test records.

Controlled temporal protocol:

TRAIN:
    records 1..89,000

MIXED VALIDATION:
    1,000 normal
    1,000 Slow Drift

TEST:
    records 90,001..100,000

The diagnostic compares:

    Correct Normal
        vs
    False-Positive Normal

across:
    - device
    - sensor
    - sensor type
    - physical value
    - sequence behavior
    - timing behavior
    - rolling features
    - physical dynamics
    - model probability
"""

from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

from sklearn.metrics import (
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

TRAIN_END = 89000
VAL_END = 90000

ATTACK_NAME = "Slow Drift Attack"

MIXED_SLOW_DRIFT_COUNT = 1000
MIXED_NORMAL_COUNT = 1000

THRESHOLD = 0.10


# ============================================================================
# HELPER
# ============================================================================

def print_section(title):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def describe_numeric(
    frame,
    column,
):
    """
    Print descriptive statistics safely.
    """

    if column not in frame.columns:
        return

    series = pd.to_numeric(
        frame[column],
        errors="coerce",
    ).dropna()

    if len(series) == 0:
        return

    print(
        f"\n{column}"
    )

    print(
        series.describe().to_string()
    )


def compare_numeric(
    correct,
    false_positive,
    columns,
):
    """
    Compare numeric feature distributions between:
        correctly classified normal
        false-positive normal
    """

    rows = []

    for column in columns:

        if column not in correct.columns:
            continue

        correct_values = pd.to_numeric(
            correct[column],
            errors="coerce",
        )

        fp_values = pd.to_numeric(
            false_positive[column],
            errors="coerce",
        )

        correct_values = (
            correct_values
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
        )

        fp_values = (
            fp_values
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
        )

        if len(correct_values) == 0:
            continue

        if len(fp_values) == 0:
            continue

        correct_mean = correct_values.mean()
        fp_mean = fp_values.mean()

        correct_std = correct_values.std()
        fp_std = fp_values.std()

        pooled_std = np.sqrt(
            (
                correct_std ** 2
                +
                fp_std ** 2
            )
            / 2
        )

        if pooled_std > 0:
            standardized_difference = (
                fp_mean - correct_mean
            ) / pooled_std
        else:
            standardized_difference = 0.0

        rows.append(
            {
                "feature": column,
                "correct_mean": correct_mean,
                "fp_mean": fp_mean,
                "correct_std": correct_std,
                "fp_std": fp_std,
                "standardized_difference":
                    standardized_difference,
            }
        )

    if not rows:
        print(
            "No comparable numeric features found."
        )
        return pd.DataFrame()

    result = (
        pd.DataFrame(rows)
        .sort_values(
            "standardized_difference",
            key=lambda x: x.abs(),
            ascending=False,
        )
    )

    print(
        result
        .head(30)
        .to_string(index=False)
    )

    return result


# ============================================================================
# MAIN
# ============================================================================

def main():

    print_section(
        "LIGHTX-IDS TEMPORAL FALSE-POSITIVE DIAGNOSTIC"
    )

    print(
        f"\nDataset: {DATASET}"
    )

    print(
        f"TRAIN: records 1..{TRAIN_END:,}"
    )

    print(
        f"TEST: records {VAL_END + 1:,}..100,000"
    )

    print(
        f"Threshold: {THRESHOLD:.2f}"
    )

    print(
        "\nThis is READ-ONLY."
    )


    # ========================================================================
    # 1. LOAD DATASET
    # ========================================================================

    print_section(
        "[1] LOAD DATASET"
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
        f"Rows loaded: {len(df):,}"
    )


    # ========================================================================
    # 2. GENERATE CAUSAL FEATURES
    # ========================================================================

    print_section(
        "[2] GENERATE CAUSAL STREAM FEATURES"
    )

    feature_generator = (
        FeatureGenerator()
    )

    df_stream = (
        feature_generator
        .generate_causal_stream_features(
            df
        )
    )

    print(
        f"Columns after causal features: "
        f"{len(df_stream.columns)}"
    )


    # ========================================================================
    # 3. SPLIT
    # ========================================================================

    print_section(
        "[3] CONTROLLED TEMPORAL SPLIT"
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

    print(
        f"TRAIN: {len(train_df):,}"
    )

    print(
        f"VALIDATION REGION: "
        f"{len(original_val_df):,}"
    )

    print(
        f"TEST: {len(test_df):,}"
    )


    # ========================================================================
    # 4. PREPARE TRAIN
    # ========================================================================

    print_section(
        "[4] PREPARE TRAIN"
    )

    y_train = (
        train_df["label"]
        .copy()
    )

    X_train_raw = (
        train_df
        .drop(columns=["label"])
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
    # 5. TRAIN-ONLY FEATURE FIT
    # ========================================================================

    print_section(
        "[5] TRAIN-ONLY FEATURE FIT"
    )

    feature_generator.fit(
        X_train_raw
    )

    X_train_features = (
        feature_generator
        .transform(
            X_train_raw
        )
    )

    X_test_features = (
        feature_generator
        .transform(
            X_test_raw
        )
    )


    # ========================================================================
    # 6. FEATURE SELECTION
    # ========================================================================

    print_section(
        "[6] FEATURE SELECTION"
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
    # 7. PREPROCESSOR
    # ========================================================================

    print_section(
        "[7] PREPROCESSING"
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
    # 8. XGBOOST
    # ========================================================================

    print_section(
        "[8] XGBOOST TRAINING"
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

    trainer = ModelTrainer()

    start = time.perf_counter()

    pipeline, training_time = (
        trainer.train(
            pipeline,
            X_train,
            y_train,
            model_name=(
                "xgboost_temporal_fp_diagnostic"
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
    # 9. TEST PREDICTIONS
    # ========================================================================

    print_section(
        "[9] TEST PREDICTIONS"
    )

    probabilities = (
        pipeline
        .predict_proba(X_test)[:, 1]
    )

    predictions = (
        probabilities
        >= THRESHOLD
    ).astype(int)

    test_analysis = (
        test_df[
            [
                "record_id",
                "timestamp",
                "topic",
                "device_id",
                "sensor_code",
                "sensor_type",
                "value",
                "unit",
                "status",
                "attack_type",
                "label",
                "source",
                "sequence_number",
            ]
        ]
        .copy()
    )

    test_analysis[
        "attack_probability"
    ] = probabilities

    test_analysis[
        "prediction"
    ] = predictions


    # ========================================================================
    # 10. NORMAL TEST ONLY
    # ========================================================================

    print_section(
        "[10] NORMAL TEST ANALYSIS"
    )

    normal_test = (
        test_analysis[
            test_analysis["label"] == 0
        ]
        .copy()
    )

    correct_normal = (
        normal_test[
            normal_test["prediction"] == 0
        ]
        .copy()
    )

    false_positive_normal = (
        normal_test[
            normal_test["prediction"] == 1
        ]
        .copy()
    )

    print(
        f"Normal test records: "
        f"{len(normal_test):,}"
    )

    print(
        f"Correct normal: "
        f"{len(correct_normal):,}"
    )

    print(
        f"False-positive normal: "
        f"{len(false_positive_normal):,}"
    )

    fp_rate = (
        len(false_positive_normal)
        /
        len(normal_test)
        if len(normal_test) > 0
        else 0
    )

    print(
        f"False-positive rate: "
        f"{fp_rate * 100:.2f}%"
    )


    # ========================================================================
    # 11. FALSE POSITIVE PROBABILITY DISTRIBUTION
    # ========================================================================

    print_section(
        "[11] ATTACK-PROBABILITY DISTRIBUTION"
    )

    print(
        "\nCorrect normal probability:"
    )

    print(
        correct_normal[
            "attack_probability"
        ]
        .describe()
        .to_string()
    )

    print(
        "\nFalse-positive normal probability:"
    )

    print(
        false_positive_normal[
            "attack_probability"
        ]
        .describe()
        .to_string()
    )


    # ========================================================================
    # 12. FALSE POSITIVE RECORDS
    # ========================================================================

    print_section(
        "[12] FALSE-POSITIVE RECORDS"
    )

    display_columns = [
        "record_id",
        "timestamp",
        "device_id",
        "sensor_code",
        "sensor_type",
        "value",
        "status",
        "sequence_number",
        "attack_probability",
    ]

    print(
        "\nHighest-probability false positives:"
    )

    print(
        false_positive_normal[
            display_columns
        ]
        .sort_values(
            "attack_probability",
            ascending=False,
        )
        .head(50)
        .to_string(index=False)
    )


    # ========================================================================
    # 13. FALSE POSITIVE BY DEVICE
    # ========================================================================

    print_section(
        "[13] FALSE POSITIVE BY DEVICE"
    )

    device_total = (
        normal_test
        .groupby("device_id")
        .size()
        .rename("normal_total")
    )

    device_fp = (
        false_positive_normal
        .groupby("device_id")
        .size()
        .rename("false_positives")
    )

    device_summary = (
        pd.concat(
            [
                device_total,
                device_fp,
            ],
            axis=1,
        )
        .fillna(0)
    )

    device_summary[
        "false_positive_rate"
    ] = (
        device_summary["false_positives"]
        /
        device_summary["normal_total"]
    )

    device_summary = (
        device_summary
        .sort_values(
            "false_positive_rate",
            ascending=False,
        )
    )

    print(
        device_summary
        .to_string()
    )


    # ========================================================================
    # 14. FALSE POSITIVE BY SENSOR
    # ========================================================================

    print_section(
        "[14] FALSE POSITIVE BY SENSOR"
    )

    sensor_total = (
        normal_test
        .groupby("sensor_code")
        .size()
        .rename("normal_total")
    )

    sensor_fp = (
        false_positive_normal
        .groupby("sensor_code")
        .size()
        .rename("false_positives")
    )

    sensor_summary = (
        pd.concat(
            [
                sensor_total,
                sensor_fp,
            ],
            axis=1,
        )
        .fillna(0)
    )

    sensor_summary[
        "false_positive_rate"
    ] = (
        sensor_summary["false_positives"]
        /
        sensor_summary["normal_total"]
    )

    sensor_summary = (
        sensor_summary
        .sort_values(
            "false_positive_rate",
            ascending=False,
        )
    )

    print(
        sensor_summary
        .to_string()
    )


    # ========================================================================
    # 15. FALSE POSITIVE BY SENSOR TYPE
    # ========================================================================

    print_section(
        "[15] FALSE POSITIVE BY SENSOR TYPE"
    )

    type_total = (
        normal_test
        .groupby("sensor_type")
        .size()
        .rename("normal_total")
    )

    type_fp = (
        false_positive_normal
        .groupby("sensor_type")
        .size()
        .rename("false_positives")
    )

    type_summary = (
        pd.concat(
            [
                type_total,
                type_fp,
            ],
            axis=1,
        )
        .fillna(0)
    )

    type_summary[
        "false_positive_rate"
    ] = (
        type_summary["false_positives"]
        /
        type_summary["normal_total"]
    )

    type_summary = (
        type_summary
        .sort_values(
            "false_positive_rate",
            ascending=False,
        )
    )

    print(
        type_summary
        .to_string()
    )


    # ========================================================================
    # 16. FALSE POSITIVE BY STATUS
    # ========================================================================

    print_section(
        "[16] FALSE POSITIVE BY STATUS"
    )

    status_total = (
        normal_test
        .groupby("status")
        .size()
        .rename("normal_total")
    )

    status_fp = (
        false_positive_normal
        .groupby("status")
        .size()
        .rename("false_positives")
    )

    status_summary = (
        pd.concat(
            [
                status_total,
                status_fp,
            ],
            axis=1,
        )
        .fillna(0)
    )

    status_summary[
        "false_positive_rate"
    ] = (
        status_summary["false_positives"]
        /
        status_summary["normal_total"]
    )

    status_summary = (
        status_summary
        .sort_values(
            "false_positive_rate",
            ascending=False,
        )
    )

    print(
        status_summary
        .to_string()
    )


    # ========================================================================
    # 17. TEMPORAL LOCATION OF FALSE POSITIVES
    # ========================================================================

    print_section(
        "[17] TEMPORAL LOCATION OF FALSE POSITIVES"
    )

    if len(false_positive_normal) > 0:

        print(
            "\nFalse-positive record range:"
        )

        print(
            f"{false_positive_normal['record_id'].min()}"
            f" -> "
            f"{false_positive_normal['record_id'].max()}"
        )

        print(
            "\nFalse positives by 1,000-record bucket:"
        )

        false_positive_normal = (
            false_positive_normal
            .copy()
        )

        false_positive_normal[
            "record_bucket"
        ] = (
            false_positive_normal[
                "record_id"
            ]
            // 1000
        ) * 1000

        bucket_summary = (
            false_positive_normal
            .groupby("record_bucket")
            .size()
            .rename("false_positives")
        )

        print(
            bucket_summary
            .to_string()
        )


    # ========================================================================
    # 18. NUMERIC FEATURE COMPARISON
    # ========================================================================

    print_section(
        "[18] RAW NUMERIC DISTRIBUTION COMPARISON"
    )

    raw_numeric_columns = [
        "value",
        "sequence_number",
    ]

    compare_numeric(
        correct_normal,
        false_positive_normal,
        raw_numeric_columns,
    )


    # ========================================================================
    # 19. FEATURE-SPACE COMPARISON
    # ========================================================================

    print_section(
        "[19] ENGINEERED FEATURE DISTRIBUTION COMPARISON"
    )

    feature_frame = (
        df_stream
        .iloc[VAL_END:]
        .copy()
    )

    feature_frame[
        "attack_probability"
    ] = probabilities

    feature_frame[
        "prediction"
    ] = predictions

    feature_frame[
        "normal_correct"
    ] = (
        (feature_frame["label"] == 0)
        &
        (feature_frame["prediction"] == 0)
    )

    feature_frame[
        "normal_false_positive"
    ] = (
        (feature_frame["label"] == 0)
        &
        (feature_frame["prediction"] == 1)
    )

    correct_feature_frame = (
        feature_frame[
            feature_frame[
                "normal_correct"
            ]
        ]
        .copy()
    )

    fp_feature_frame = (
        feature_frame[
            feature_frame[
                "normal_false_positive"
            ]
        ]
        .copy()
    )

    feature_columns = [
        column
        for column in feature_frame.columns
        if column in X_train.columns
    ]

    print(
        f"\nComparing "
        f"{len(feature_columns)} ML features."
    )

    feature_comparison = compare_numeric(
        correct_feature_frame,
        fp_feature_frame,
        feature_columns,
    )


    # ========================================================================
    # 20. KEY TIMING FEATURES
    # ========================================================================

    print_section(
        "[20] TIMING / COMMUNICATION FEATURE COMPARISON"
    )

    timing_features = [
        "device_seq_gap",
        "seq_gap_dev",
        "rolling_seq_std_5",
        "time_delta",
        "rolling_time_delta_3",
        "rolling_time_delta_5",
        "rolling_time_delta_std_5",
        "is_negative_time_delta",
        "global_time_delta",
        "rolling_global_td_5",
        "rolling_global_td_10",
        "rolling_global_td_std_10",
        "packet_rate_10",
    ]

    timing_features = [
        column
        for column in timing_features
        if column in feature_frame.columns
    ]

    print(
        "\nTiming feature comparison:"
    )

    compare_numeric(
        correct_feature_frame,
        fp_feature_frame,
        timing_features,
    )


    # ========================================================================
    # 21. PHYSICAL DYNAMICS
    # ========================================================================

    print_section(
        "[21] PHYSICAL-DYNAMICS FEATURE COMPARISON"
    )

    physical_features = [
        "value_change",
        "abs_value_change",
        "value_accel",
        "is_duplicate_value",
        "plant_duplicate_ratio_19",
        "percentage_change",
        "rolling_mean_3",
        "rolling_mean_5",
        "rolling_mean_10",
        "rolling_std_3",
        "rolling_std_5",
        "rolling_std_10",
        "rolling_range_5",
    ]

    physical_features = [
        column
        for column in physical_features
        if column in feature_frame.columns
    ]

    print(
        "\nPhysical feature comparison:"
    )

    compare_numeric(
        correct_feature_frame,
        fp_feature_frame,
        physical_features,
    )


    # ========================================================================
    # 22. SENSOR-AWARE FEATURES
    # ========================================================================

    print_section(
        "[22] SENSOR-AWARE FEATURE COMPARISON"
    )

    sensor_aware_features = [
        "device_mean_deviation",
        "z_score",
        "rel_volatility",
        "stability_anomaly",
    ]

    sensor_aware_features = [
        column
        for column in sensor_aware_features
        if column in feature_frame.columns
    ]

    print(
        "\nSensor-aware feature comparison:"
    )

    compare_numeric(
        correct_feature_frame,
        fp_feature_frame,
        sensor_aware_features,
    )


    # ========================================================================
    # 23. FALSE POSITIVE PROBABILITY QUANTILES
    # ========================================================================

    print_section(
        "[23] PROBABILITY QUANTILES"
    )

    quantiles = [
        0.50,
        0.75,
        0.90,
        0.95,
        0.99,
        1.00,
    ]

    probability_comparison = pd.DataFrame(
        {
            "quantile": quantiles,
            "correct_normal":
                [
                    correct_normal[
                        "attack_probability"
                    ].quantile(q)
                    for q in quantiles
                ],
            "false_positive_normal":
                [
                    false_positive_normal[
                        "attack_probability"
                    ].quantile(q)
                    for q in quantiles
                ],
        }
    )

    print(
        probability_comparison
        .to_string(index=False)
    )


    # ========================================================================
    # 24. FINAL SUMMARY
    # ========================================================================

    print_section(
        "FINAL DIAGNOSTIC SUMMARY"
    )

    print(
        f"\nNormal test records: "
        f"{len(normal_test):,}"
    )

    print(
        f"Correct normal records: "
        f"{len(correct_normal):,}"
    )

    print(
        f"False-positive normal records: "
        f"{len(false_positive_normal):,}"
    )

    print(
        f"False-positive rate: "
        f"{fp_rate * 100:.2f}%"
    )

    if len(false_positive_normal) > 0:

        print(
            "\nFalse-positive probability range:"
        )

        print(
            f"Minimum: "
            f"{false_positive_normal['attack_probability'].min():.6f}"
        )

        print(
            f"Maximum: "
            f"{false_positive_normal['attack_probability'].max():.6f}"
        )

        print(
            f"Mean: "
            f"{false_positive_normal['attack_probability'].mean():.6f}"
        )

        print(
            f"Median: "
            f"{false_positive_normal['attack_probability'].median():.6f}"
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
        "NO MODEL WAS SAVED."
    )

    print(
        "\nDiagnostic complete."
    )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()