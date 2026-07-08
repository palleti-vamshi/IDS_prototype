"""
TON-IoT Benchmark Runner

Trains, evaluates and benchmarks all supported
machine learning models on the TON-IoT dataset.
"""

import logging

from sklearn.model_selection import train_test_split

from backend.ml.evaluation.evaluator import ModelEvaluator
from backend.ml.experiments.results import ResultManager
from backend.ml.models.model_factory import ModelFactory
from backend.ml.preprocessing.loader import DatasetLoader
from backend.ml.training.model_manager import ModelManager
from backend.ml.training.trainer import ModelTrainer

from backend.ml.ton_iot.config import (
    DATASET_PATH,
    DROP_COLUMNS,
    RANDOM_STATE,
    TARGET_COLUMN,
    TEST_SIZE,
    VALIDATION_SIZE,
)

from backend.ml.ton_iot.pipeline import TONPipeline
from backend.ml.ton_iot.printer import BenchmarkPrinter


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)


def main():

    printer = BenchmarkPrinter()

    # ---------------------------------------------------------
    # Dataset
    # ---------------------------------------------------------

    from backend.ml.ton_iot.feature_generator import (
    TONFeatureGenerator,
    )

    loader = DatasetLoader()

    df = loader.load(DATASET_PATH)

    feature_generator = TONFeatureGenerator()

    df = feature_generator.transform(df)

    X = df.drop(
        columns=DROP_COLUMNS + [TARGET_COLUMN],
    )

    y = df[TARGET_COLUMN]

    # ---------------------------------------------------------
    # Dataset Split
    # ---------------------------------------------------------

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    validation_ratio = (
        VALIDATION_SIZE / TEST_SIZE
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=validation_ratio,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    # ---------------------------------------------------------
    # ML Objects
    # ---------------------------------------------------------

    trainer = ModelTrainer()

    evaluator = ModelEvaluator()

    factory = ModelFactory()

    manager = ModelManager()

    results = ResultManager()

    leaderboard = []

    # ---------------------------------------------------------
    # Train Models
    # ---------------------------------------------------------

    for model_name in factory.available_models():

        model = factory.get(
            model_name,
        )

        pipeline = TONPipeline().build(
            model,
        )

        pipeline, training_time = trainer.train(
            pipeline,
            X_train,
            y_train,
            model_name=model_name,
        )

        evaluation = evaluator.evaluate(
            pipeline,
            X_test,
            y_test,
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
            f"ton_{model_name}",
            metadata,
        )

        metadata[
            "model_size_mb"
        ] = manager.size_mb(
            f"ton_{model_name}"
        )

        leaderboard.append(
            metadata,
        )

        results.add(
            metadata,
        )

    # ---------------------------------------------------------
    # Ranking
    # ---------------------------------------------------------

    leaderboard.sort(
        key=lambda item: item["accuracy"],
        reverse=True,
    )


    # ---------------------------------------------------------
    # Printer
    # ---------------------------------------------------------

    printer.title()

    printer.dataset(
        rows=len(df),
        columns=len(df.columns),
        train=len(X_train),
        validation=len(X_val),
        test=len(X_test),
    )

    printer.table_header()

    for rank, row in enumerate(
        leaderboard,
        start=1,
    ):
        printer.row(
            rank,
            row,
        )

    printer.summary(
        leaderboard,
    )

    # ---------------------------------------------------------
    # Export Reports
    # ---------------------------------------------------------

    csv_file, json_file = results.save(
        "benchmark_ton_iot",
    )

    printer.reports(
        csv_file,
        json_file,
    )

    printer.models()

    printer.completed()


if __name__ == "__main__":
    main()