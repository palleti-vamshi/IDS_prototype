"""
Threshold Optimizer

Finds the optimal probability threshold for binary
classification models.
"""

import logging

import numpy as np

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

logger = logging.getLogger(__name__)


class ThresholdOptimizer:
    """
    Finds the best probability threshold.
    """

    def optimize(
        self,
        pipeline,
        X_test,
        y_test,
    ):

        logger.info(
            "Optimizing decision threshold..."
        )

        probabilities = pipeline.predict_proba(
            X_test
        )[:, 1]

        best = {
            "threshold": 0.50,
            "accuracy": 0,
            "precision": 0,
            "recall": 0,
            "f1_score": 0,
        }

        for threshold in np.arange(
            0.10,
            0.91,
            0.01,
        ):

            predictions = (
                probabilities >= threshold
            ).astype(int)

            accuracy = accuracy_score(
                y_test,
                predictions,
            )

            precision = precision_score(
                y_test,
                predictions,
                zero_division=0,
            )

            recall = recall_score(
                y_test,
                predictions,
                zero_division=0,
            )

            f1 = f1_score(
                y_test,
                predictions,
                zero_division=0,
            )

            if f1 > best["f1_score"]:

                best = {

                    "threshold": threshold,

                    "accuracy": accuracy,

                    "precision": precision,

                    "recall": recall,

                    "f1_score": f1,
                }

        logger.info(
            "Best Threshold : %.2f",
            best["threshold"],
        )

        logger.info(
            "Best F1 Score : %.4f",
            best["f1_score"],
        )

        return best