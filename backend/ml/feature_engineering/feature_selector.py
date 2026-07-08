"""
Feature Selector

Splits features and target for machine learning.
"""

import logging

import pandas as pd

from backend.ml.config import (
    TARGET_COLUMN,
    DROP_COLUMNS,
)

logger = logging.getLogger(__name__)


class FeatureSelector:
    """Selects training features."""

    def split(
        self,
        df: pd.DataFrame,
    ):
        """
        Split dataset into features and labels.
        """

        logger.info("Selecting features...")

        X = df.drop(
            columns=DROP_COLUMNS + [TARGET_COLUMN]
        )

        y = df[TARGET_COLUMN]

        logger.info(
            f"Features selected: {len(X.columns)}"
        )

        return X, y