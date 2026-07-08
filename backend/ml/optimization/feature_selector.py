"""
Feature Selector

Selects the most informative features using
Recursive Feature Elimination (RFE).
"""

import logging

from sklearn.feature_selection import RFE
from sklearn.tree import DecisionTreeClassifier

logger = logging.getLogger(__name__)


class FeatureSelectorOptimizer:
    """
    Performs feature selection.
    """

    def select(
        self,
        X,
        y,
        features_to_keep=None,
    ):
        """
        Select best features.

        Returns
        -------
        selected_dataframe
        selected_features
        """

        logger.info(
            "Selecting important features..."
        )

        if features_to_keep is None:

            features_to_keep = max(
                5,
                len(X.columns) // 2,
            )

        estimator = DecisionTreeClassifier(
            random_state=42,
        )

        selector = RFE(
            estimator=estimator,
            n_features_to_select=features_to_keep,
        )

        selector.fit(
            X,
            y,
        )

        selected = X.columns[
            selector.support_
        ]

        logger.info(
            "Selected %d features.",
            len(selected),
        )

        return (
            X[selected],
            list(selected),
        )