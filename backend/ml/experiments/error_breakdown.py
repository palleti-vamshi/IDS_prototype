"""
LightX-IDS Error Breakdown

Shows which attack types are being misclassified
by the XGBoost model.
"""

import logging

import pandas as pd

from sklearn.metrics import confusion_matrix

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
from backend.ml.training.trainer import (
    ModelTrainer,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)


def main():

    print("\n" + "=" * 80)
    print("LIGHTX-IDS ERROR BREAKDOWN")
    print("=" * 80)

    # ---------------------------------------------------------
    # Load Dataset
    # ---------------------------------------------------------

    loader = DatasetLoader()

    df = loader.load(
        LIGHTX_100K,
    )

    # Keep attack type before feature engineering
    attack_type = df["attack_type"].copy()

    # ---------------------------------------------------------
    # Feature Engineering
    # ---------------------------------------------------------

    df = FeatureGenerator().transform(
        df,
    )

    X, y = FeatureSelector().split(
        df,
    )

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

    # Match attack types with test indices
    attack_test = attack_type.loc[
        X_test.index
    ]

    # ---------------------------------------------------------
    # Train XGBoost
    # ---------------------------------------------------------

    model = ModelFactory().get(
        "xgboost",
    )

    pipeline = MLPipeline().build(
        model,
    )

    trainer = ModelTrainer()

    pipeline, _ = trainer.train(
        pipeline,
        X_train,
        y_train,
        model_name="xgboost",
    )

    # ---------------------------------------------------------
    # Prediction
    # ---------------------------------------------------------

    predictions = pipeline.predict(
        X_test,
    )

    # ---------------------------------------------------------
    # Confusion Matrix
    # ---------------------------------------------------------

    cm = confusion_matrix(
        y_test,
        predictions,
    )

    print("\nConfusion Matrix\n")
    print(cm)

    # ---------------------------------------------------------
    # Error Samples
    # ---------------------------------------------------------

    result = pd.DataFrame({

        "Actual": y_test,

        "Predicted": predictions,

        "Attack Type": attack_test,

    })

    errors = result[
        result["Actual"] != result["Predicted"]
    ]

    print("\n")
    print("=" * 80)
    print("MISCLASSIFIED ATTACK TYPES")
    print("=" * 80)

    if errors.empty:

        print("No misclassifications.")

    else:

        print(
            errors["Attack Type"]
            .fillna("NORMAL")
            .value_counts()
        )

    print("\n")
    print("=" * 80)
    print("TOP 20 MISCLASSIFIED SAMPLES")
    print("=" * 80)

    print(
        errors.head(20)
    )


if __name__ == "__main__":
    main()