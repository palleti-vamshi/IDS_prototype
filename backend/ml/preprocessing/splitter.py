"""
Dataset Splitter

Splits datasets into train, validation, and test sets.
"""

import logging

from sklearn.model_selection import train_test_split

from backend.ml.config import (
    RANDOM_STATE,
    TEST_SIZE,
    VALIDATION_SIZE,
)

logger = logging.getLogger(__name__)


class DatasetSplitter:
    """Handles train/validation/test splitting."""

    def split(self, X, y):

        logger.info("Creating train/test split...")

        # -----------------------------
        # Train + Temp
        # -----------------------------
        X_train, X_temp, y_train, y_temp = train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=y,
        )

        # -----------------------------
        # Validation + Test
        # -----------------------------
        validation_ratio = VALIDATION_SIZE / TEST_SIZE

        X_val, X_test, y_val, y_test = train_test_split(
            X_temp,
            y_temp,
            test_size=1 - validation_ratio,
            random_state=RANDOM_STATE,
            stratify=y_temp,
        )

        logger.info("Dataset split completed.")

        logger.info(
            f"Train: {len(X_train)} | "
            f"Validation: {len(X_val)} | "
            f"Test: {len(X_test)}"
        )

        return (
            X_train,
            X_val,
            X_test,
            y_train,
            y_val,
            y_test,
        )