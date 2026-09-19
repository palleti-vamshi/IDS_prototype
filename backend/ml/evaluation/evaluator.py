"""
LightX-IDS Model Evaluator

Evaluates trained machine-learning pipelines using a single,
consistent classification threshold and the centralized
LightX-IDS metrics implementation.
"""

import logging
import time
from typing import Any

import numpy as np

from sklearn.metrics import (
    classification_report,
)

from backend.ml.config import (
    DEFAULT_THRESHOLD,
)

from backend.ml.evaluation.metrics import (
    calculate_binary_metrics,
)


logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Evaluates trained machine-learning pipelines.
    """

    def evaluate(
        self,
        pipeline: Any,
        X_test: Any,
        y_test: Any,
        threshold: float = DEFAULT_THRESHOLD,
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

        threshold : float
            Classification threshold applied to the positive
            class (Attack).

        Returns
        -------
        dict
            Comprehensive benchmark metrics.
        """

        threshold = float(
            threshold
        )

        if not (
            0.0
            <= threshold
            <= 1.0
        ):
            raise ValueError(
                f"Classification threshold must be "
                f"between 0 and 1. Got {threshold}."
            )

        logger.info(
            "Evaluating model (threshold=%.4f)...",
            threshold,
        )

        # ====================================================
        # PREDICTION
        # ====================================================

        start_time = time.perf_counter()

        probabilities = None

        # ====================================================
        # PROBABILITY-BASED MODELS
        # ====================================================
        #
        # This is the preferred path for LightX-IDS.
        #
        # The positive class is:
        #
        #     0 = Normal
        #     1 = Attack
        #
        # ====================================================

        if hasattr(
            pipeline,
            "predict_proba",
        ):

            probabilities = (
                pipeline.predict_proba(
                    X_test,
                )[:, 1]
            )

            probabilities = np.asarray(
                probabilities,
                dtype=float,
            )

            if not np.isfinite(
                probabilities
            ).all():

                raise ValueError(
                    "Model probability output contains "
                    "NaN or infinite values."
                )

            predictions = (
                probabilities >= threshold
            ).astype(int)

        # ====================================================
        # DECISION FUNCTION
        # ====================================================
        #
        # A decision function is NOT generally a probability.
        #
        # Therefore we do not apply the probability threshold
        # directly to the raw decision score.
        #
        # Instead, use the model's own binary prediction.
        #
        # The decision scores are still passed to the metrics
        # layer for ranking metrics such as ROC-AUC/PR-AUC.
        #
        # ====================================================

        elif hasattr(
            pipeline,
            "decision_function",
        ):

            scores = np.asarray(
                pipeline.decision_function(
                    X_test,
                ),
                dtype=float,
            )

            if not np.isfinite(
                scores
            ).all():

                raise ValueError(
                    "Model decision-function output contains "
                    "NaN or infinite values."
                )

            predictions = pipeline.predict(
                X_test
            )

            probabilities = scores

        # ====================================================
        # MODELS WITHOUT PROBABILITY OR SCORE OUTPUT
        # ====================================================

        else:

            predictions = pipeline.predict(
                X_test
            )

        prediction_time = (
            time.perf_counter()
            - start_time
        )

        # ====================================================
        # CENTRALIZED IDS METRICS
        # ====================================================

        metrics = calculate_binary_metrics(
            y_true=y_test,
            y_pred=predictions,
            y_probability=probabilities,
        )

        # ====================================================
        # CLASSIFICATION REPORT
        # ====================================================

        report = classification_report(
            y_test,
            predictions,
            output_dict=True,
            zero_division=0,
        )

        # ====================================================
        # FINAL RESULTS
        # ====================================================

        results = {

            # ------------------------------------------------
            # Core classification metrics
            # ------------------------------------------------

            "accuracy": metrics[
                "accuracy"
            ],

            "precision": metrics[
                "precision"
            ],

            "recall": metrics[
                "recall"
            ],

            "f1_score": metrics[
                "f1_score"
            ],

            # ------------------------------------------------
            # Probability / ranking metrics
            # ------------------------------------------------

            "roc_auc": metrics[
                "roc_auc"
            ],

            "pr_auc": metrics[
                "pr_auc"
            ],

            # ------------------------------------------------
            # Confusion matrix
            # ------------------------------------------------

            "true_negative": metrics[
                "true_negative"
            ],

            "false_positive": metrics[
                "false_positive"
            ],

            "false_negative": metrics[
                "false_negative"
            ],

            "true_positive": metrics[
                "true_positive"
            ],

            # ------------------------------------------------
            # IDS-specific error rates
            # ------------------------------------------------

            "false_positive_rate": metrics[
                "false_positive_rate"
            ],

            "false_negative_rate": metrics[
                "false_negative_rate"
            ],

            # ------------------------------------------------
            # Matrix + detailed report
            # ------------------------------------------------

            "confusion_matrix": metrics[
                "confusion_matrix"
            ],

            "classification_report": report,

            # ------------------------------------------------
            # Runtime
            # ------------------------------------------------

            "prediction_time": prediction_time,

            # ------------------------------------------------
            # Operating threshold
            # ------------------------------------------------

            "threshold": threshold,
        }

        logger.info(
            "Evaluation completed successfully. "
            "Accuracy=%.4f, Precision=%.4f, "
            "Recall=%.4f, F1=%.4f, "
            "ROC-AUC=%.4f, PR-AUC=%.4f, "
            "FPR=%.4f, FNR=%.4f",
            results["accuracy"],
            results["precision"],
            results["recall"],
            results["f1_score"],
            results["roc_auc"],
            results["pr_auc"],
            results["false_positive_rate"],
            results["false_negative_rate"],
        )

        return results