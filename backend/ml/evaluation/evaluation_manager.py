"""
Evaluation Manager

Coordinates all evaluation tasks for trained
machine learning models.
"""

import logging

from backend.ml.evaluation.evaluator import (
    ModelEvaluator,
)
from backend.ml.evaluation.error_analysis import (
    ErrorAnalyzer,
)
from backend.ml.evaluation.feature_importance import (
    FeatureImportanceAnalyzer,
)
from backend.ml.optimization.threshold_optimizer import (
    ThresholdOptimizer,
)

logger = logging.getLogger(__name__)


class EvaluationManager:
    """
    Runs the complete evaluation pipeline.
    """

    def __init__(self):

        self.evaluator = ModelEvaluator()

        self.error_analyzer = ErrorAnalyzer()

        self.feature_importance = (
            FeatureImportanceAnalyzer()
        )

        self.threshold_optimizer = (
            ThresholdOptimizer()
        )

    def evaluate(
        self,
        pipeline,
        X_val,
        y_val,
        X_test,
        y_test,
        model_name: str,
    ):
        
        """
        Execute complete evaluation pipeline.
        """

        logger.info(
            "Starting evaluation for %s...",
            model_name,
        )

        # -----------------------------------------
        # Threshold Optimization
        # -----------------------------------------

        best_threshold = 0.50

        try:

            threshold_results = (
                self.threshold_optimizer.optimize(
                    pipeline=pipeline,
                    X_val=X_val,
                    y_val=y_val,
                    model_name=model_name,
                )
            )

            if threshold_results is not None:

                best_threshold = (
                    threshold_results["best_threshold"]
                )

        except Exception as error:

            logger.warning(
                "Threshold optimization failed for %s: %s",
                model_name,
                error,
            )

        # -----------------------------------------
        # Metrics
        # -----------------------------------------

        metrics = self.evaluator.evaluate(
            pipeline,
            X_test,
            y_test,
            threshold=best_threshold,
        )

        metrics["best_threshold"] = (
            best_threshold
        )

        # -----------------------------------------
        # Feature Importance
        # -----------------------------------------

        try:

            self.feature_importance.analyze(
                pipeline=pipeline,
                model_name=model_name,
            )

        except Exception as error:

            logger.warning(
                "Feature importance skipped for %s: %s",
                model_name,
                error,
            )

        # -----------------------------------------
        # Error Analysis
        # -----------------------------------------

        try:

            self.error_analyzer.analyze(
                pipeline=pipeline,
                X_test=X_test,
                y_test=y_test,
                model_name=model_name,
            )

        except Exception as error:

            logger.warning(
                "Error analysis failed for %s: %s",
                model_name,
                error,
            )

        logger.info(
            "Evaluation completed for %s.",
            model_name,
        )

        return metrics