"""
Feature Importance Analyzer

Generates feature importance reports for supported
tree-based machine learning models.
"""

import logging

import matplotlib.pyplot as plt
import pandas as pd

from backend.ml.config import REPORT_DIR

logger = logging.getLogger(__name__)


class FeatureImportanceAnalyzer:
    """
    Generates feature importance reports
    for tree-based models.
    """

    def analyze(
        self,
        pipeline,
        feature_names=None,
        model_name: str = "model",
    ):
        """
        Generate feature importance report.
        """

        classifier = pipeline.named_steps["classifier"]

        # -------------------------------------------------
        # Check Model Support
        # -------------------------------------------------

        if not hasattr(
            classifier,
            "feature_importances_",
        ):

            logger.info(
                "%s does not support feature importance.",
                model_name,
            )

            return None

        # -------------------------------------------------
        # Get Feature Names
        # -------------------------------------------------

        if feature_names is None:

            try:

                preprocessor = pipeline.named_steps[
                    "preprocessor"
                ]

                feature_names = (
                    preprocessor.get_feature_names_out()
                )

            except Exception:

                logger.warning(
                    "Unable to obtain transformed feature names."
                )

                feature_names = [
                    f"Feature_{i}"
                    for i in range(
                        len(
                            classifier.feature_importances_
                        )
                    )
                ]

        importance = classifier.feature_importances_

        # -------------------------------------------------
        # Safety Check
        # -------------------------------------------------

        if len(feature_names) != len(importance):

            logger.warning(
                "Feature mismatch (%d != %d)",
                len(feature_names),
                len(importance),
            )

            minimum = min(
                len(feature_names),
                len(importance),
            )

            feature_names = feature_names[:minimum]
            importance = importance[:minimum]

        # -------------------------------------------------
        # Create DataFrame
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Save Reports
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Plot Top 20 Features
        # -------------------------------------------------

        fig, ax = plt.subplots(
            figsize=(12, 8),
        )

        top = df.head(20)

        ax.barh(
            top["Feature"],
            top["Importance"],
        )

        ax.invert_yaxis()

        ax.set_title(
            f"{model_name} Feature Importance"
        )

        ax.set_xlabel(
            "Importance Score"
        )

        fig.tight_layout()

        fig.savefig(
            image_path,
            dpi=300,
        )

        plt.close(fig)

        # -------------------------------------------------
        # Logging
        # -------------------------------------------------

        logger.info(
            "Feature importance generated for %s",
            model_name,
        )

        logger.info(
            "CSV : %s",
            csv_path.name,
        )

        logger.info(
            "PNG : %s",
            image_path.name,
        )

        return df