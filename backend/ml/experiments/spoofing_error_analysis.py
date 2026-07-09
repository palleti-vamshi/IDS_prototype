"""
LightX-IDS Spoofing Error Analysis

Compares correctly classified and misclassified
Spoofing attacks.
"""

import logging

import pandas as pd

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


def print_summary(title, dataframe):

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    print(f"Samples : {len(dataframe)}")

    print("\nDevice IDs")
    print(
        dataframe["device_id"]
        .value_counts(dropna=False)
    )

    print("\nSensor Types")
    print(
        dataframe["sensor_type"]
        .value_counts(dropna=False)
    )

    features = [
        "value",
        "value_change",
        "time_delta",
        "rolling_mean",
        "rolling_std",
        "rolling_max",
        "rolling_min",
        "percentage_change",
        "z_score",
    ]

    print("\nFeature Statistics")
    print(
        dataframe[features]
        .describe()
        .round(3)
    )


def main():

    print("\n" + "=" * 80)
    print("LIGHTX-IDS SPOOFING ERROR ANALYSIS")
    print("=" * 80)

    loader = DatasetLoader()

    original_df = loader.load(
        LIGHTX_100K,
    )

    engineered_df = FeatureGenerator().transform(
        original_df
    )

    X, y = FeatureSelector().split(
        engineered_df
    )

    (
        X_train,
        _,
        X_test,
        y_train,
        _,
        y_test,
    ) = DatasetSplitter().split(
        X,
        y,
    )

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

    predictions = pipeline.predict(
        X_test
    )

    test_df = engineered_df.loc[
        X_test.index
    ].copy()

    test_df["actual"] = y_test.values

    test_df["predicted"] = predictions

    spoofing = test_df[
        test_df["attack_type"]
        == "Spoofing Attack"
    ]

    correct = spoofing[
        spoofing["actual"]
        == spoofing["predicted"]
    ]

    incorrect = spoofing[
        spoofing["actual"]
        != spoofing["predicted"]
    ]

    print_summary(
        "CORRECTLY CLASSIFIED SPOOFING",
        correct,
    )

    print_summary(
        "MISCLASSIFIED SPOOFING",
        incorrect,
    )


if __name__ == "__main__":
    main()