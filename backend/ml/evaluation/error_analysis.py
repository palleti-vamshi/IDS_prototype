"""
Error Analysis

Generates detailed evaluation reports for trained
machine-learning models.

All classification/error reports use the same threshold
selected from the validation dataset.
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
        threshold: float = 0.50,
    ):
        """
        Generate error-analysis reports.

        Parameters
        ----------
        pipeline
            Trained sklearn pipeline.

        X_test
            Test features.

        y_test
            Test labels.

        model_name : str
            Model identifier.

        threshold : float
            Frozen classification threshold selected using
            validation data.
        """

        logger.info(
            "Running error analysis for %s "
            "(threshold=%.4f)...",
            model_name,
            threshold,
        )

        REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ====================================================
        # PREDICTIONS
        # ====================================================

        probabilities = None

        if hasattr(
            pipeline,
            "predict_proba",
        ):

            probabilities = (
                pipeline.predict_proba(
                    X_test,
                )[:, 1]
            )

            y_pred = (
                probabilities >= threshold
            ).astype(int)

        else:

            y_pred = pipeline.predict(
                X_test,
            )

        # ====================================================
        # CLASSIFICATION REPORT
        # ====================================================

        report = classification_report(
            y_test,
            y_pred,
            digits=4,
            zero_division=0,
        )

        report_path = (
            REPORT_DIR
            / f"{model_name}_classification_report.txt"
        )

        with open(
            report_path,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                f"Model: {model_name}\n"
            )

            file.write(
                f"Threshold: {threshold:.6f}\n\n"
            )

            file.write(
                report
            )

        # ====================================================
        # CONFUSION MATRIX
        # ====================================================

        matrix = confusion_matrix(
            y_test,
            y_pred,
            labels=[0, 1],
        )

        fig, ax = plt.subplots(
            figsize=(6, 6),
        )

        ConfusionMatrixDisplay(
            confusion_matrix=matrix,
            display_labels=[
                "Normal",
                "Attack",
            ],
        ).plot(
            ax=ax,
        )

        ax.set_title(
            f"{model_name} "
            f"(threshold={threshold:.2f})"
        )

        fig.tight_layout()

        fig.savefig(
            REPORT_DIR
            / f"{model_name}_confusion_matrix.png",
            dpi=300,
        )

        plt.close(fig)

        # ====================================================
        # EXPLICIT FP / FN REPORT
        # ====================================================

        tn, fp, fn, tp = matrix.ravel()

        total_normal = tn + fp

        total_attack = fn + tp

        if total_normal > 0:

            false_positive_rate = (
                fp / total_normal
            )

        else:

            false_positive_rate = 0.0

        if total_attack > 0:

            false_negative_rate = (
                fn / total_attack
            )

        else:

            false_negative_rate = 0.0

        error_report_path = (
            REPORT_DIR
            / f"{model_name}_error_summary.txt"
        )

        with open(
            error_report_path,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                f"Model: {model_name}\n"
            )

            file.write(
                f"Threshold: {threshold:.6f}\n\n"
            )

            file.write(
                "Confusion Matrix\n"
            )

            file.write(
                "----------------\n"
            )

            file.write(
                f"TN: {tn}\n"
            )

            file.write(
                f"FP: {fp}\n"
            )

            file.write(
                f"FN: {fn}\n"
            )

            file.write(
                f"TP: {tp}\n\n"
            )

            file.write(
                "IDS Error Metrics\n"
            )

            file.write(
                "-----------------\n"
            )

            file.write(
                f"False Positive Rate: "
                f"{false_positive_rate:.6f}\n"
            )

            file.write(
                f"False Negative Rate: "
                f"{false_negative_rate:.6f}\n"
            )

        # ====================================================
        # ROC & PRECISION-RECALL CURVES
        # ====================================================

        if (
            probabilities is not None
        ):

            # ------------------------------------------------
            # ROC Curve
            # ------------------------------------------------

            try:

                fig, ax = plt.subplots(
                    figsize=(6, 6),
                )

                RocCurveDisplay.from_predictions(
                    y_test,
                    probabilities,
                    ax=ax,
                )

                ax.set_title(
                    f"{model_name} ROC Curve"
                )

                fig.tight_layout()

                fig.savefig(
                    REPORT_DIR
                    / f"{model_name}_roc_curve.png",
                    dpi=300,
                )

                plt.close(fig)

            except Exception as error:

                logger.warning(
                    "ROC curve generation failed "
                    "for %s: %s",
                    model_name,
                    error,
                )

            # ------------------------------------------------
            # Precision-Recall Curve
            # ------------------------------------------------

            try:

                fig, ax = plt.subplots(
                    figsize=(6, 6),
                )

                PrecisionRecallDisplay.from_predictions(
                    y_test,
                    probabilities,
                    ax=ax,
                )

                ax.set_title(
                    f"{model_name} "
                    "Precision-Recall Curve"
                )

                fig.tight_layout()

                fig.savefig(
                    REPORT_DIR
                    / f"{model_name}_precision_recall_curve.png",
                    dpi=300,
                )

                plt.close(fig)

            except Exception as error:

                logger.warning(
                    "Precision-recall curve generation "
                    "failed for %s: %s",
                    model_name,
                    error,
                )

        logger.info(
            "Error analysis completed for %s.",
            model_name,
        )