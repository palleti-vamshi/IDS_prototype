"""
LightX-IDS
Final Temporal False-Positive Feature Carryover Diagnostic

READ-ONLY ANALYSIS

Goal:
Determine whether false positives in the controlled temporal
experiment are primarily associated with:
    1. residual/carryover attack-state feature signatures after
       Slow Drift ends, or
    2. broader normal-distribution shift later in the test stream.

IMPORTANT:
- Does NOT modify dataset
- Does NOT modify labels
- Does NOT modify project ML files
- Does NOT modify threshold
- Does NOT save models
- Does NOT save datasets
"""

from pathlib import Path

import numpy as np
import pandas as pd

from xgboost import XGBClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import f1_score


# ============================================================
# CONFIGURATION
# ============================================================

DATASET = Path("dataset/lightx_ids_dataset_100k.csv")

TRAIN_END = 89000
VAL_START = 89001
VAL_END = 90000
TEST_START = 90001
TEST_END = 100000

THRESHOLD_MIN = 0.10
THRESHOLD_MAX = 0.90
THRESHOLD_STEP = 0.05

SLOW_DRIFT_NAME = "Slow Drift Attack"

# Same controlled temporal XGBoost protocol
XGB_PARAMS = dict(
    random_state=42,
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
    reg_lambda=3,
    tree_method="hist",
    n_jobs=-1,
)


# ============================================================
# HELPERS
# ============================================================

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reproduce the controlled temporal 40-feature construction.
    """

    df = df.copy()

    df.sort_values("record_id", inplace=True)

    df["ts"] = pd.to_datetime(df["timestamp"], errors="raise")
    df["value"] = pd.to_numeric(df["value"], errors="raise")

    # --------------------------------------------------------
    # Communication / sequence features
    # --------------------------------------------------------

    df["device_seq_gap"] = (
        df.groupby("device_id")["sequence_number"]
        .diff()
        .fillna(19.0)
    )

    df["seq_gap_dev"] = (
        df["device_seq_gap"] - 19.0
    ).abs()

    df["rolling_seq_std_5"] = (
        df.groupby("device_id")["device_seq_gap"]
        .rolling(5, min_periods=1)
        .std()
        .fillna(0)
        .reset_index(level=0, drop=True)
    )

    # --------------------------------------------------------
    # Timing features
    # --------------------------------------------------------

    df["time_delta"] = (
        df.groupby("device_id")["ts"]
        .diff()
        .dt.total_seconds()
        .fillna(0)
    )

    df["is_negative_time_delta"] = (
        df["time_delta"] < 0
    ).astype(int)

    df["global_time_delta"] = (
        df["ts"]
        .diff()
        .dt.total_seconds()
        .fillna(0)
    )

    df["rolling_global_td_10"] = (
        df["global_time_delta"]
        .rolling(10, min_periods=1)
        .mean()
        .fillna(0)
    )

    df["rolling_time_delta_5"] = (
        df.groupby("device_id")["time_delta"]
        .rolling(5, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["rolling_time_delta_std_5"] = (
        df.groupby("device_id")["time_delta"]
        .rolling(5, min_periods=1)
        .std()
        .fillna(0)
        .reset_index(level=0, drop=True)
    )

    df["rolling_global_td_std_10"] = (
        df["global_time_delta"]
        .rolling(10, min_periods=1)
        .std()
        .fillna(0)
    )

    df["packet_rate_10"] = (
        1.0
        / (df["rolling_global_td_10"].abs() + 1e-4)
    )

    # --------------------------------------------------------
    # Physical/value dynamics
    # --------------------------------------------------------

    df["value_change"] = (
        df.groupby("device_id")["value"]
        .diff()
        .fillna(0)
    )

    df["abs_value_change"] = (
        df["value_change"].abs()
    )

    df["value_accel"] = (
        df.groupby("device_id")["value_change"]
        .diff()
        .fillna(0)
    )

    df["is_duplicate_value"] = (
        df["value_change"] == 0
    ).astype(int)

    # --------------------------------------------------------
    # Multi-window physical features
    # --------------------------------------------------------

    for w in [3, 5, 10]:

        df[f"rolling_mean_{w}"] = (
            df.groupby("device_id")["value"]
            .rolling(w, min_periods=1)
            .mean()
            .reset_index(level=0, drop=True)
        )

        df[f"rolling_std_{w}"] = (
            df.groupby("device_id")["value"]
            .rolling(w, min_periods=1)
            .std()
            .fillna(0)
            .reset_index(level=0, drop=True)
        )

    df["rolling_range_5"] = (
        df.groupby("device_id")["value"]
        .rolling(5, min_periods=1)
        .max()
        .reset_index(level=0, drop=True)
        -
        df.groupby("device_id")["value"]
        .rolling(5, min_periods=1)
        .min()
        .reset_index(level=0, drop=True)
    )

    # --------------------------------------------------------
    # Plant-wide duplicate behavior
    # --------------------------------------------------------

    df["plant_duplicate_ratio_19"] = (
        df["is_duplicate_value"]
        .rolling(19, min_periods=1)
        .mean()
        .fillna(0)
    )

    df["percentage_change"] = (
        df.groupby("device_id")["value"]
        .pct_change()
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    return df


def add_train_only_sensor_statistics(
    train_df: pd.DataFrame,
    other_dfs: list[pd.DataFrame],
):
    """
    Fit device-level statistics ONLY on training data.
    """

    train_stats = (
        train_df
        .groupby("device_id")["value"]
        .agg(["mean", "std"])
        .to_dict(orient="index")
    )

    # Training duplicate rate
    train_diff = (
        train_df.groupby("device_id")["value"]
        .diff()
        .fillna(1)
    )

    duplicate_rates = (
        (train_diff == 0)
        .groupby(train_df["device_id"])
        .mean()
        .to_dict()
    )

    outputs = []

    for split_df in [train_df] + other_dfs:

        split_df = split_df.copy()

        def get_mean(device):
            return train_stats.get(
                device,
                {}
            ).get("mean", 0.0)

        def get_std(device):
            value = train_stats.get(
                device,
                {}
            ).get("std", 1.0)

            if not np.isfinite(value) or value == 0:
                return 1.0

            return value

        def get_dup_rate(device):
            return duplicate_rates.get(
                device,
                0.5
            )

        sensor_mean = (
            split_df["device_id"]
            .map(get_mean)
            .fillna(0.0)
        )

        sensor_std = (
            split_df["device_id"]
            .map(get_std)
            .replace(0, 1.0)
            .fillna(1.0)
        )

        duplicate_rate = (
            split_df["device_id"]
            .map(get_dup_rate)
            .fillna(0.5)
        )

        split_df["device_mean_deviation"] = (
            split_df["value"] - sensor_mean
        )

        split_df["z_score"] = (
            (split_df["value"] - sensor_mean)
            / sensor_std
        )

        split_df["rel_volatility"] = (
            split_df["rolling_std_5"]
            / sensor_std
        )

        split_df["stability_anomaly"] = (
            split_df["is_duplicate_value"]
            * (1.0 - duplicate_rate)
        )

        outputs.append(split_df)

    return outputs


def make_preprocessor(num_cols, cat_cols):

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                num_cols,
            ),
            (
                "categorical",
                categorical_pipeline,
                cat_cols,
            ),
        ],
        remainder="drop",
    )


def threshold_search(y_true, probabilities):

    best_threshold = 0.50
    best_f1 = -1

    thresholds = np.arange(
        THRESHOLD_MIN,
        THRESHOLD_MAX + 1e-9,
        THRESHOLD_STEP,
    )

    for threshold in thresholds:

        predictions = (
            probabilities >= threshold
        ).astype(int)

        score = f1_score(
            y_true,
            predictions,
            zero_division=0,
        )

        if score > best_f1:
            best_f1 = score
            best_threshold = float(
                round(threshold, 2)
            )

    return best_threshold, best_f1


def feature_comparison(
    df,
    fp_mask,
    reference_mask,
    features,
    title,
):

    print()
    print("=" * 100)
    print(title)
    print("=" * 100)

    rows = []

    for feature in features:

        fp_values = pd.to_numeric(
            df.loc[fp_mask, feature],
            errors="coerce",
        )

        ref_values = pd.to_numeric(
            df.loc[reference_mask, feature],
            errors="coerce",
        )

        fp_values = fp_values.replace(
            [np.inf, -np.inf],
            np.nan,
        ).dropna()

        ref_values = ref_values.replace(
            [np.inf, -np.inf],
            np.nan,
        ).dropna()

        if len(fp_values) == 0 or len(ref_values) == 0:
            continue

        fp_mean = fp_values.mean()
        ref_mean = ref_values.mean()

        fp_std = fp_values.std()
        ref_std = ref_values.std()

        pooled = np.sqrt(
            (
                fp_std ** 2
                +
                ref_std ** 2
            ) / 2
        )

        if pooled == 0 or not np.isfinite(pooled):
            standardized = 0.0
        else:
            standardized = (
                fp_mean - ref_mean
            ) / pooled

        rows.append(
            {
                "feature": feature,
                "fp_mean": fp_mean,
                "reference_mean": ref_mean,
                "difference": fp_mean - ref_mean,
                "standardized_difference": standardized,
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        print("No comparable numeric features.")
        return

    result["abs_standardized_difference"] = (
        result["standardized_difference"].abs()
    )

    result.sort_values(
        "abs_standardized_difference",
        ascending=False,
        inplace=True,
    )

    print(
        result.head(15).to_string(
            index=False
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 100)
    print("LIGHTX-IDS FINAL FP FEATURE-CARRYOVER DIAGNOSTIC")
    print("=" * 100)
    print("READ-ONLY ANALYSIS")
    print(f"Dataset: {DATASET.resolve()}")

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    print()
    print("[1] LOAD DATASET")
    print("-" * 100)

    df = pd.read_csv(DATASET)

    print(f"Dataset shape: {df.shape}")

    df.sort_values(
        "record_id",
        inplace=True,
    )

    # --------------------------------------------------------
    # Slow Drift boundary
    # --------------------------------------------------------

    slow = df[
        df["attack_type"]
        == SLOW_DRIFT_NAME
    ]

    if slow.empty:
        raise RuntimeError(
            f"Attack type '{SLOW_DRIFT_NAME}' not found."
        )

    slow_start = int(
        slow["record_id"].min()
    )

    slow_end = int(
        slow["record_id"].max()
    )

    print()
    print("Slow Drift boundary")
    print("-" * 100)
    print(f"Slow Drift start : {slow_start}")
    print(f"Slow Drift end   : {slow_end}")

    # --------------------------------------------------------
    # Temporal split
    # --------------------------------------------------------

    train = df[
        df["record_id"].between(
            1,
            TRAIN_END,
        )
    ].copy()

    val = df[
        df["record_id"].between(
            VAL_START,
            VAL_END,
        )
    ].copy()

    test = df[
        df["record_id"].between(
            TEST_START,
            TEST_END,
        )
    ].copy()

    print()
    print("Temporal split")
    print("-" * 100)
    print(
        f"Train      : 1 -> {TRAIN_END} "
        f"({len(train):,})"
    )
    print(
        f"Validation : {VAL_START} -> {VAL_END} "
        f"({len(val):,})"
    )
    print(
        f"Test       : {TEST_START} -> {TEST_END} "
        f"({len(test):,})"
    )

    print(
        "Slow Drift in training:",
        int(
            (
                train["attack_type"]
                == SLOW_DRIFT_NAME
            ).sum()
        ),
    )

    # --------------------------------------------------------
    # Generate features over COMPLETE chronological stream
    # --------------------------------------------------------

    print()
    print("[2] GENERATE CAUSAL FEATURES")
    print("-" * 100)
    print(
        "Generating features over the complete "
        "chronological stream..."
    )

    featured = generate_features(df)

    # Preserve record identity
    featured.sort_values(
        "record_id",
        inplace=True,
    )

    train_f = featured[
        featured["record_id"]
        <= TRAIN_END
    ].copy()

    val_f = featured[
        featured["record_id"].between(
            VAL_START,
            VAL_END,
        )
    ].copy()

    test_f = featured[
        featured["record_id"]
        >= TEST_START
    ].copy()

    # --------------------------------------------------------
    # Train-only statistics
    # --------------------------------------------------------

    print()
    print("[3] FIT TRAINING-ONLY SENSOR STATISTICS")
    print("-" * 100)

    train_f, val_f, test_f = (
        add_train_only_sensor_statistics(
            train_f,
            [val_f, test_f],
        )
    )

    # --------------------------------------------------------
    # Feature definition
    # --------------------------------------------------------

    num_cols = [
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

    cat_cols = [
        "topic",
        "device_id",
        "sensor_code",
        "sensor_type",
        "unit",
        "status",
        "source",
    ]

    print(
        f"ML numeric features : {len(num_cols)}"
    )
    print(
        f"ML categorical features : {len(cat_cols)}"
    )
    print(
        f"Total raw ML features : "
        f"{len(num_cols) + len(cat_cols)}"
    )

    # --------------------------------------------------------
    # Preprocessing
    # --------------------------------------------------------

    print()
    print("[4] PREPROCESSING")
    print("-" * 100)

    preprocessor = make_preprocessor(
        num_cols,
        cat_cols,
    )

    X_train = train_f[
        num_cols + cat_cols
    ]

    X_val = val_f[
        num_cols + cat_cols
    ]

    X_test = test_f[
        num_cols + cat_cols
    ]

    y_train = train_f["label"]
    y_val = val_f["label"]
    y_test = test_f["label"]

    X_train_t = preprocessor.fit_transform(
        X_train
    )

    X_val_t = preprocessor.transform(
        X_val
    )

    X_test_t = preprocessor.transform(
        X_test
    )

    print(
        "Training matrix:",
        X_train_t.shape,
    )
    print(
        "Validation matrix:",
        X_val_t.shape,
    )
    print(
        "Test matrix:",
        X_test_t.shape,
    )

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    print()
    print("[5] TRAIN CONTROLLED TEMPORAL XGBOOST")
    print("-" * 100)

    model = XGBClassifier(
        **XGB_PARAMS
    )

    model.fit(
        X_train_t,
        y_train,
    )

    # --------------------------------------------------------
    # Validation threshold
    # --------------------------------------------------------

    val_prob = model.predict_proba(
        X_val_t
    )[:, 1]

    threshold, val_f1 = threshold_search(
        y_val,
        val_prob,
    )

    print()
    print("Validation threshold")
    print("-" * 100)
    print(f"Threshold : {threshold:.2f}")
    print(f"Validation F1 : {val_f1:.6f}")

    # --------------------------------------------------------
    # Test predictions
    # --------------------------------------------------------

    test_prob = model.predict_proba(
        X_test_t
    )[:, 1]

    test_pred = (
        test_prob >= threshold
    ).astype(int)

    test_f = test_f.copy()

    test_f["attack_probability"] = (
        test_prob
    )

    test_f["prediction"] = (
        test_pred
    )

    # --------------------------------------------------------
    # Identify FP
    # --------------------------------------------------------

    normal_mask = (
        test_f["label"] == 0
    )

    fp_mask = (
        normal_mask
        & (test_f["prediction"] == 1)
    )

    slow_mask = (
        test_f["attack_type"]
        == SLOW_DRIFT_NAME
    )

    print()
    print("[6] OVERALL TEST")
    print("-" * 100)

    print(
        f"Accuracy : "
        f"{((test_pred == y_test).mean() * 100):.2f}%"
    )

    print(
        f"F1       : "
        f"{f1_score(y_test, test_pred):.4f}"
    )

    print(
        f"Normal test records : "
        f"{normal_mask.sum():,}"
    )

    print(
        f"False positives     : "
        f"{fp_mask.sum():,}"
    )

    # --------------------------------------------------------
    # Compare feature distributions
    # --------------------------------------------------------

    print()
    print("[7] FEATURE CARRYOVER ANALYSIS")
    print("-" * 100)

    # First 100 normal after Slow Drift
    first100 = (
        (test_f["record_id"] >= slow_end + 1)
        &
        (test_f["record_id"] <= slow_end + 100)
        &
        normal_mask
    )

    first500 = (
        (test_f["record_id"] >= slow_end + 1)
        &
        (test_f["record_id"] <= slow_end + 500)
        &
        normal_mask
    )

    first2000 = (
        (test_f["record_id"] >= slow_end + 1)
        &
        (test_f["record_id"] <= slow_end + 2000)
        &
        normal_mask
    )

    later_normal = (
        (test_f["record_id"] >= slow_end + 2001)
        &
        normal_mask
    )

    slow_test = (
        slow_mask
    )

    # False positives in each region
    fp_first100 = first100 & fp_mask
    fp_first500 = first500 & fp_mask
    fp_first2000 = first2000 & fp_mask
    fp_later = later_normal & fp_mask

    print(
        f"FP first 100   : {fp_first100.sum():,}"
    )
    print(
        f"FP first 500   : {fp_first500.sum():,}"
    )
    print(
        f"FP first 2000  : {fp_first2000.sum():,}"
    )
    print(
        f"FP later       : {fp_later.sum():,}"
    )

    # --------------------------------------------------------
    # Feature groups
    # --------------------------------------------------------

    timing_features = [
        "time_delta",
        "global_time_delta",
        "rolling_global_td_10",
        "rolling_time_delta_5",
        "rolling_time_delta_std_5",
        "rolling_global_td_std_10",
        "packet_rate_10",
        "is_negative_time_delta",
    ]

    communication_features = [
        "device_seq_gap",
        "seq_gap_dev",
        "rolling_seq_std_5",
        "plant_duplicate_ratio_19",
    ]

    physical_features = [
        "value_change",
        "abs_value_change",
        "value_accel",
        "rolling_mean_3",
        "rolling_std_3",
        "rolling_mean_5",
        "rolling_std_5",
        "rolling_mean_10",
        "rolling_std_10",
        "rolling_range_5",
        "percentage_change",
    ]

    sensor_features = [
        "device_mean_deviation",
        "z_score",
        "rel_volatility",
        "stability_anomaly",
    ]

    # --------------------------------------------------------
    # FP vs immediately preceding Slow Drift
    # --------------------------------------------------------

    feature_comparison(
        test_f,
        fp_first100,
        slow_test,
        timing_features,
        "TIMING: FIRST-100 FALSE POSITIVES vs SLOW DRIFT",
    )

    feature_comparison(
        test_f,
        fp_first100,
        slow_test,
        communication_features,
        "COMMUNICATION: FIRST-100 FALSE POSITIVES vs SLOW DRIFT",
    )

    feature_comparison(
        test_f,
        fp_first100,
        slow_test,
        physical_features,
        "PHYSICAL: FIRST-100 FALSE POSITIVES vs SLOW DRIFT",
    )

    feature_comparison(
        test_f,
        fp_first100,
        slow_test,
        sensor_features,
        "SENSOR-AWARE: FIRST-100 FALSE POSITIVES vs SLOW DRIFT",
    )

    # --------------------------------------------------------
    # Early FP vs later normal
    # --------------------------------------------------------

    feature_comparison(
        test_f,
        fp_first2000,
        later_normal,
        timing_features,
        "TIMING: FIRST-2000 FALSE POSITIVES vs LATER NORMAL",
    )

    feature_comparison(
        test_f,
        fp_first2000,
        later_normal,
        communication_features,
        "COMMUNICATION: FIRST-2000 FALSE POSITIVES vs LATER NORMAL",
    )

    feature_comparison(
        test_f,
        fp_first2000,
        later_normal,
        physical_features,
        "PHYSICAL: FIRST-2000 FALSE POSITIVES vs LATER NORMAL",
    )

    feature_comparison(
        test_f,
        fp_first2000,
        later_normal,
        sensor_features,
        "SENSOR-AWARE: FIRST-2000 FALSE POSITIVES vs LATER NORMAL",
    )

    # --------------------------------------------------------
    # Later FP vs later correct normal
    # --------------------------------------------------------

    later_correct_normal = (
        later_normal
        & (test_f["prediction"] == 0)
    )

    feature_comparison(
        test_f,
        fp_later,
        later_correct_normal,
        timing_features,
        "TIMING: LATER FALSE POSITIVES vs LATER CORRECT NORMAL",
    )

    feature_comparison(
        test_f,
        fp_later,
        later_correct_normal,
        communication_features,
        "COMMUNICATION: LATER FALSE POSITIVES vs LATER CORRECT NORMAL",
    )

    feature_comparison(
        test_f,
        fp_later,
        later_correct_normal,
        physical_features,
        "PHYSICAL: LATER FALSE POSITIVES vs LATER CORRECT NORMAL",
    )

    feature_comparison(
        test_f,
        fp_later,
        later_correct_normal,
        sensor_features,
        "SENSOR-AWARE: LATER FALSE POSITIVES vs LATER CORRECT NORMAL",
    )

    # --------------------------------------------------------
    # Probability comparison
    # --------------------------------------------------------

    print()
    print("[8] PROBABILITY COMPARISON")
    print("-" * 100)

    for name, mask in [
        ("Slow Drift", slow_test),
        ("First 100 normal", first100),
        ("First 2000 normal", first2000),
        ("Later normal FP", fp_later),
        ("Later correct normal", later_correct_normal),
    ]:

        values = test_f.loc[
            mask,
            "attack_probability",
        ]

        if len(values) == 0:
            continue

        print()
        print(name)
        print(
            f"  count  : {len(values):,}"
        )
        print(
            f"  mean   : {values.mean():.6f}"
        )
        print(
            f"  median : {values.median():.6f}"
        )
        print(
            f"  p90    : {values.quantile(.90):.6f}"
        )
        print(
            f"  p99    : {values.quantile(.99):.6f}"
        )
        print(
            f"  max    : {values.max():.6f}"
        )

    # --------------------------------------------------------
    # Final interpretation
    # --------------------------------------------------------

    print()
    print("=" * 100)
    print("FINAL DIAGNOSTIC INTERPRETATION")
    print("=" * 100)

    early_fp = int(fp_first2000.sum())
    later_fp = int(fp_later.sum())
    total_fp = int(fp_mask.sum())

    if total_fp > 0:
        early_share = (
            100.0 * early_fp / total_fp
        )
    else:
        early_share = 0.0

    print()
    print(
        f"Total false positives : {total_fp}"
    )
    print(
        f"First 2,000 FP        : {early_fp}"
    )
    print(
        f"Later FP              : {later_fp}"
    )
    print(
        f"Early FP share        : {early_share:.2f}%"
    )

    print()
    print("Interpretation must be based on the feature comparisons above.")
    print()
    print(
        "If early FPs strongly resemble Slow Drift across timing/"
        "communication features while later FPs resemble later-normal "
        "distribution, this supports a transition/carryover effect."
    )
    print()
    print(
        "If later FPs remain strongly separated from later-correct-normal "
        "records in their own feature distributions, this supports a "
        "broader normal distribution shift."
    )
    print()
    print(
        "If both patterns are present, the evidence supports a mixed "
        "transition + broader distribution-shift explanation."
    )

    print()
    print("IMPORTANT:")
    print(
        "This diagnostic does not modify the dataset, labels, "
        "features, threshold, or model."
    )
    print("Analysis only.")


if __name__ == "__main__":
    main()