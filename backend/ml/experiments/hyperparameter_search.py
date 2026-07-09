"""
Decision Tree Hyperparameter Search

Searches for the best Decision Tree hyperparameters
for the LightX-IDS dataset.
"""

import logging

from backend.ml.config import LIGHTX_100K
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
from backend.ml.training.hyperparameter_optimizer import (
    HyperparameterOptimizer,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)


def main():

    print("\n" + "=" * 70)
    print("LIGHTX-IDS LOGISTIC REGRESSION HYPERPARAMETER SEARCH")
    print("=" * 70)

    # ---------------------------------------------------------
    # Dataset
    # ---------------------------------------------------------

    loader = DatasetLoader()

    df = loader.load(
        LIGHTX_100K,
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
        _,
        _,
        y_train,
        _,
        _,
    ) = DatasetSplitter().split(
        X,
        y,
    )

    # ---------------------------------------------------------
    # Model
    # ---------------------------------------------------------

    model = ModelFactory().get(
        "logistic_regression",
    )

    pipeline = MLPipeline().build(
        model,
    )

    # ---------------------------------------------------------
    # Hyperparameter Optimization
    # ---------------------------------------------------------

    optimizer = HyperparameterOptimizer()

    best_pipeline, best_parameters = optimizer.optimize(
        pipeline=pipeline,
        X_train=X_train,
        y_train=y_train,
        model_name="logistic_regression",
    )

    print()

    print("=" * 70)
    print("BEST PARAMETERS")
    print("=" * 70)

    for key, value in best_parameters.items():

        print(f"{key:<35} : {value}")

    print("=" * 70)

    print("\nSearch Completed Successfully.\n")


if __name__ == "__main__":
    main()