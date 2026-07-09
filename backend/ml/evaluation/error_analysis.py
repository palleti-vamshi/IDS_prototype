"""
Error Analysis

Generates detailed evaluation reports for trained
machine learning models.
"""

import logging

import matplotlib.pyplot as plt
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    PrecisionRecallDisplay,
    RocCurveDisplay,
    classification_report,
    confusion_matrix,
)

from backend.ml.config import REPORT_DIR

logger = logging.getLogger(__name__)


class ErrorAnalyzer:
    """
    Generates detailed evaluation reports.
    """

    def analyze(
        self,
        pipeline,
        X_test,
        y_test,
        model_name: str,
    ):

        logger.info(
            "Running error analysis for %s...",
            model_name,
        )

        REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -------------------------------------------------
        # Predictions
        # -------------------------------------------------

        y_pred = pipeline.predict(
            X_test,
        )

        # -------------------------------------------------
        # Classification Report
        # -------------------------------------------------

        report = classification_report(
            y_test,
            y_pred,
            digits=4,
        )

        report_path = (
            REPORT_DIR
            / f"{model_name}_classification_report.txt"
        )

        with open(
            report_path,
            "w",
        ) as file:

            file.write(report)

        # -------------------------------------------------
        # Confusion Matrix
        # -------------------------------------------------

        fig, ax = plt.subplots(
            figsize=(6, 6),
        )

        ConfusionMatrixDisplay(
            confusion_matrix=confusion_matrix(
                y_test,
                y_pred,
            )
        ).plot(
            ax=ax,
        )

        fig.tight_layout()

        fig.savefig(
            REPORT_DIR
            / f"{model_name}_confusion_matrix.png",
            dpi=300,
        )

        plt.close(fig)

        # -------------------------------------------------
        # ROC & Precision-Recall Curves
        # -------------------------------------------------

        if hasattr(
            pipeline,
            "predict_proba",
        ):

            # ROC Curve

            fig, ax = plt.subplots(
                figsize=(6, 6),
            )

            RocCurveDisplay.from_estimator(
                pipeline,
                X_test,
                y_test,
                ax=ax,
            )

            fig.tight_layout()

            fig.savefig(
                REPORT_DIR
                / f"{model_name}_roc_curve.png",
                dpi=300,
            )

            plt.close(fig)

            # Precision-Recall Curve

            fig, ax = plt.subplots(
                figsize=(6, 6),
            )

            PrecisionRecallDisplay.from_estimator(
                pipeline,
                X_test,
                y_test,
                ax=ax,
            )

            fig.tight_layout()

            fig.savefig(
                REPORT_DIR
                / f"{model_name}_precision_recall_curve.png",
                dpi=300,
            )

            plt.close(fig)

        logger.info(
            "Error analysis completed for %s.",
            model_name,
        )