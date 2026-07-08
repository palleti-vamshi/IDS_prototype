"""
TON-IoT Preprocessing Transformer

Creates preprocessing pipeline for TON-IoT datasets.
"""

import logging

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

from backend.ml.config import (
    TON_NUMERIC_COLUMNS,
    TON_CATEGORICAL_COLUMNS,
)

logger = logging.getLogger(__name__)


class TonTransformer:
    """
    Builds preprocessing pipeline for TON-IoT.
    """

    def build(self):

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
                    "num",
                    numeric_pipeline,
                    TON_NUMERIC_COLUMNS,
                ),
                (
                    "cat",
                    categorical_pipeline,
                    TON_CATEGORICAL_COLUMNS,
                ),
            ]
        )

        logger.info(
            "TON-IoT transformer ready."
        )

        return transformer