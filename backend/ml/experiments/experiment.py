"""
LightX-IDS Benchmark Runner

Trains, evaluates, benchmarks and saves all supported
machine learning models.

Phase 4 protocol:

1. Load and validate the raw dataset.
2. Split the raw dataset into train/validation/test.
3. Fit feature-generation statistics on training data only.
4. Generate features independently for train/validation/test.
5. Select ML features.
6. Train all supported models.
7. Select the operating threshold using validation data.
8. Evaluate once on the untouched test set.
9. Save models, metadata and benchmark reports.
"""

import logging
from pathlib import Path

from backend.ml.config import (
    LIGHTX_10K,
    LIGHTX_100K,
    LIGHTX_REQUIRED_COLUMNS,
    BENCHMARK_10K,
    BENCHMARK_100K,
    NUMERIC_COLUMNS,
    CATEGORICAL_COLUMNS,
    RANDOM_STATE,
)
from backend.ml.preprocessing.transformer import (
    DatasetTransformer,
)

from backend.ml.evaluation.evaluation_manager import (
    EvaluationManager,
)

from backend.ml.experiments.results import (
    ResultManager,
)

from backend.ml.feature_engineering.feature_generator import (
    FeatureGenerator,
)

from backend.ml.feature_engineering.feature_selector import (
    FeatureSelector,
)

from backend.ml.models.model_factory import (
    ModelFactory,
)

from backend.ml.preprocessing.loader import (
    DatasetLoader,
)

from backend.ml.preprocessing.pipeline import (
    MLPipeline,
)

from backend.ml.preprocessing.splitter import (
    DatasetSplitter,
)

from backend.ml.training.model_manager import (
    ModelManager,
)

from backend.ml.training.trainer import (
    ModelTrainer,
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# BENCHMARK
# ============================================================

def run_benchmark(
    dataset_path: Path,
    benchmark_name: str,
    split_protocol: str = "stratified",
    ablation: str | None = None,
) -> list[dict]:
    """
    Run the complete LightX-IDS ML benchmark.

    Causal features are computed along the continuous chronological stream.
    Training-derived statistics and transformers are fit strictly on training data.
    """

    print("\n" + "=" * 110)

    print(
        f"LIGHTX-IDS BENCHMARK : "
        f"{benchmark_name.upper()} (split={split_protocol}, ablation={ablation or 'none'})"
    )

    print("=" * 110)

    # ========================================================
    # DATASET
    # ========================================================

    loader = DatasetLoader()

    df = loader.load(
        dataset_path,
        required_columns=LIGHTX_REQUIRED_COLUMNS,
    )

    print(
        f"\nDataset : {dataset_path.name}"
    )

    print(
        f"Records : {len(df):,}"
    )

    # --------------------------------------------------------
    # Basic target validation
    # --------------------------------------------------------

    if "label" not in df.columns:
        raise ValueError(
            "Dataset does not contain required target column: label"
        )

    labels = set(
        df["label"]
        .dropna()
        .unique()
        .tolist()
    )

    if not labels.issubset({0, 1}):
        raise ValueError(
            "LightX-IDS label column must contain only "
            "binary values 0 and 1. "
            f"Found: {sorted(labels)}"
        )

    if df["label"].isnull().any():
        raise ValueError(
            "LightX-IDS label column contains null values."
        )

    # ========================================================
    # CAUSAL STREAM FEATURES & SPLIT
    # ========================================================

    feature_generator = FeatureGenerator()
    df_stream = feature_generator.generate_causal_stream_features(df)

    splitter = DatasetSplitter()

    X_raw = df_stream.drop(
        columns=["label"],
    )

    y_raw = df_stream["label"]

    if split_protocol == "temporal":
        (
            X_train_raw,
            X_val_raw,
            X_test_raw,
            y_train,
            y_val,
            y_test,
        ) = splitter.temporal_split(
            X_raw,
            y_raw,
        )
    else:
        (
            X_train_raw,
            X_val_raw,
            X_test_raw,
            y_train,
            y_val,
            y_test,
        ) = splitter.split(
            X_raw,
            y_raw,
        )

    print("\nDataset Split")
    print("-" * 35)

    print(
        f"Train      : {len(X_train_raw):,}"
    )

    print(
        f"Validation : {len(X_val_raw):,}"
    )

    print(
        f"Test       : {len(X_test_raw):,}"
    )

    # ========================================================
    # FEATURE ENGINEERING (FIT ON TRAIN ONLY)
    # ========================================================

    # Fit ONLY on training data
    feature_generator.fit(
        X_train_raw,
    )

    # Transform each split independently
    X_train_features = (
        feature_generator.transform(
            X_train_raw,
        )
    )

    X_val_features = (
        feature_generator.transform(
            X_val_raw,
        )
    )

    X_test_features = (
        feature_generator.transform(
            X_test_raw,
        )
    )

    print("\nFeature Engineering")
    print("-" * 35)

    print(
        f"Generated features : "
        f"{len(X_train_features.columns)}"
    )

    # ========================================================
    # FEATURE SELECTION & ABLATION
    # ========================================================

    selector = FeatureSelector()

    X_train, y_train = selector.split(
        X_train_features.assign(
            label=y_train.values,
        )
    )

    X_val, y_val = selector.split(
        X_val_features.assign(
            label=y_val.values,
        )
    )

    X_test, y_test = selector.split(
        X_test_features.assign(
            label=y_test.values,
        )
    )

    if ablation == "no_sensor_code":
        drop_ablation = ["sensor_code"]
        X_train = X_train.drop(columns=[c for c in drop_ablation if c in X_train.columns])
        X_val = X_val.drop(columns=[c for c in drop_ablation if c in X_val.columns])
        X_test = X_test.drop(columns=[c for c in drop_ablation if c in X_test.columns])
    elif ablation == "no_identity":
        drop_ablation = ["device_id", "sensor_code", "topic"]
        X_train = X_train.drop(columns=[c for c in drop_ablation if c in X_train.columns])
        X_val = X_val.drop(columns=[c for c in drop_ablation if c in X_val.columns])
        X_test = X_test.drop(columns=[c for c in drop_ablation if c in X_test.columns])
    elif ablation == "baseline_features":
        keep_num = [
            "value", "value_change", "time_delta", "is_duplicate_value",
            "rolling_mean", "rolling_std", "rolling_max", "rolling_min",
            "percentage_change", "z_score", "device_mean_deviation"
        ]
        drop_ablation = [c for c in X_train.columns if c in NUMERIC_COLUMNS and c not in keep_num]
        X_train = X_train.drop(columns=[c for c in drop_ablation if c in X_train.columns])
        X_val = X_val.drop(columns=[c for c in drop_ablation if c in X_val.columns])
        X_test = X_test.drop(columns=[c for c in drop_ablation if c in X_test.columns])
    elif ablation == "no_communication":
        drop_ablation = [
            "device_seq_gap", "seq_gap_dev", "rolling_seq_std_5",
            "is_negative_time_delta", "global_time_delta", "rolling_global_td_10",
            "rolling_time_delta_5", "rolling_time_delta_std_5",
            "rolling_global_td_std_10", "packet_rate_10"
        ]
        X_train = X_train.drop(columns=[c for c in drop_ablation if c in X_train.columns])
        X_val = X_val.drop(columns=[c for c in drop_ablation if c in X_val.columns])
        X_test = X_test.drop(columns=[c for c in drop_ablation if c in X_test.columns])
    elif ablation == "no_new_timing":
        drop_ablation = [
            "rolling_time_delta_5", "rolling_time_delta_std_5",
            "rolling_global_td_std_10", "packet_rate_10"
        ]
        X_train = X_train.drop(columns=[c for c in drop_ablation if c in X_train.columns])
        X_val = X_val.drop(columns=[c for c in drop_ablation if c in X_val.columns])
        X_test = X_test.drop(columns=[c for c in drop_ablation if c in X_test.columns])
    elif ablation == "no_multiwindow":
        drop_ablation = [
            "rolling_mean_3", "rolling_std_3", "rolling_mean_10", "rolling_std_10",
            "rolling_range_5", "plant_duplicate_ratio_19", "value_accel", "abs_value_change"
        ]
        X_train = X_train.drop(columns=[c for c in drop_ablation if c in X_train.columns])
        X_val = X_val.drop(columns=[c for c in drop_ablation if c in X_val.columns])
        X_test = X_test.drop(columns=[c for c in drop_ablation if c in X_test.columns])
    elif ablation == "no_sensor_baselines":
        drop_ablation = ["rel_volatility", "stability_anomaly", "z_score", "device_mean_deviation"]
        X_train = X_train.drop(columns=[c for c in drop_ablation if c in X_train.columns])
        X_val = X_val.drop(columns=[c for c in drop_ablation if c in X_val.columns])
        X_test = X_test.drop(columns=[c for c in drop_ablation if c in X_test.columns])
    elif ablation == "no_physical_dynamics":
        drop_ablation = [
            "value_change", "abs_value_change", "value_accel",
            "percentage_change", "rolling_range_5"
        ]
        X_train = X_train.drop(columns=[c for c in drop_ablation if c in X_train.columns])
        X_val = X_val.drop(columns=[c for c in drop_ablation if c in X_val.columns])
        X_test = X_test.drop(columns=[c for c in drop_ablation if c in X_test.columns])
    elif ablation == "no_plant_wide":
        drop_ablation = ["plant_duplicate_ratio_19", "rolling_global_td_10", "rolling_global_td_std_10", "packet_rate_10"]
        X_train = X_train.drop(columns=[c for c in drop_ablation if c in X_train.columns])
        X_val = X_val.drop(columns=[c for c in drop_ablation if c in X_val.columns])
        X_test = X_test.drop(columns=[c for c in drop_ablation if c in X_test.columns])

    print(
        f"ML features        : "
        f"{len(X_train.columns)}"
    )

    meta_cols = [c for c in ["record_id", "timestamp", "device_id", "sensor_code", "sensor_type", "attack_type", "label"] if c in df.columns]
    test_metadata = df.loc[X_test_raw.index, meta_cols].copy()

    # --------------------------------------------------------
    # Verify feature alignment
    # --------------------------------------------------------

    train_columns = list(
        X_train.columns
    )

    validation_columns = list(
        X_val.columns
    )

    test_columns = list(
        X_test.columns
    )

    if train_columns != validation_columns:
        raise ValueError(
            "Training and validation feature columns do not match."
        )

    if train_columns != test_columns:
        raise ValueError(
            "Training and test feature columns do not match."
        )

    # ========================================================
    # MODEL COMPONENTS
    # ========================================================

    # ========================================================
    # MODEL COMPONENTS
    # ========================================================

    trainer = ModelTrainer()

    evaluation_manager = EvaluationManager()

    factory = ModelFactory()

    manager = ModelManager()

    results = ResultManager()

    leaderboard = []

    # Build preprocessing transformer using active features
    active_num = [c for c in NUMERIC_COLUMNS if c in X_train.columns]
    active_cat = [c for c in CATEGORICAL_COLUMNS if c in X_train.columns]
    custom_transformer = DatasetTransformer(
        numeric_features=active_num,
        categorical_features=active_cat,
    ).build()

    # ========================================================
    # TRAIN EVERY MODEL
    # ========================================================

    for model_name in factory.available_models():

        print(
            f"\nTraining {model_name}..."
        )

        # ----------------------------------------------------
        # Create model
        # ----------------------------------------------------

        model = factory.get(
            model_name,
        )

        # ----------------------------------------------------
        # Build preprocessing + model pipeline
        # ----------------------------------------------------

        pipeline = MLPipeline(
            transformer=custom_transformer,
        ).build(
            model,
        )

        # ----------------------------------------------------
        # Train
        # ----------------------------------------------------

        pipeline, training_time = trainer.train(
            pipeline,
            X_train,
            y_train,
            model_name=model_name,
        )

        # ----------------------------------------------------
        # Validation + Test Evaluation
        # ----------------------------------------------------

        evaluation = evaluation_manager.evaluate(
            pipeline=pipeline,
            X_val=X_val,
            y_val=y_val,
            X_test=X_test,
            y_test=y_test,
            model_name=model_name,
            metadata=test_metadata,
        )

        # ----------------------------------------------------
        # Model Size
        # ----------------------------------------------------

        model_size_mb = manager.size_mb(
            model_name,
        )

        # ----------------------------------------------------
        # Benchmark Metadata
        # ----------------------------------------------------

        metadata = {

            # Identification
            "model": model_name,

            "dataset": dataset_path.name,

            "benchmark": benchmark_name,

            # Dataset information
            "dataset_size": len(df),

            "train_size": len(X_train),

            "validation_size": len(X_val),

            "test_size": len(X_test),

            "feature_count": len(X_train.columns),

            # Split configuration
            "random_state": RANDOM_STATE,

            "split_protocol": f"80/10/10 {split_protocol}",

            "ablation": ablation or "none",

            # Threshold configuration
            "threshold_metric": evaluation[
                "threshold_metric"
            ],

            "best_threshold": evaluation[
                "best_threshold"
            ],

            "validation_threshold_score": evaluation[
                "validation_threshold_score"
            ],

            # Core metrics
            "accuracy": evaluation[
                "accuracy"
            ],

            "precision": evaluation[
                "precision"
            ],

            "recall": evaluation[
                "recall"
            ],

            "f1_score": evaluation[
                "f1_score"
            ],

            # Probability metrics
            "roc_auc": evaluation[
                "roc_auc"
            ],

            "pr_auc": evaluation[
                "pr_auc"
            ],

            # IDS error metrics
            "fpr": evaluation[
                "false_positive_rate"
            ],

            "fnr": evaluation[
                "false_negative_rate"
            ],

            # Confusion matrix
            "tn": evaluation[
                "true_negative"
            ],

            "fp": evaluation[
                "false_positive"
            ],

            "fn": evaluation[
                "false_negative"
            ],

            "tp": evaluation[
                "true_positive"
            ],

            # Runtime
            "training_time": training_time,

            "prediction_time": evaluation[
                "prediction_time"
            ],

            "model_size_mb": model_size_mb,
        }

        # ----------------------------------------------------
        # Save trained pipeline + complete metadata
        # ----------------------------------------------------

        manager.save(
            pipeline,
            model_name,
            metadata,
        )

        # ----------------------------------------------------
        # Store Results
        # ----------------------------------------------------

        leaderboard.append(
            metadata,
        )

        results.add(
            metadata,
        )

    # ========================================================
    # RANKING
    # ========================================================

    leaderboard.sort(
        key=lambda x: (
            x["accuracy"],
            x["f1_score"],
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # Print final benchmark table AFTER all training
    # --------------------------------------------------------

    print("\n")

    header = (
        f"{'Rank':<6}"
        f"{'Model':<24}"
        f"{'Accuracy':<12}"
        f"{'Precision':<12}"
        f"{'Recall':<12}"
        f"{'F1':<12}"
        f"{'Train(s)':<12}"
        f"{'Size(MB)':<10}"
    )

    print(header)

    print("-" * len(header))

    for rank, row in enumerate(
        leaderboard,
        start=1,
    ):

        print(
            f"{rank:<6}"
            f"{row['model']:<24}"
            f"{row['accuracy'] * 100:<11.2f}%"
            f"{row['precision'] * 100:<11.2f}%"
            f"{row['recall'] * 100:<11.2f}%"
            f"{row['f1_score'] * 100:<11.2f}"
            f"{row['training_time']:<12.4f}"
            f"{row['model_size_mb']:<10.3f}"
        )

    print(
        "-" * len(header)
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    if not leaderboard:
        raise RuntimeError(
            "No benchmark results were produced."
        )

    best = max(
        leaderboard,
        key=lambda x: (
            x["accuracy"],
            x["f1_score"],
        ),
    )

    fastest = min(
        leaderboard,
        key=lambda x: x["training_time"],
    )

    smallest = min(
        leaderboard,
        key=lambda x: x["model_size_mb"],
    )

    print("\n🏆 SUMMARY")
    print("-" * 35)

    print(
        f"Highest Accuracy : "
        f"{best['model']} "
        f"({best['accuracy'] * 100:.2f}%)"
    )

    print(
        f"Fastest Training : "
        f"{fastest['model']} "
        f"({fastest['training_time']:.4f} sec)"
    )

    print(
        f"Smallest Model   : "
        f"{smallest['model']} "
        f"({smallest['model_size_mb']:.3f} MB)"
    )

    # ========================================================
    # SAVE REPORTS
    # ========================================================

    csv_file, json_file = results.save(
        benchmark_name,
    )

    print("\n📄 Reports")

    print(
        f"CSV  : {csv_file.name}"
    )

    print(
        f"JSON : {json_file.name}"
    )

    print("\n💾 Models")

    print(
        "Saved in backend/ml/saved_models"
    )

    print(
        "\n✅ Benchmark Completed Successfully"
    )

    return leaderboard


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """
    Default Phase 4 authoritative benchmark on 100K dataset.
    """

    run_benchmark(
        LIGHTX_100K,
        BENCHMARK_100K,
        split_protocol="stratified",
    )


if __name__ == "__main__":
    main()