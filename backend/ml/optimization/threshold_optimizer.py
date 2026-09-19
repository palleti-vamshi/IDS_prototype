"""
LightX-IDS Threshold Optimizer

Optimizes classification thresholds for binary
LightX-IDS intrusion detection models.

Protocol:
- Threshold optimization uses validation data only.
- The test set is never used to select the threshold.
- F1 is the default optimization objective.
- Additional IDS metrics are recorded for every threshold.
"""

import logging

import numpy as np
import pandas as pd

from backend.ml.config import (
    DEFAULT_THRESHOLD,
    PRIMARY_THRESHOLD_METRIC,
    REPORT_DIR,
    THRESHOLD_MAX,
    THRESHOLD_MIN,
    THRESHOLD_STEP,
)

from backend.ml.evaluation.metrics import (
    calculate_binary_metrics,
)


logger = logging.getLogger(__name__)


class ThresholdOptimizer:
    """
    Optimize probability thresholds for binary classifiers.

    Threshold selection is performed exclusively on the
    validation dataset.
    """

    SUPPORTED_METRICS = {
        "accuracy",
        "precision",
        "recall",
        "f1",
        "f1_score",
    }

    # ========================================================
    # THRESHOLD OPTIMIZATION
    # ========================================================

    def optimize(
        self,
        pipeline,
        X_val,
        y_val,
        model_name: str,
        metric: str = PRIMARY_THRESHOLD_METRIC,
    ) -> dict | None:
        """
        Find the best classification threshold using
        validation data.

        The test dataset is never accessed by this method.

        Parameters
        ----------
        pipeline
            Trained sklearn pipeline.

        X_val
            Validation features.

        y_val
            Validation labels.

        model_name : str
            Model identifier.

        metric : str
            Validation metric used to select the threshold.

        Returns
        -------
        dict or None
            Threshold optimization results.
        """

        # ----------------------------------------------------
        # Validate optimization objective
        # ----------------------------------------------------

        metric = str(
            metric
        ).lower()

        if metric not in self.SUPPORTED_METRICS:

            raise ValueError(
                f"Unsupported threshold metric: {metric}. "
                f"Supported metrics: "
                f"{sorted(self.SUPPORTED_METRICS)}"
            )

        # ----------------------------------------------------
        # Locate classifier
        # ----------------------------------------------------

        if "classifier" not in pipeline.named_steps:

            raise ValueError(
                "Pipeline does not contain a "
                "'classifier' step."
            )

        classifier = pipeline.named_steps[
            "classifier"
        ]

        # ----------------------------------------------------
        # Probability support
        # ----------------------------------------------------

        if not hasattr(
            classifier,
            "predict_proba",
        ):

            logger.info(
                "%s does not support probability "
                "predictions. Threshold optimization "
                "skipped.",
                model_name,
            )

            return None

        logger.info(
            "Optimizing threshold for %s using "
            "validation data...",
            model_name,
        )

        # ====================================================
        # VALIDATION PROBABILITIES
        # ====================================================

        probabilities = (
            pipeline.predict_proba(
                X_val,
            )[:, 1]
        )

        probabilities = np.asarray(
            probabilities,
            dtype=float,
        )

        if len(probabilities) != len(y_val):

            raise ValueError(
                "Validation probability count does not "
                "match validation label count."
            )

        if not np.isfinite(
            probabilities
        ).all():

            raise ValueError(
                "Validation probabilities contain "
                "NaN or infinite values."
            )

        # ====================================================
        # THRESHOLD CANDIDATES
        # ====================================================

        thresholds = np.arange(
            THRESHOLD_MIN,
            THRESHOLD_MAX + (
                THRESHOLD_STEP / 2.0
            ),
            THRESHOLD_STEP,
        )

        thresholds = np.round(
            thresholds,
            decimals=10,
        )

        rows = []

        best_threshold = float(
            DEFAULT_THRESHOLD
        )

        best_score = -np.inf

        best_fpr = np.inf

        # ====================================================
        # EVALUATE EVERY THRESHOLD
        # ====================================================

        for threshold in thresholds:

            threshold = float(
                threshold
            )

            predictions = (
                probabilities >= threshold
            ).astype(int)

            metrics = calculate_binary_metrics(
                y_true=y_val,
                y_pred=predictions,
                y_probability=probabilities,
            )

            accuracy = metrics[
                "accuracy"
            ]

            precision = metrics[
                "precision"
            ]

            recall = metrics[
                "recall"
            ]

            f1 = metrics[
                "f1_score"
            ]

            pr_auc = metrics[
                "pr_auc"
            ]

            roc_auc = metrics[
                "roc_auc"
            ]

            fpr = metrics[
                "false_positive_rate"
            ]

            fnr = metrics[
                "false_negative_rate"
            ]

            rows.append(
                {
                    "Threshold": threshold,

                    "Accuracy": accuracy,

                    "Precision": precision,

                    "Recall": recall,

                    "F1": f1,

                    "ROC_AUC": roc_auc,

                    "PR_AUC": pr_auc,

                    "FPR": fpr,

                    "FNR": fnr,

                    "TN": metrics[
                        "true_negative"
                    ],

                    "FP": metrics[
                        "false_positive"
                    ],

                    "FN": metrics[
                        "false_negative"
                    ],

                    "TP": metrics[
                        "true_positive"
                    ],
                }
            )

            # ------------------------------------------------
            # Optimization score
            # ------------------------------------------------

            metric_values = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "f1_score": f1,
            }

            score = float(
                metric_values[metric]
            )

            # ------------------------------------------------
            # Best threshold selection
            # ------------------------------------------------
            #
            # Primary objective:
            #     maximize selected metric
            #
            # Tie-break:
            #     minimize false-positive rate
            #
            # Final tie-break:
            #     prefer threshold closest to 0.50
            #
            # This makes the result deterministic.
            # ------------------------------------------------

            is_better = (
                score > best_score
            )

            is_equal = np.isclose(
                score,
                best_score,
                rtol=1e-12,
                atol=1e-12,
            )

            if is_equal:

                lower_fpr = (
                    fpr < best_fpr
                )

                same_fpr = np.isclose(
                    fpr,
                    best_fpr,
                    rtol=1e-12,
                    atol=1e-12,
                )

                closer_to_default = (
                    abs(
                        threshold
                        - DEFAULT_THRESHOLD
                    )
                    <
                    abs(
                        best_threshold
                        - DEFAULT_THRESHOLD
                    )
                )

                is_better = (
                    lower_fpr
                    or (
                        same_fpr
                        and closer_to_default
                    )
                )

            if is_better:

                best_score = score

                best_threshold = (
                    threshold
                )

                best_fpr = float(
                    fpr
                )

        # ====================================================
        # SAFETY CHECK
        # ====================================================

        if not np.isfinite(
            best_score
        ):

            raise RuntimeError(
                "Threshold optimization did not "
                "produce a valid score."
            )

        # ====================================================
        # SAVE THRESHOLD REPORT
        # ====================================================

        REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        report = pd.DataFrame(
            rows
        )

        report_path = (
            REPORT_DIR
            / f"{model_name}_threshold_report.csv"
        )

        report.to_csv(
            report_path,
            index=False,
        )

        logger.info(
            "Best Threshold : %.4f",
            best_threshold,
        )

        logger.info(
            "Best %s : %.4f",
            metric,
            best_score,
        )

        logger.info(
            "Validation FPR at selected threshold : %.6f",
            best_fpr,
        )

        return {
            "best_threshold": float(
                best_threshold
            ),

            "best_score": float(
                best_score
            ),

            "metric": metric,

            "table": report,
        }

    # ========================================================
    # TEST EVALUATION
    # ========================================================

    def evaluate_threshold(
        self,
        pipeline,
        X_test,
        y_test,
        threshold: float,
    ) -> dict:
        """
        Evaluate a previously selected threshold on
        the test dataset.

        IMPORTANT:
        This method does not optimize the threshold.

        The threshold must already have been selected
        using validation data.
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
                f"Test evaluation threshold must "
                f"be between 0 and 1. Got {threshold}."
            )

        if "classifier" not in pipeline.named_steps:

            raise ValueError(
                "Pipeline does not contain a "
                "'classifier' step."
            )

        classifier = pipeline.named_steps[
            "classifier"
        ]

        # ====================================================
        # PROBABILITY-BASED CLASSIFIER
        # ====================================================

        if hasattr(
            classifier,
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

            predictions = (
                probabilities >= threshold
            ).astype(int)

        # ====================================================
        # FALLBACK
        # ====================================================

        else:

            predictions = pipeline.predict(
                X_test
            )

            probabilities = None

        # ====================================================
        # METRICS
        # ====================================================

        metrics = calculate_binary_metrics(
            y_true=y_test,
            y_pred=predictions,
            y_probability=probabilities,
        )

        return {
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

            "roc_auc": metrics[
                "roc_auc"
            ],

            "pr_auc": metrics[
                "pr_auc"
            ],

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

            "false_positive_rate": metrics[
                "false_positive_rate"
            ],

            "false_negative_rate": metrics[
                "false_negative_rate"
            ],

            "confusion_matrix": metrics[
                "confusion_matrix"
            ],

            "threshold": threshold,
        }