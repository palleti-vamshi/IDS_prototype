"""
LightX-IDS Model Evaluator

Evaluates trained machine learning models and
returns benchmark metrics.
"""

import logging
import time
from typing import Any

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluates trained machine learning pipelines.
    """

    def evaluate(
        self,
        pipeline: Any,
        X_test: Any,
        y_test: Any,
    ) -> dict:
        """
        Evaluate a trained pipeline.

        Parameters
        ----------
        pipeline
            Trained sklearn pipeline.

        X_test
            Test features.

        y_test
            Test labels.

        Returns
        -------
        dict
            Dictionary containing benchmark metrics.
        """

        logger.info("Evaluating model...")

        start_time = time.perf_counter()

        predictions = pipeline.predict(X_test)

        prediction_time = (
            time.perf_counter()
            - start_time
        )

        results = {
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

            "prediction_time": prediction_time,

            "confusion_matrix": confusion_matrix(
                y_test,
                predictions,
            ).tolist(),

            "classification_report": classification_report(
                y_test,
                predictions,
                output_dict=True,
                zero_division=0,
            ),
        }

        # -----------------------------------------
        # ROC-AUC
        # -----------------------------------------

        try:

            if hasattr(
                pipeline,
                "predict_proba",
            ):

                probabilities = (
                    pipeline.predict_proba(X_test)
                )[:, 1]

                results["roc_auc"] = (
                    roc_auc_score(
                        y_test,
                        probabilities,
                    )
                )

            elif hasattr(
                pipeline,
                "decision_function",
            ):

                scores = pipeline.decision_function(
                    X_test
                )

                results["roc_auc"] = (
                    roc_auc_score(
                        y_test,
                        scores,
                    )
                )

            else:

                results["roc_auc"] = None

        except Exception:

            results["roc_auc"] = None

        logger.info(
            "Evaluation completed successfully."
        )

        return results