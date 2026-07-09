"""
Threshold Optimizer

Optimizes classification thresholds for
binary classification models.
"""

import logging

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from backend.ml.config import REPORT_DIR

logger = logging.getLogger(__name__)


class ThresholdOptimizer:
    """
    Optimizes probability thresholds for
    binary classifiers.
    """

    def optimize(
        self,
        pipeline,
        X_val,
        y_val,
        model_name: str,
        metric: str = "accuracy",
    ):
        """
        Find the best probability threshold
        using the validation dataset.
        """

        classifier = pipeline.named_steps["classifier"]

        if not hasattr(classifier, "predict_proba"):

            logger.info(
                "%s does not support probability predictions.",
                model_name,
            )

            return None

        logger.info(
            "Optimizing threshold for %s...",
            model_name,
        )

        probabilities = pipeline.predict_proba(
            X_val
        )[:, 1]

        thresholds = np.arange(
            0.10,
            0.91,
            0.05,
        )

        rows = []

        best_threshold = 0.50
        best_score = -1.0

        for threshold in thresholds:

            predictions = (
                probabilities >= threshold
            ).astype(int)

            accuracy = accuracy_score(
                y_val,
                predictions,
            )

            precision = precision_score(
                y_val,
                predictions,
                zero_division=0,
            )

            recall = recall_score(
                y_val,
                predictions,
                zero_division=0,
            )

            f1 = f1_score(
                y_val,
                predictions,
                zero_division=0,
            )

            rows.append(
                {
                    "Threshold": threshold,
                    "Accuracy": accuracy,
                    "Precision": precision,
                    "Recall": recall,
                    "F1": f1,
                }
            )

            metrics = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }

            if metrics[metric] > best_score:

                best_score = metrics[metric]
                best_threshold = threshold

        REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        report = pd.DataFrame(rows)

        report.to_csv(
            REPORT_DIR /
            f"{model_name}_threshold_report.csv",
            index=False,
        )

        logger.info(
            "Best Threshold : %.2f",
            best_threshold,
        )

        logger.info(
            "Best %s : %.4f",
            metric,
            best_score,
        )

        return {
            "best_threshold": best_threshold,
            "best_score": best_score,
            "metric": metric,
            "table": report,
        }

    def evaluate_threshold(
        self,
        pipeline,
        X_test,
        y_test,
        threshold: float,
    ):
        """
        Evaluate a model using
        a custom threshold.
        """

        probabilities = (
            pipeline.predict_proba(
                X_test,
            )[:, 1]
        )

        predictions = (
            probabilities >= threshold
        ).astype(int)

        return {

            "accuracy": accuracy_score(
                y_test,
                predictions,
            ),

            "precision": precision_score(
                y_test,
                predictions,
                zero_division=0,
            ),

            "recall": recall_score(
                y_test,
                predictions,
                zero_division=0,
            ),

            "f1_score": f1_score(
                y_test,
                predictions,
                zero_division=0,
            ),
        }