"""
LightX-IDS Evaluation Metrics

Centralized binary-classification metrics for the IDS benchmark.

All classification metrics are calculated from the final
predictions and, where applicable, prediction probabilities
or decision scores.

Metric conventions:
- label 0 = Normal
- label 1 = Attack
- positive class = Attack
- pr_auc = Average Precision (AP), used as the
  precision-recall summary metric
"""

from __future__ import annotations

from typing import Any

import numpy as np

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def calculate_binary_metrics(
    y_true,
    y_pred,
    y_probability=None,
) -> dict[str, Any]:
    """
    Calculate comprehensive binary IDS metrics.

    Parameters
    ----------
    y_true:
        Ground-truth binary labels.

    y_pred:
        Binary predictions generated using the selected
        operating threshold.

    y_probability:
        Positive-class probability or decision score.

        For LightX-IDS:
            0 = Normal
            1 = Attack

        Required for ROC-AUC and Average Precision.

    Returns
    -------
    dict
        Complete binary IDS evaluation metrics.
    """

    # ========================================================
    # INPUT NORMALIZATION
    # ========================================================

    y_true = np.asarray(
        y_true
    ).reshape(-1)

    y_pred = np.asarray(
        y_pred
    ).reshape(-1)

    # --------------------------------------------------------
    # Length validation
    # --------------------------------------------------------

    if len(y_true) != len(y_pred):

        raise ValueError(
            "y_true and y_pred must contain the same "
            "number of observations."
        )

    if len(y_true) == 0:

        raise ValueError(
            "Cannot calculate metrics on an empty dataset."
        )

    # --------------------------------------------------------
    # Label validation
    # --------------------------------------------------------

    valid_true_labels = set(
        np.unique(y_true).tolist()
    )

    valid_pred_labels = set(
        np.unique(y_pred).tolist()
    )

    if not valid_true_labels.issubset(
        {0, 1}
    ):

        raise ValueError(
            "y_true must contain only binary labels "
            "0 and 1. "
            f"Found: {sorted(valid_true_labels)}"
        )

    if not valid_pred_labels.issubset(
        {0, 1}
    ):

        raise ValueError(
            "y_pred must contain only binary labels "
            "0 and 1. "
            f"Found: {sorted(valid_pred_labels)}"
        )

    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    )

    tn, fp, fn, tp = (
        matrix.ravel()
    )

    # ========================================================
    # BASIC CLASSIFICATION METRICS
    # ========================================================

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    # ========================================================
    # FALSE POSITIVE RATE
    # ========================================================
    #
    # FPR = FP / (FP + TN)
    #
    # Measures the proportion of Normal observations
    # incorrectly classified as Attack.
    #
    # ========================================================

    normal_count = (
        tn + fp
    )

    if normal_count > 0:

        false_positive_rate = (
            fp / normal_count
        )

    else:

        false_positive_rate = 0.0

    # ========================================================
    # FALSE NEGATIVE RATE
    # ========================================================
    #
    # FNR = FN / (FN + TP)
    #
    # Measures the proportion of attacks missed by
    # the intrusion detection system.
    #
    # ========================================================

    attack_count = (
        fn + tp
    )

    if attack_count > 0:

        false_negative_rate = (
            fn / attack_count
        )

    else:

        false_negative_rate = 0.0

    # ========================================================
    # ROC-AUC / AVERAGE PRECISION
    # ========================================================

    roc_auc = None

    pr_auc = None

    if y_probability is not None:

        y_probability = np.asarray(
            y_probability,
            dtype=float,
        ).reshape(-1)

        if len(y_probability) != len(
            y_true
        ):

            raise ValueError(
                "y_probability must contain the same "
                "number of observations as y_true."
            )

        if not np.isfinite(
            y_probability
        ).all():

            raise ValueError(
                "y_probability contains NaN or "
                "infinite values."
            )

        # ----------------------------------------------------
        # Both classes are required for ROC-AUC.
        # ----------------------------------------------------

        if len(
            np.unique(y_true)
        ) == 2:

            roc_auc = roc_auc_score(
                y_true,
                y_probability,
            )

            # ------------------------------------------------
            # Average Precision
            #
            # This is used as the project's PR-AUC-style
            # summary metric.
            # ------------------------------------------------

            pr_auc = (
                average_precision_score(
                    y_true,
                    y_probability,
                )
            )

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "accuracy": float(
            accuracy
        ),

        "precision": float(
            precision
        ),

        "recall": float(
            recall
        ),

        "f1_score": float(
            f1
        ),

        "roc_auc": (
            float(roc_auc)
            if roc_auc is not None
            else None
        ),

        "pr_auc": (
            float(pr_auc)
            if pr_auc is not None
            else None
        ),

        "true_negative": int(
            tn
        ),

        "false_positive": int(
            fp
        ),

        "false_negative": int(
            fn
        ),

        "true_positive": int(
            tp
        ),

        "false_positive_rate": float(
            false_positive_rate
        ),

        "false_negative_rate": float(
            false_negative_rate
        ),

        "confusion_matrix": [
            [
                int(tn),
                int(fp),
            ],
            [
                int(fn),
                int(tp),
            ],
        ],
    }