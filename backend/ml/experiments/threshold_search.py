"""
LightX-IDS Threshold Optimization

Searches for the best classification threshold
for all supported machine learning models.
"""

import logging

import pandas as pd

from backend.ml.config import (
    LIGHTX_100K,
    REPORT_DIR,
)

from backend.ml.preprocessing.loader import (
    DatasetLoader,
)

from backend.ml.feature_engineering.feature_generator import (
    FeatureGenerator,
)

from backend.ml.feature_engineering.feature_selector import (
    FeatureSelector,
)

from backend.ml.preprocessing.splitter import (
    DatasetSplitter,
)

from backend.ml.models.model_factory import (
    ModelFactory,
)

from backend.ml.preprocessing.pipeline import (
    MLPipeline,
)

from backend.ml.training.trainer import (
    ModelTrainer,
)

from backend.ml.evaluation.evaluator import (
    ModelEvaluator,
)

from backend.ml.optimization.threshold_optimizer import (
    ThresholdOptimizer,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():

    print("\n" + "=" * 80)
    print("LIGHTX-IDS THRESHOLD OPTIMIZATION")
    print("=" * 80)

    # ---------------------------------------------------------
    # Dataset
    # ---------------------------------------------------------

    from backend.ml.config import (
        LIGHTX_REQUIRED_COLUMNS,
        PRIMARY_THRESHOLD_METRIC,
    )

    df = DatasetLoader().load(
        LIGHTX_100K,
        required_columns=LIGHTX_REQUIRED_COLUMNS,
    )

    # ---------------------------------------------------------
    # Causal Stream Features & Dataset Split
    # ---------------------------------------------------------

    generator = FeatureGenerator()
    df_stream = generator.generate_causal_stream_features(df)

    X_raw = df_stream.drop(columns=["label"])
    y_raw = df_stream["label"]

    (
        X_train_raw,
        X_val_raw,
        X_test_raw,
        y_train,
        y_val,
        y_test,
    ) = DatasetSplitter().split(
        X_raw,
        y_raw,
    )

    # ---------------------------------------------------------
    # Feature Engineering (Fit on Train ONLY)
    # ---------------------------------------------------------

    generator.fit(X_train_raw)

    X_train_features = generator.transform(X_train_raw)
    X_val_features = generator.transform(X_val_raw)
    X_test_features = generator.transform(X_test_raw)

    # ---------------------------------------------------------
    # Feature Selection
    # ---------------------------------------------------------

    selector = FeatureSelector()

    X_train, y_train = selector.split(
        X_train_features.assign(label=y_train.values)
    )
    X_val, y_val = selector.split(
        X_val_features.assign(label=y_val.values)
    )
    X_test, y_test = selector.split(
        X_test_features.assign(label=y_test.values)
    )

    trainer = ModelTrainer()

    evaluator = ModelEvaluator()

    optimizer = ThresholdOptimizer()

    factory = ModelFactory()

    summary = []

    for model_name in factory.available_models():

        print("\n" + "-" * 80)
        print(model_name.upper())
        print("-" * 80)

        model = factory.get(
            model_name,
        )

        pipeline = MLPipeline().build(
            model,
        )

        pipeline, _ = trainer.train(
            pipeline,
            X_train,
            y_train,
            model_name=model_name,
        )

        # -----------------------------------------------------
        # Default Evaluation (Threshold = 0.50)
        # -----------------------------------------------------

        default_results = evaluator.evaluate(
            pipeline=pipeline,
            X_test=X_test,
            y_test=y_test,
        )

        # -----------------------------------------------------
        # Threshold Optimization (Validation ONLY, metric=PRIMARY_THRESHOLD_METRIC)
        # -----------------------------------------------------

        optimization = optimizer.optimize(
            pipeline=pipeline,
            X_val=X_val,
            y_val=y_val,
            model_name=model_name,
            metric=PRIMARY_THRESHOLD_METRIC,
        )

        if optimization is None:

            print(
                f"{model_name} does not support "
                "probability predictions."
            )

            continue

        best_threshold = optimization[
            "best_threshold"
        ]

        # -----------------------------------------------------
        # Optimized Evaluation
        # -----------------------------------------------------

        optimized_results = (
            optimizer.evaluate_threshold(
                pipeline=pipeline,
                X_test=X_test,
                y_test=y_test,
                threshold=best_threshold,
            )
        )

        # -----------------------------------------------------
        # Console Output
        # -----------------------------------------------------

        print(
            f"Best Threshold : "
            f"{best_threshold:.2f}"
        )

        print(
            f"Default Accuracy   : "
            f"{default_results['accuracy']*100:.2f}%"
        )

        print(
            f"Optimized Accuracy : "
            f"{optimized_results['accuracy']*100:.2f}%"
        )

        print(
            f"Default F1   : "
            f"{default_results['f1_score']*100:.2f}%"
        )

        print(
            f"Optimized F1 : "
            f"{optimized_results['f1_score']*100:.2f}%"
        )

        summary.append(

            {

                "Model": model_name,

                "Threshold": best_threshold,

                "Default Accuracy":
                    default_results["accuracy"],

                "Optimized Accuracy":
                    optimized_results["accuracy"],

                "Default F1":
                    default_results["f1_score"],

                "Optimized F1":
                    optimized_results["f1_score"],
            }

        )

    # ---------------------------------------------------------
    # Summary Report
    # ---------------------------------------------------------

    report = pd.DataFrame(
        summary,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report.to_csv(

        REPORT_DIR /
        "threshold_summary.csv",

        index=False,

    )

    print("\n")
    print("=" * 90)
    print("THRESHOLD OPTIMIZATION SUMMARY")
    print("=" * 90)

    print(report)

    print("\n")
    print(
        "Report saved to:"
    )

    print(
        REPORT_DIR /
        "threshold_summary.csv"
    )


if __name__ == "__main__":

    main()
