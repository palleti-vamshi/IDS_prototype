"""
LightX-IDS Benchmark Runner

Trains, evaluates, benchmarks and saves all supported
machine learning models.
"""

import logging
from pathlib import Path

from backend.ml.config import (
    LIGHTX_1K,
    LIGHTX_10K,
    LIGHTX_100K,
    BENCHMARK_1K,
    BENCHMARK_10K,
    BENCHMARK_100K,
)

from backend.ml.evaluation import evaluator
from backend.ml.evaluation.evaluation_manager import (
    EvaluationManager,
)
from backend.ml.experiments.results import ResultManager

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

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s - %(message)s",
)


def run_benchmark(
    dataset_path: Path,
    benchmark_name: str,
):

    print("\n" + "=" * 110)
    print(
        f"LIGHTX-IDS BENCHMARK : {benchmark_name.upper()}"
    )
    print("=" * 110)

    # ---------------------------------------------------------
    # Dataset
    # ---------------------------------------------------------

    loader = DatasetLoader()

    df = loader.load(
        dataset_path,
    )

    # ---------------------------------------------------------
    # Feature Engineering
    # ---------------------------------------------------------

    df = FeatureGenerator().transform(
        df,
    )


    # ---------------------------------------------------------
    # Feature Selection
    # ---------------------------------------------------------

    X, y = FeatureSelector().split(
        df,
    )

    # ---------------------------------------------------------
    # Dataset Split
    # ---------------------------------------------------------

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = DatasetSplitter().split(
        X,
        y,
    )

    trainer = ModelTrainer()

    evaluation_manager = EvaluationManager()


    factory = ModelFactory()

    manager = ModelManager()

    results = ResultManager()

    leaderboard = []

    print()

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

    # ---------------------------------------------------------
    # Train Every Model
    # ---------------------------------------------------------

    for model_name in factory.available_models():

        model = factory.get(
            model_name,
        )

        pipeline = MLPipeline().build(
            model,
        )

        pipeline, training_time = trainer.train(
            pipeline,
            X_train,
            y_train,
            model_name=model_name,
        )

        evaluation = evaluation_manager.evaluate(
            pipeline,
            X_test,
            y_test,
            model_name=model_name,
        )


        metadata = {

            "model": model_name,

            "accuracy": evaluation["accuracy"],

            "precision": evaluation["precision"],

            "recall": evaluation["recall"],

            "f1_score": evaluation["f1_score"],

            "roc_auc": evaluation["roc_auc"],

            "training_time": training_time,

            "prediction_time": evaluation[
                "prediction_time"
            ],
        }

        manager.save(
            pipeline,
            model_name,
            metadata,
        )

        metadata[
            "model_size_mb"
        ] = manager.size_mb(
            model_name,
        )

        leaderboard.append(
            metadata,
        )

        results.add(
            metadata,
        )

    # ===== CONTINUE WITH PART 2 =====

    # ---------------------------------------------------------
    # Ranking
    # ---------------------------------------------------------

    leaderboard.sort(
        key=lambda x: x["accuracy"],
        reverse=True,
    )

    for rank, row in enumerate(
        leaderboard,
        start=1,
    ):

        print(
            f"{rank:<6}"
            f"{row['model']:<24}"
            f"{row['accuracy']*100:<11.2f}%"
            f"{row['precision']*100:<11.2f}%"
            f"{row['recall']*100:<11.2f}%"
            f"{row['f1_score']*100:<11.2f}"
            f"{row['training_time']:<12.4f}"
            f"{row['model_size_mb']:<10.3f}"
        )

    print("-" * len(header))

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    best = max(
        leaderboard,
        key=lambda x: x["accuracy"],
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
        f"Best Accuracy   : "
        f"{best['model']} "
        f"({best['accuracy']*100:.2f}%)"
    )

    print(
        f"Fastest Training: "
        f"{fastest['model']} "
        f"({fastest['training_time']:.4f} sec)"
    )

    print(
        f"Smallest Model  : "
        f"{smallest['model']} "
        f"({smallest['model_size_mb']:.3f} MB)"
    )

    # ---------------------------------------------------------
    # Save Reports
    # ---------------------------------------------------------

    csv_file, json_file = results.save(
        benchmark_name,
    )

    print("\n📄 Reports")
    print(f"CSV  : {csv_file.name}")
    print(f"JSON : {json_file.name}")

    print("\n💾 Models")
    print("Saved in backend/ml/saved_models")

    print("\n✅ Benchmark Completed Successfully")


def main():

    run_benchmark(
        LIGHTX_100K,
        BENCHMARK_100K,
    )


if __name__ == "__main__":
    main()