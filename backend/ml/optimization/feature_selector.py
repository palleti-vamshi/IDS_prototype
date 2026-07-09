"""
Feature Selector

Selects the most informative features using
SelectFromModel and Random Forest importance.
"""

import logging

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel

logger = logging.getLogger(__name__)


class FeatureSelectorOptimizer:
    """
    Performs automatic feature selection.
    """

    def select(
        self,
        X: pd.DataFrame,
        y,
        threshold: str = "median",
    ):
        """
        Select important features.

        Parameters
        ----------
        X : DataFrame

        y : Labels

        threshold : str
            median / mean

        Returns
        -------
        selected_dataframe,
        selected_features
        """

        logger.info(
            "Running feature selection..."
        )

        estimator = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
        )

        estimator.fit(
            X,
            y,
        )

        selector = SelectFromModel(
            estimator,
            threshold=threshold,
            prefit=True,
        )

        selected_columns = X.columns[
            selector.get_support()
        ]

        logger.info(
            "Selected %d of %d features.",
            len(selected_columns),
            len(X.columns),
        )

        logger.info(
            "Selected Features:"
        )

        for feature in selected_columns:

            logger.info(
                "  %s",
                feature,
            )

        X_selected = X[
            selected_columns
        ].copy()

        return (
            X_selected,
            list(selected_columns),
        )