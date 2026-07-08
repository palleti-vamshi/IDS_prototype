"""
TON-IoT Preprocessing

Creates preprocessing pipeline for TON-IoT datasets.
"""

import logging

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

from backend.ml.ton_iot.config import (
    NUMERIC_COLUMNS,
    CATEGORICAL_COLUMNS,
)

logger = logging.getLogger(__name__)


class TONPreprocessor:
    """
    Builds preprocessing pipeline for TON-IoT.
    """

    def build(self):
        """
        Create preprocessing pipeline.
        """

        logger.info(
            "Building TON-IoT preprocessing..."
        )

        numeric_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy="median",
                    ),
                ),
                (
                    "scaler",
                    StandardScaler(),
                ),
            ]
        )

        categorical_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy="constant",
                        fill_value="Unknown",
                    ),
                ),
                (
                    "encoder",
                    OneHotEncoder(
                        handle_unknown="ignore",
                    ),
                ),
            ]
        )

        transformer = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    numeric_pipeline,
                    NUMERIC_COLUMNS,
                ),
                (
                    "categorical",
                    categorical_pipeline,
                    CATEGORICAL_COLUMNS,
                ),
            ]
        )

        logger.info(
            "TON-IoT preprocessing ready."
        )

        return transformer