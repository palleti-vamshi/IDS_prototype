"""
Evaluation Manager

Coordinates the complete evaluation workflow for
LightX-IDS machine-learning models.

Evaluation protocol:

1. Optimize threshold on validation data only.
2. Freeze the selected threshold.
3. Evaluate the frozen threshold on test data.
4. Run feature-importance analysis.
5. Run error analysis using the same threshold.
"""

import logging

from backend.ml.config import (
    DEFAULT_THRESHOLD,
    PRIMARY_THRESHOLD_METRIC,
)

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
    Runs the complete LightX-IDS evaluation pipeline.
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

    # ========================================================
    # COMPLETE EVALUATION
    # ========================================================

    def evaluate(
        self,
        pipeline,
        X_val,
        y_val,
        X_test,
        y_test,
        model_name: str,
    ) -> dict:
        """
        Execute the complete evaluation pipeline.

        Validation data is used exclusively for threshold
        selection.

        The selected threshold is then frozen and used for:

        - final test metrics
        - confusion matrix
        - classification report
        - error analysis

        The test set is never used to optimize the threshold.
        """

        logger.info(
            "Starting evaluation for %s...",
            model_name,
        )

        # ====================================================
        # THRESHOLD OPTIMIZATION
        # ====================================================

        best_threshold = DEFAULT_THRESHOLD

        threshold_results = None

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

                best_threshold = float(
                    threshold_results[
                        "best_threshold"
                    ]
                )

        except Exception as error:

            logger.warning(
                "Threshold optimization failed for %s: %s",
                model_name,
                error,
            )

            logger.warning(
                "Falling back to default threshold %.2f",
                DEFAULT_THRESHOLD,
            )

        # ----------------------------------------------------
        # Validate threshold
        # ----------------------------------------------------

        if not (
            0.0
            <= best_threshold
            <= 1.0
        ):

            logger.warning(
                "Invalid threshold %.4f for %s. "
                "Using default threshold %.2f.",
                best_threshold,
                model_name,
                DEFAULT_THRESHOLD,
            )

            best_threshold = (
                DEFAULT_THRESHOLD
            )

        logger.info(
            "Selected threshold for %s: %.4f",
            model_name,
            best_threshold,
        )

        # ====================================================
        # FINAL TEST EVALUATION
        # ====================================================
        #
        # IMPORTANT:
        #
        # X_test/y_test are used only here for final
        # evaluation. No threshold optimization occurs
        # on test data.
        #
        # ====================================================

        metrics = self.evaluator.evaluate(
            pipeline=pipeline,
            X_test=X_test,
            y_test=y_test,
            threshold=best_threshold,
        )

        # ====================================================
        # THRESHOLD METADATA
        # ====================================================

        metrics["best_threshold"] = (
            best_threshold
        )

        if threshold_results is not None:

            metrics["threshold_metric"] = (
                threshold_results.get(
                    "metric",
                    PRIMARY_THRESHOLD_METRIC,
                )
            )

            metrics[
                "validation_threshold_score"
            ] = threshold_results.get(
                "best_score"
            )

        else:

            metrics[
                "threshold_metric"
            ] = PRIMARY_THRESHOLD_METRIC

            metrics[
                "validation_threshold_score"
            ] = None

        # ====================================================
        # FEATURE IMPORTANCE
        # ====================================================

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

        # ====================================================
        # ERROR ANALYSIS
        # ====================================================
        #
        # Use exactly the same threshold as the final
        # benchmark evaluation.
        #
        # ====================================================

        try:

            self.error_analyzer.analyze(
                pipeline=pipeline,
                X_test=X_test,
                y_test=y_test,
                model_name=model_name,
                threshold=best_threshold,
            )

        except Exception as error:

            logger.warning(
                "Error analysis failed for %s: %s",
                model_name,
                error,
            )

        # ====================================================
        # COMPLETE
        # ====================================================

        logger.info(
            "Evaluation completed for %s.",
            model_name,
        )

        return metrics