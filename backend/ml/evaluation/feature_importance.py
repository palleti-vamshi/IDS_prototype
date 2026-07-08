"""
Feature Importance Analyzer

Generates feature importance reports for supported
tree-based machine learning models.
"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from backend.ml.config import REPORT_DIR

logger = logging.getLogger(__name__)


class FeatureImportanceAnalyzer:
    """
    Generates feature importance CSV and chart.
    """

    def analyze(
        self,
        pipeline,
        feature_names,
        model_name: str,
    ):

        classifier = pipeline.named_steps["classifier"]

        if not hasattr(
            classifier,
            "feature_importances_",
        ):

            logger.info(
                "%s does not support feature importance.",
                model_name,
            )

            return None

        importance = classifier.feature_importances_

        # Safety check
        if len(feature_names) != len(importance):

            logger.warning(
                "Feature count mismatch "
                "(%d != %d).",
                len(feature_names),
                len(importance),
            )

            minimum = min(
                len(feature_names),
                len(importance),
            )

            feature_names = feature_names[:minimum]
            importance = importance[:minimum]

        df = pd.DataFrame(
            {
                "Feature": feature_names,
                "Importance": importance,
            }
        )

        df.sort_values(
            by="Importance",
            ascending=False,
            inplace=True,
        )

        REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        csv_path = (
            REPORT_DIR
            / f"{model_name}_feature_importance.csv"
        )

        image_path = (
            REPORT_DIR
            / f"{model_name}_feature_importance.png"
        )

        df.to_csv(
            csv_path,
            index=False,
        )

        plt.figure(
            figsize=(12, 8),
        )

        top = df.head(20)

        plt.barh(
            top["Feature"],
            top["Importance"],
        )

        plt.gca().invert_yaxis()

        plt.title(
            f"{model_name} Feature Importance"
        )

        plt.xlabel(
            "Importance Score"
        )

        plt.tight_layout()

        plt.savefig(
            image_path,
            dpi=300,
        )

        plt.close()

        logger.info(
            "Feature importance exported: %s",
            model_name,
        )

        return df