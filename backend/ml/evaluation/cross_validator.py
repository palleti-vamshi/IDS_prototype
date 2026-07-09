"""
Cross Validator

Performs Stratified K-Fold Cross Validation
for machine learning pipelines.
"""

import logging

import numpy as np

from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate,
)

logger = logging.getLogger(__name__)


class CrossValidator:
    """
    Performs Stratified K-Fold Cross Validation.
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

        Parameters
        ----------
        pipeline : sklearn Pipeline

        X : pandas.DataFrame

        y : pandas.Series

        folds : int

        Returns
        -------
        dict
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

        scores = cross_validate(
            pipeline,
            X,
            y,
            cv=cv,
            scoring={
                "accuracy": "accuracy",
                "precision": "precision",
                "recall": "recall",
                "f1": "f1",
            },
            n_jobs=-1,
        )

        results = {

            "accuracy": scores["test_accuracy"],

            "precision": scores["test_precision"],

            "recall": scores["test_recall"],

            "f1": scores["test_f1"],

            "mean_accuracy": np.mean(
                scores["test_accuracy"]
            ),

            "mean_precision": np.mean(
                scores["test_precision"]
            ),

            "mean_recall": np.mean(
                scores["test_recall"]
            ),

            "mean_f1": np.mean(
                scores["test_f1"]
            ),

            "std_accuracy": np.std(
                scores["test_accuracy"]
            ),

            "std_precision": np.std(
                scores["test_precision"]
            ),

            "std_recall": np.std(
                scores["test_recall"]
            ),

            "std_f1": np.std(
                scores["test_f1"]
            ),

            "best_accuracy": np.max(
                scores["test_accuracy"]
            ),

            "worst_accuracy": np.min(
                scores["test_accuracy"]
            ),
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

        print()

        print("=" * 65)
        print("5-FOLD STRATIFIED CROSS VALIDATION")
        print("=" * 65)

        print(
            f"{'Fold':<10}"
            f"{'Accuracy':<12}"
            f"{'Precision':<12}"
            f"{'Recall':<12}"
            f"{'F1 Score':<12}"
        )

        print("-" * 65)

        for index in range(
            len(results["accuracy"])
        ):

            print(
                f"{index+1:<10}"
                f"{results['accuracy'][index]*100:<11.2f}%"
                f"{results['precision'][index]*100:<11.2f}%"
                f"{results['recall'][index]*100:<11.2f}%"
                f"{results['f1'][index]*100:<11.2f}%"
            )

        print("-" * 65)

        print(
            f"{'Mean':<10}"
            f"{results['mean_accuracy']*100:<11.2f}%"
            f"{results['mean_precision']*100:<11.2f}%"
            f"{results['mean_recall']*100:<11.2f}%"
            f"{results['mean_f1']*100:<11.2f}%"
        )

        print()

        print(
            f"Accuracy Std Dev : "
            f"{results['std_accuracy']*100:.2f}%"
        )

        print(
            f"Precision Std Dev : "
            f"{results['std_precision']*100:.2f}%"
        )

        print(
            f"Recall Std Dev : "
            f"{results['std_recall']*100:.2f}%"
        )

        print(
            f"F1 Std Dev : "
            f"{results['std_f1']*100:.2f}%"
        )

        print()

        print(
            f"Best Accuracy  : "
            f"{results['best_accuracy']*100:.2f}%"
        )

        print(
            f"Worst Accuracy : "
            f"{results['worst_accuracy']*100:.2f}%"
        )

        print("=" * 65)