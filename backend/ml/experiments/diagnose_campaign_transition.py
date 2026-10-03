"""
LightX-IDS
Campaign Transition Diagnostic

READ-ONLY DIAGNOSTIC

Purpose:
    Determine whether temporal false positives are concentrated
    immediately after the Slow Drift -> Normal campaign transition.

Protocol intentionally matches the controlled temporal diagnostic:

    TRAIN:
        record_id 1..89000

    VALIDATION:
        record_id 89001..90000

    TEST:
        record_id 90001..100000

    XGBoost:
        n_estimators=400
        learning_rate=0.05
        max_depth=10
        min_child_weight=2
        subsample=0.90
        colsample_bytree=0.90
        reg_alpha=0.10
        reg_lambda=3.0

    Threshold:
        validation-only
        0.10..0.90
        step=0.05

IMPORTANT:
    This script does NOT modify:
        - dataset
        - labels
        - Phase 1-3 code
        - Phase 4 pipeline
        - reports
        - saved models
"""

from pathlib import Path
import time

import numpy as np
import pandas as pd

from xgboost import XGBClassifier

from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "lightx_ids_dataset_100k.csv"
)


# ============================================================
# PROTOCOL
# ============================================================

TRAIN_START = 1
TRAIN_END = 89000

VAL_START = 89001
VAL_END = 90000

TEST_START = 90001
TEST_END = 100000

RANDOM_STATE = 42


# ============================================================
# ATTACK NAME
# ============================================================

SLOW_DRIFT_NAME = "Slow Drift Attack"


# ============================================================
# OUTPUT HELPERS
# ============================================================

def banner(title: str) -> None:
    print()
    print("=" * 100)
    print(title)
    print("=" * 100)


def section(title: str) -> None:
    print()
    print(title)
    print("-" * 100)


# ============================================================
# CAUSAL FEATURE GENERATION
# ============================================================

def generate_causal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reproduce the causal stream features used by the controlled
    temporal diagnostics.

    Ordering is strictly by physical arrival order: record_id.
    """

    df = df.copy()

    df = df.sort_values(
        "record_id",
        kind="mergesort",
    ).reset_index(drop=True)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="raise",
    )

    df["value"] = pd.to_numeric(
        df["value"],
        errors="raise",
    )

    # --------------------------------------------------------
    # Basic per-record features
    # --------------------------------------------------------

    df["value_change"] = (
        df.groupby("device_id")["value"]
        .diff()
        .fillna(0.0)
    )

    df["abs_value_change"] = (
        df["value_change"].abs()
    )

    df["value_accel"] = (
        df.groupby("device_id")["value_change"]
        .diff()
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Device-local timing
    # --------------------------------------------------------

    df["time_delta"] = (
        df.groupby("device_id")["timestamp"]
        .diff()
        .dt.total_seconds()
        .fillna(0.0)
    )

    df["is_negative_time_delta"] = (
        df["time_delta"] < 0
    ).astype(int)

    # --------------------------------------------------------
    # Global arrival timing
    # --------------------------------------------------------

    df["global_time_delta"] = (
        df["timestamp"]
        .diff()
        .dt.total_seconds()
        .fillna(0.0)
    )

    df["rolling_global_td_10"] = (
        df["global_time_delta"]
        .rolling(
            window=10,
            min_periods=1,
        )
        .mean()
    )

    df["rolling_time_delta_5"] = (
        df.groupby("device_id")["time_delta"]
        .transform(
            lambda s: s.rolling(
                5,
                min_periods=1,
            ).mean()
        )
    )

    df["rolling_time_delta_std_5"] = (
        df.groupby("device_id")["time_delta"]
        .transform(
            lambda s: s.rolling(
                5,
                min_periods=2,
            ).std()
        )
        .fillna(0.0)
    )

    df["rolling_global_td_std_10"] = (
        df["global_time_delta"]
        .rolling(
            10,
            min_periods=2,
        )
        .std()
        .fillna(0.0)
    )

    df["packet_rate_10"] = (
        1.0
        / df["global_time_delta"]
        .replace(0, np.nan)
    ).rolling(
        10,
        min_periods=1,
    ).mean().fillna(0.0)

    # --------------------------------------------------------
    # Duplicate / sequence features
    # --------------------------------------------------------

    df["is_duplicate_value"] = (
        df.groupby("device_id")["value"]
        .diff()
        .eq(0)
        .astype(int)
    )

    df["device_seq_gap"] = (
        df.groupby("device_id")["sequence_number"]
        .diff()
        .fillna(0.0)
    )

    # Expected physical round-robin step is approximately 19.
    df["seq_gap_dev"] = (
        (df["device_seq_gap"] - 19.0)
        .abs()
    )

    df["rolling_seq_std_5"] = (
        df.groupby("device_id")["device_seq_gap"]
        .transform(
            lambda s: s.rolling(
                5,
                min_periods=2,
            ).std()
        )
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Physical rolling features
    # --------------------------------------------------------

    grouped_value = df.groupby("device_id")["value"]

    df["rolling_mean_3"] = (
        grouped_value.transform(
            lambda s: s.rolling(
                3,
                min_periods=1,
            ).mean()
        )
    )

    df["rolling_std_3"] = (
        grouped_value.transform(
            lambda s: s.rolling(
                3,
                min_periods=2,
            ).std()
        )
        .fillna(0.0)
    )

    df["rolling_mean_5"] = (
        grouped_value.transform(
            lambda s: s.rolling(
                5,
                min_periods=1,
            ).mean()
        )
    )

    df["rolling_std_5"] = (
        grouped_value.transform(
            lambda s: s.rolling(
                5,
                min_periods=2,
            ).std()
        )
        .fillna(0.0)
    )

    df["rolling_mean_10"] = (
        grouped_value.transform(
            lambda s: s.rolling(
                10,
                min_periods=1,
            ).mean()
        )
    )

    df["rolling_std_10"] = (
        grouped_value.transform(
            lambda s: s.rolling(
                10,
                min_periods=2,
            ).std()
        )
        .fillna(0.0)
    )

    df["rolling_range_5"] = (
        grouped_value.transform(
            lambda s: (
                s.rolling(
                    5,
                    min_periods=1,
                ).max()
                -
                s.rolling(
                    5,
                    min_periods=1,
                ).min()
            )
        )
    )

    # --------------------------------------------------------
    # Plant-wide duplicate ratio
    # --------------------------------------------------------

    df["plant_duplicate_ratio_19"] = (
        df["is_duplicate_value"]
        .rolling(
            19,
            min_periods=1,
        )
        .mean()
    )

    # --------------------------------------------------------
    # Percentage change
    # --------------------------------------------------------

    previous_value = (
        df.groupby("device_id")["value"]
        .shift(1)
    )

    denominator = previous_value.abs().replace(
        0,
        np.nan,
    )

    df["percentage_change"] = (
        (df["value"] - previous_value)
        / denominator
    ).replace(
        [np.inf, -np.inf],
        np.nan,
    ).fillna(0.0)

    return df


# ============================================================
# TRAIN-ONLY SENSOR STATISTICS
# ============================================================

def add_train_only_sensor_features(
    train_df: pd.DataFrame,
    other_dfs: list[pd.DataFrame],
) -> None:
    """
    Fit physical baselines strictly on training data.
    """

    stats = (
        train_df
        .groupby("device_id")["value"]
        .agg(["mean", "std"])
        .to_dict(orient="index")
    )

    train_diff = (
        train_df
        .groupby("device_id")["value"]
        .diff()
        .fillna(1.0)
    )

    duplicate_rates = (
        (train_diff == 0)
        .groupby(train_df["device_id"])
        .mean()
        .to_dict()
    )

    for split_df in [train_df] + other_dfs:

        means = split_df["device_id"].map(
            lambda d: stats.get(
                d,
                {},
            ).get(
                "mean",
                0.0,
            )
        )

        stds = split_df["device_id"].map(
            lambda d: stats.get(
                d,
                {},
            ).get(
                "std",
                1.0,
            )
        )

        stds = (
            stds
            .fillna(1.0)
            .replace(0, 1.0)
        )

        duplicate_rate = (
            split_df["device_id"]
            .map(
                lambda d: duplicate_rates.get(
                    d,
                    0.5,
                )
            )
            .fillna(0.5)
        )

        split_df["device_mean_deviation"] = (
            split_df["value"] - means
        )

        split_df["z_score"] = (
            (split_df["value"] - means)
            / stds
        )

        split_df["rel_volatility"] = (
            split_df["rolling_std_5"]
            / stds
        )

        split_df["stability_anomaly"] = (
            split_df["is_duplicate_value"]
            * (1.0 - duplicate_rate)
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    banner(
        "LIGHTX-IDS CAMPAIGN TRANSITION DIAGNOSTIC"
    )

    print("READ-ONLY ANALYSIS")
    print(f"Dataset: {DATASET_PATH}")

    # ========================================================
    # LOAD
    # ========================================================

    section("[1] LOAD AUTHORITATIVE DATASET")

    df = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Dataset shape: {df.shape}"
    )

    required_columns = {
        "record_id",
        "timestamp",
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
    }

    missing = (
        required_columns
        - set(df.columns)
    )

    if missing:
        raise RuntimeError(
            f"Missing required columns: {sorted(missing)}"
        )

    df = df.sort_values(
        "record_id",
        kind="mergesort",
    ).reset_index(drop=True)

    # ========================================================
    # IDENTIFY SLOW DRIFT BOUNDARY
    # ========================================================

    section("Slow Drift boundary")

    slow_drift = df[
        df["attack_type"]
        == SLOW_DRIFT_NAME
    ]

    if slow_drift.empty:
        raise RuntimeError(
            f"No '{SLOW_DRIFT_NAME}' records found."
        )

    slow_start = int(
        slow_drift["record_id"].min()
    )

    slow_end = int(
        slow_drift["record_id"].max()
    )

    print(
        f"Slow Drift start : {slow_start}"
    )

    print(
        f"Slow Drift end   : {slow_end}"
    )

    # ========================================================
    # TEMPORAL SPLIT
    # ========================================================

    section("Temporal split")

    train = df[
        (df["record_id"] >= TRAIN_START)
        & (df["record_id"] <= TRAIN_END)
    ].copy()

    val = df[
        (df["record_id"] >= VAL_START)
        & (df["record_id"] <= VAL_END)
    ].copy()

    test = df[
        (df["record_id"] >= TEST_START)
        & (df["record_id"] <= TEST_END)
    ].copy()

    print(
        f"Train : {TRAIN_START} -> {TRAIN_END} "
        f"({len(train):,})"
    )

    print(
        f"Validation : {VAL_START} -> {VAL_END} "
        f"({len(val):,})"
    )

    print(
        f"Test : {TEST_START} -> {TEST_END} "
        f"({len(test):,})"
    )

    print(
        "Slow Drift records in training:",
        int(
            (
                train["attack_type"]
                == SLOW_DRIFT_NAME
            ).sum()
        ),
    )

    # ========================================================
    # CAUSAL FEATURES
    # ========================================================

    section(
        "[2] GENERATE CAUSAL STREAM FEATURES"
    )

    print(
        "Ordering by record_id / physical arrival order..."
    )

    df_features = generate_causal_features(
        df
    )

    # Recover the temporal partitions after
    # feature generation.

    train = df_features[
        (df_features["record_id"] >= TRAIN_START)
        & (df_features["record_id"] <= TRAIN_END)
    ].copy()

    val = df_features[
        (df_features["record_id"] >= VAL_START)
        & (df_features["record_id"] <= VAL_END)
    ].copy()

    test = df_features[
        (df_features["record_id"] >= TEST_START)
        & (df_features["record_id"] <= TEST_END)
    ].copy()

    # ========================================================
    # TRAIN-ONLY FEATURES
    # ========================================================

    section(
        "[3] FIT TRAINING-ONLY SENSOR STATISTICS"
    )

    add_train_only_sensor_features(
        train,
        [val, test],
    )

    # ========================================================
    # FEATURE LIST
    # ========================================================

    numeric_columns = [
        "value",
        "value_change",
        "abs_value_change",
        "value_accel",
        "time_delta",
        "is_negative_time_delta",
        "global_time_delta",
        "rolling_global_td_10",
        "rolling_time_delta_5",
        "rolling_time_delta_std_5",
        "rolling_global_td_std_10",
        "packet_rate_10",
        "is_duplicate_value",
        "device_seq_gap",
        "seq_gap_dev",
        "rolling_seq_std_5",
        "rolling_mean_3",
        "rolling_std_3",
        "rolling_mean_5",
        "rolling_std_5",
        "rolling_mean_10",
        "rolling_std_10",
        "rolling_range_5",
        "plant_duplicate_ratio_19",
        "percentage_change",
        "device_mean_deviation",
        "z_score",
        "rel_volatility",
        "stability_anomaly",
    ]

    categorical_columns = [
        "topic",
        "device_id",
        "sensor_code",
        "sensor_type",
        "unit",
        "status",
        "source",
    ]

    feature_columns = (
        numeric_columns
        + categorical_columns
    )

    print(
        f"ML feature count: {len(feature_columns)}"
    )

    # ========================================================
    # PREPARE X/Y
    # ========================================================

    X_train = train[
        feature_columns
    ].copy()

    y_train = train["label"].astype(int)

    X_val = val[
        feature_columns
    ].copy()

    y_val = val["label"].astype(int)

    X_test = test[
        feature_columns
    ].copy()

    y_test = test["label"].astype(int)

    # ========================================================
    # PREPROCESSING
    # ========================================================

    section("[4] PREPROCESSING")

    transformer = ColumnTransformer(
        transformers=[
            (
                "num",
                StandardScaler(),
                numeric_columns,
            ),
            (
                "cat",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                categorical_columns,
            ),
        ]
    )

    X_train_transformed = (
        transformer.fit_transform(
            X_train
        )
    )

    X_val_transformed = (
        transformer.transform(
            X_val
        )
    )

    X_test_transformed = (
        transformer.transform(
            X_test
        )
    )

    print(
        "Training matrix:",
        X_train_transformed.shape,
    )

    print(
        "Validation matrix:",
        X_val_transformed.shape,
    )

    print(
        "Test matrix:",
        X_test_transformed.shape,
    )

    # ========================================================
    # XGBOOST
    # ========================================================

    section(
        "[5] TRAIN CONTROLLED TEMPORAL XGBOOST"
    )

    model = XGBClassifier(
        random_state=RANDOM_STATE,
        objective="binary:logistic",
        eval_metric="logloss",
        n_estimators=400,
        learning_rate=0.05,
        max_depth=10,
        min_child_weight=2,
        subsample=0.90,
        colsample_bytree=0.90,
        gamma=0,
        reg_alpha=0.10,
        reg_lambda=3.0,
        tree_method="hist",
        n_jobs=-1,
    )

    start_time = time.perf_counter()

    model.fit(
        X_train_transformed,
        y_train,
    )

    training_time = (
        time.perf_counter()
        - start_time
    )

    print(
        f"Training time: {training_time:.3f}s"
    )

    # ========================================================
    # VALIDATION THRESHOLD
    # ========================================================

    section("Validation threshold")

    val_probabilities = (
        model.predict_proba(
            X_val_transformed
        )[:, 1]
    )

    best_threshold = 0.50
    best_f1 = -1.0

    for threshold in np.arange(
        0.10,
        0.90 + 0.001,
        0.05,
    ):

        predictions = (
            val_probabilities
            >= threshold
        ).astype(int)

        score = f1_score(
            y_val,
            predictions,
            zero_division=0,
        )

        if score > best_f1:
            best_f1 = score
            best_threshold = float(
                threshold
            )

    print(
        f"Threshold : {best_threshold:.2f}"
    )

    print(
        f"Validation F1 : {best_f1:.6f}"
    )

    # ========================================================
    # TEST
    # ========================================================

    section(
        "[6] FROZEN-THRESHOLD TEST PREDICTIONS"
    )

    test_probabilities = (
        model.predict_proba(
            X_test_transformed
        )[:, 1]
    )

    test_predictions = (
        test_probabilities
        >= best_threshold
    ).astype(int)

    test_meta = test[
        [
            "record_id",
            "timestamp",
            "device_id",
            "sensor_code",
            "sensor_type",
            "value",
            "status",
            "sequence_number",
            "attack_type",
            "label",
        ]
    ].copy()

    test_meta["attack_probability"] = (
        test_probabilities
    )

    test_meta["prediction"] = (
        test_predictions
    )

    # ========================================================
    # OVERALL TEST METRICS
    # ========================================================

    section(
        "[7] OVERALL CONTROLLED TEMPORAL TEST"
    )

    accuracy = accuracy_score(
        y_test,
        test_predictions,
    )

    precision = precision_score(
        y_test,
        test_predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        test_predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        test_predictions,
        zero_division=0,
    )

    roc = roc_auc_score(
        y_test,
        test_probabilities,
    )

    print(
        f"Accuracy : {accuracy * 100:.2f}%"
    )

    print(
        f"Precision: {precision * 100:.2f}%"
    )

    print(
        f"Recall   : {recall * 100:.2f}%"
    )

    print(
        f"F1       : {f1 * 100:.2f}%"
    )

    print(
        f"ROC-AUC  : {roc:.5f}"
    )

    # ========================================================
    # NORMAL POST-SLOW-DRIFT REGION
    # ========================================================

    section(
        "[8] POST-SLOW-DRIFT NORMAL PERIOD"
    )

    post_slow = test_meta[
        (
            test_meta["record_id"]
            > slow_end
        )
        &
        (
            test_meta["label"]
            == 0
        )
    ].copy()

    first_normal_record = int(
        post_slow["record_id"].min()
    )

    last_normal_record = int(
        post_slow["record_id"].max()
    )

    print(
        f"Last Slow Drift record : {slow_end}"
    )

    print(
        f"First normal record    : {first_normal_record}"
    )

    print(
        f"Last normal record     : {last_normal_record}"
    )

    print(
        f"Normal records         : {len(post_slow):,}"
    )

    # ========================================================
    # WINDOW ANALYSIS
    # ========================================================

    windows = [
        ("FIRST 100", 100),
        ("FIRST 500", 500),
        ("FIRST 1,000", 1000),
        ("FIRST 2,000", 2000),
    ]

    results = []

    for name, window_size in windows:

        start_record = (
            slow_end + 1
        )

        end_record = (
            slow_end
            + window_size
        )

        window = post_slow[
            (
                post_slow["record_id"]
                >= start_record
            )
            &
            (
                post_slow["record_id"]
                <= end_record
            )
        ].copy()

        fp_count = int(
            (
                window["prediction"]
                == 1
            ).sum()
        )

        normal_count = len(
            window
        )

        fpr = (
            fp_count
            / normal_count
            * 100
            if normal_count
            else 0.0
        )

        results.append(
            {
                "window": name,
                "start": start_record,
                "end": end_record,
                "normal": normal_count,
                "false_positives": fp_count,
                "fpr": fpr,
            }
        )

        print()
        print(name)
        print("-" * 70)

        print(
            f"Record range       : "
            f"{start_record} -> {end_record}"
        )

        print(
            f"Normal records     : {normal_count}"
        )

        print(
            f"False positives    : {fp_count}"
        )

        print(
            f"FPR                : {fpr:.2f}%"
        )

        print(
            f"Mean probability   : "
            f"{window['attack_probability'].mean():.6f}"
        )

        print(
            f"Median probability : "
            f"{window['attack_probability'].median():.6f}"
        )

        print(
            f"Maximum probability: "
            f"{window['attack_probability'].max():.6f}"
        )

    # ========================================================
    # REMAINDER
    # ========================================================

    remainder_start = (
        slow_end + 2001
    )

    remainder = post_slow[
        post_slow["record_id"]
        >= remainder_start
    ].copy()

    remainder_fp = int(
        (
            remainder["prediction"]
            == 1
        ).sum()
    )

    remainder_fpr = (
        remainder_fp
        / len(remainder)
        * 100
        if len(remainder)
        else 0.0
    )

    print()
    print(
        "REMAINING NORMAL TEST PERIOD"
    )
    print("-" * 70)

    print(
        f"Record range       : "
        f"{remainder_start} -> {last_normal_record}"
    )

    print(
        f"Normal records     : {len(remainder):,}"
    )

    print(
        f"False positives    : {remainder_fp}"
    )

    print(
        f"FPR                : {remainder_fpr:.2f}%"
    )

    # ========================================================
    # FP CONCENTRATION
    # ========================================================

    section(
        "[9] FALSE-POSITIVE CONCENTRATION"
    )

    total_post_fp = int(
        (
            post_slow["prediction"]
            == 1
        ).sum()
    )

    print(
        f"Total post-transition FPs : "
        f"{total_post_fp}"
    )

    for result in results:

        count = result[
            "false_positives"
        ]

        percentage = (
            count
            / total_post_fp
            * 100
            if total_post_fp
            else 0.0
        )

        print(
            f"{result['window']:>12} : "
            f"{count:4d} FP "
            f"({percentage:6.2f}% of all FPs)"
        )

    print(
        f"{'REMAINDER':>12} : "
        f"{remainder_fp:4d} FP "
        f"({remainder_fp / total_post_fp * 100 if total_post_fp else 0.0:6.2f}% of all FPs)"
    )

    # ========================================================
    # DEVICE CONCENTRATION
    # ========================================================

    section(
        "[10] FALSE POSITIVES BY DEVICE"
    )

    fp_df = post_slow[
        post_slow["prediction"] == 1
    ]

    if fp_df.empty:
        print(
            "No false positives."
        )
    else:

        device_stats = (
            post_slow
            .groupby("device_id")
            .agg(
                normal=("prediction", "size"),
                false_positives=(
                    "prediction",
                    "sum",
                ),
            )
        )

        device_stats["fpr"] = (
            device_stats[
                "false_positives"
            ]
            /
            device_stats["normal"]
            * 100
        )

        device_stats = (
            device_stats
            .sort_values(
                "false_positives",
                ascending=False,
            )
        )

        print(
            device_stats.to_string()
        )

    # ========================================================
    # SENSOR TYPE
    # ========================================================

    section(
        "[11] FALSE POSITIVES BY SENSOR TYPE"
    )

    sensor_stats = (
        post_slow
        .groupby("sensor_type")
        .agg(
            normal=("prediction", "size"),
            false_positives=(
                "prediction",
                "sum",
            ),
        )
    )

    sensor_stats["fpr"] = (
        sensor_stats[
            "false_positives"
        ]
        /
        sensor_stats["normal"]
        * 100
    )

    sensor_stats = (
        sensor_stats
        .sort_values(
            "false_positives",
            ascending=False,
        )
    )

    print(
        sensor_stats.to_string()
    )

    # ========================================================
    # HIGH-PROBABILITY FP RECORDS
    # ========================================================

    section(
        "[12] HIGHEST-PROBABILITY FALSE POSITIVES"
    )

    if fp_df.empty:

        print(
            "No false positives."
        )

    else:

        display_columns = [
            "record_id",
            "timestamp",
            "device_id",
            "sensor_code",
            "sensor_type",
            "value",
            "sequence_number",
            "attack_probability",
        ]

        print(
            fp_df
            .sort_values(
                "attack_probability",
                ascending=False,
            )
            [display_columns]
            .head(30)
            .to_string(
                index=False
            )
        )

    # ========================================================
    # FINAL INTERPRETATION
    # ========================================================

    section(
        "[13] DIAGNOSTIC INTERPRETATION"
    )

    first_100_fp = results[0][
        "false_positives"
    ]

    first_500_fp = results[1][
        "false_positives"
    ]

    first_1000_fp = results[2][
        "false_positives"
    ]

    first_2000_fp = results[3][
        "false_positives"
    ]

    first_2000_share = (
        first_2000_fp
        / total_post_fp
        * 100
        if total_post_fp
        else 0.0
    )

    print(
        f"First 100 FP        : {first_100_fp}"
    )

    print(
        f"First 500 FP        : {first_500_fp}"
    )

    print(
        f"First 1,000 FP      : {first_1000_fp}"
    )

    print(
        f"First 2,000 FP      : {first_2000_fp}"
    )

    print(
        f"First 2,000 FP share: "
        f"{first_2000_share:.2f}%"
    )

    print()

    if (
        first_2000_share
        >= 50.0
    ):
        print(
            "FINDING:"
        )
        print(
            "False positives are strongly concentrated "
            "near the Slow Drift -> Normal transition."
        )
        print(
            "This supports a campaign-transition / "
            "distribution-shift hypothesis."
        )

    elif (
        first_2000_share
        >= 30.0
    ):
        print(
            "FINDING:"
        )
        print(
            "A substantial fraction of false positives "
            "occurs near the transition."
        )
        print(
            "However, the remainder still contributes "
            "meaningful false positives."
        )
        print(
            "The evidence therefore supports a mixed "
            "transition + broader distribution-shift explanation."
        )

    else:
        print(
            "FINDING:"
        )
        print(
            "False positives are not predominantly "
            "concentrated in the immediate transition window."
        )
        print(
            "A broader normal-distribution shift or "
            "sensor-specific behavior should be investigated."
        )

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "This diagnostic does not modify the dataset, "
        "labels, features, threshold, or model."
    )

    print(
        "It is an analysis-only experiment."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()