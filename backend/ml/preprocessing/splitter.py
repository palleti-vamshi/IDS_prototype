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

    def split(self, X, y, random_state: int | None = None):

        logger.info("Creating train/test split...")

        rs = random_state if random_state is not None else RANDOM_STATE

        # -----------------------------
        # Train + Temp
        # -----------------------------
        X_train, X_temp, y_train, y_temp = train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=rs,
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
            random_state=rs,
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

    def temporal_split(
        self,
        X,
        y,
        train_ratio: float = 0.80,
        val_ratio: float = 0.10,
    ):
        """
        Chronological / temporal split:
        Train: first 80% (earlier telemetry)
        Validation: next 10% (intermediate telemetry)
        Test: last 10% (latest telemetry)

        Preserves strict chronological ordering without scrambling time series.
        """
        logger.info("Creating chronological temporal split...")

        n = len(X)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        X_train = X.iloc[:train_end].copy()
        y_train = y.iloc[:train_end].copy()

        X_val = X.iloc[train_end:val_end].copy()
        y_val = y.iloc[train_end:val_end].copy()

        X_test = X.iloc[val_end:].copy()
        y_test = y.iloc[val_end:].copy()

        logger.info("Temporal dataset split completed.")
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