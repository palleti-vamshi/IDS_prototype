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
    LIGHTX_REQUIRED_COLUMNS,
    BENCHMARK_10K,
    RANDOM_STATE,
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
) -> None:
    """
    Run the complete LightX-IDS ML benchmark.

    The raw dataset is split BEFORE feature engineering so that
    training-derived statistics cannot use validation/test data.
    """

    print("\n" + "=" * 110)

    print(
        f"LIGHTX-IDS BENCHMARK : "
        f"{benchmark_name.upper()}"
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
    # RAW DATASET SPLIT
    # ========================================================

    splitter = DatasetSplitter()

    X_raw = df.drop(
        columns=["label"],
    )

    y_raw = df["label"]

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
    # FEATURE ENGINEERING
    # ========================================================

    feature_generator = FeatureGenerator()

    # --------------------------------------------------------
    # Fit ONLY on training data
    # --------------------------------------------------------

    feature_generator.fit(
        X_train_raw,
    )

    # --------------------------------------------------------
    # Transform each split independently
    # --------------------------------------------------------

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
    # FEATURE SELECTION
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

    print(
        f"ML features        : "
        f"{len(X_train.columns)}"
    )

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

    trainer = ModelTrainer()

    evaluation_manager = EvaluationManager()

    factory = ModelFactory()

    manager = ModelManager()

    results = ResultManager()

    leaderboard = []

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

        pipeline = MLPipeline().build(
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

            "split_protocol": "80/10/10 stratified",

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


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """
    Default Phase 4 experiment.

    We intentionally run the finalized 10K dataset first.
    The 100K experiment will be executed only after the 10K
    pipeline has been validated.
    """

    run_benchmark(
        LIGHTX_10K,
        BENCHMARK_10K,
    )


if __name__ == "__main__":
    main()