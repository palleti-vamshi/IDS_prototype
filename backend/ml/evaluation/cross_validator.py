"""
Cross Validator

Performs Stratified K-Fold Cross Validation
for machine learning pipelines.
"""

import logging

import numpy as np

from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
)

logger = logging.getLogger(__name__)


class CrossValidator:
    """
    Performs cross validation for ML pipelines.
    """

    def evaluate(
        self,
        pipeline,
        X,
        y,
        folds: int = 5,
    ) -> dict:
        """
        Run Stratified K-Fold Cross Validation.

        Returns
        -------
        dict
            Cross-validation statistics.
        """

        logger.info(
            "Running %d-Fold Cross Validation...",
            folds,
        )

        cv = StratifiedKFold(
            n_splits=folds,
            shuffle=True,
            random_state=42,
        )

        scores = cross_val_score(
            pipeline,
            X,
            y,
            cv=cv,
            scoring="accuracy",
            n_jobs=-1,
        )

        results = {

            "scores": scores,

            "mean_accuracy": np.mean(scores),

            "std_accuracy": np.std(scores),

            "min_accuracy": np.min(scores),

            "max_accuracy": np.max(scores),

        }

        logger.info(
            "Cross Validation Completed."
        )

        logger.info(
            "Mean Accuracy : %.4f",
            results["mean_accuracy"],
        )

        return results

    def print_results(
        self,
        results: dict,
    ):

        print("\n")
        print("=" * 60)
        print("CROSS VALIDATION RESULTS")
        print("=" * 60)

        for index, score in enumerate(
            results["scores"],
            start=1,
        ):

            print(
                f"Fold {index:<2}: "
                f"{score*100:.2f}%"
            )

        print("-" * 60)

        print(
            f"Mean Accuracy : "
            f"{results['mean_accuracy']*100:.2f}%"
        )

        print(
            f"Std Deviation : "
            f"{results['std_accuracy']*100:.2f}%"
        )

        print(
            f"Best Fold     : "
            f"{results['max_accuracy']*100:.2f}%"
        )

        print(
            f"Worst Fold    : "
            f"{results['min_accuracy']*100:.2f}%"
        )

        print("=" * 60)