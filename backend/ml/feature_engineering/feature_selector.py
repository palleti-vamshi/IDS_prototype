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

        drop_cols = [col for col in DROP_COLUMNS if col in df.columns]
        if TARGET_COLUMN in df.columns:
            drop_cols.append(TARGET_COLUMN)
            y = df[TARGET_COLUMN]
        else:
            y = None

        X = df.drop(
            columns=drop_cols
        )

        logger.info(
            f"Features selected: {len(X.columns)}"
        )

        return X, y