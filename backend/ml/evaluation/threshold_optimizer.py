"""
Threshold Optimizer

Finds the best probability threshold for binary
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
    Optimizes classification threshold.
    """

    def optimize(
        self,
        pipeline,
        X_test,
        y_test,
        start=0.10,
        end=0.90,
        step=0.01,
    ):
        """
        Search best threshold.
        """

        if not hasattr(
            pipeline,
            "predict_proba",
        ):

            logger.info(
                "Model does not support probability prediction."
            )

            return None

        probabilities = pipeline.predict_proba(
            X_test
        )[:, 1]

        best = None

        results = []

        threshold = start

        while threshold <= end:

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

            row = {

                "threshold": round(
                    threshold,
                    2,
                ),

                "accuracy": accuracy,

                "precision": precision,

                "recall": recall,

                "f1": f1,
            }

            results.append(row)

            if (
                best is None
                or row["f1"] > best["f1"]
            ):
                best = row

            threshold += step

        logger.info(
            "Best threshold: %.2f",
            best["threshold"],
        )

        return best, results

    def print_results(
        self,
        best,
    ):

        print()

        print("=" * 60)
        print("THRESHOLD OPTIMIZATION")
        print("=" * 60)

        print(
            f"Best Threshold : "
            f"{best['threshold']:.2f}"
        )

        print(
            f"Accuracy      : "
            f"{best['accuracy']*100:.2f}%"
        )

        print(
            f"Precision     : "
            f"{best['precision']*100:.2f}%"
        )

        print(
            f"Recall        : "
            f"{best['recall']*100:.2f}%"
        )

        print(
            f"F1 Score      : "
            f"{best['f1']*100:.2f}%"
        )

        print("=" * 60)