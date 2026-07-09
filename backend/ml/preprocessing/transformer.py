"""
Dataset Transformer

Creates reusable preprocessing transformers
for the LightX-IDS ML pipeline.
"""

import logging

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)

from backend.ml.config import (
    NUMERIC_COLUMNS,
    CATEGORICAL_COLUMNS,
)

logger = logging.getLogger(__name__)


class DatasetTransformer:
    """
    Builds preprocessing transformer.
    """

    def __init__(self):

        self.numeric_features = NUMERIC_COLUMNS

        self.categorical_features = (
            CATEGORICAL_COLUMNS
        )

    def build(self) -> ColumnTransformer:
        """
        Build preprocessing transformer.
        """

        logger.info(
            "Building preprocessing transformer..."
        )

        # -------------------------------------------------
        # Numeric Pipeline
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Categorical Pipeline
        # -------------------------------------------------

        categorical_pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy="most_frequent",
                    ),
                ),
                (
                    "encoder",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,
                    ),
                ),
            ]
        )

        # -------------------------------------------------
        # Complete Transformer
        # -------------------------------------------------

        transformer = ColumnTransformer(
            transformers=[
                (
                    "numeric",
                    numeric_pipeline,
                    self.numeric_features,
                ),
                (
                    "categorical",
                    categorical_pipeline,
                    self.categorical_features,
                ),
            ],
            remainder="drop",
            verbose_feature_names_out=False,
        )

        logger.info(
            "Preprocessing transformer created successfully."
        )

        return transformer