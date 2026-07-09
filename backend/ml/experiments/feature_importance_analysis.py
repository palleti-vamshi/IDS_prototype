"""
LightX-IDS Feature Importance Analysis

Ranks transformed features using the trained
Random Forest model.
"""

import logging

import pandas as pd

from backend.ml.config import (
    LIGHTX_100K,
    REPORT_DIR,
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
from backend.ml.training.trainer import (
    ModelTrainer,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():

    print("\n" + "=" * 80)
    print("LIGHTX-IDS FEATURE IMPORTANCE ANALYSIS")
    print("=" * 80)

    df = DatasetLoader().load(
        LIGHTX_100K,
    )

    df = FeatureGenerator().transform(
        df,
    )

    X, y = FeatureSelector().split(
        df,
    )

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

    model = ModelFactory().get(
        "random_forest",
    )

    pipeline = MLPipeline().build(
        model,
    )

    trainer = ModelTrainer()

    pipeline, _ = trainer.train(
        pipeline,
        X_train,
        y_train,
        model_name="random_forest",
    )

    preprocessor = pipeline.named_steps[
        "preprocessor"
    ]

    classifier = pipeline.named_steps[
        "classifier"
    ]

    feature_names = (
        preprocessor.get_feature_names_out()
    )

    print()

    print(
        f"Original Features    : {len(X.columns)}"
    )

    print(
        f"Transformed Features : {len(feature_names)}"
    )

    print(
        f"Feature Importances  : "
        f"{len(classifier.feature_importances_)}"
    )

    importance = pd.DataFrame(
        {
            "Feature": feature_names,
            "Importance": classifier.feature_importances_,
        }
    )

    importance = importance.sort_values(
        by="Importance",
        ascending=False,
    )

    print()
    print(importance)

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = (
        REPORT_DIR
        / "feature_importance.csv"
    )

    importance.to_csv(
        csv_path,
        index=False,
    )

    print("\n" + "=" * 80)
    print("REPORT SAVED")
    print("=" * 80)
    print(csv_path)


if __name__ == "__main__":
    main()