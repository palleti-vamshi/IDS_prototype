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

    def __init__(
        self,
        numeric_features=None,
        categorical_features=None,
    ):

        self.numeric_features = (
            list(numeric_features)
            if numeric_features is not None
            else NUMERIC_COLUMNS
        )

        self.categorical_features = (
            list(categorical_features)
            if categorical_features is not None
            else CATEGORICAL_COLUMNS
        )

    def build(
        self,
        numeric_features=None,
        categorical_features=None,
    ) -> ColumnTransformer:
        """
        Build preprocessing transformer.
        """

        num_cols = (
            list(numeric_features)
            if numeric_features is not None
            else self.numeric_features
        )

        cat_cols = (
            list(categorical_features)
            if categorical_features is not None
            else self.categorical_features
        )

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

        transformers_list = []
        if num_cols:
            transformers_list.append(
                (
                    "numeric",
                    numeric_pipeline,
                    num_cols,
                )
            )
        if cat_cols:
            transformers_list.append(
                (
                    "categorical",
                    categorical_pipeline,
                    cat_cols,
                )
            )

        transformer = ColumnTransformer(
            transformers=transformers_list,
            remainder="drop",
            verbose_feature_names_out=False,
        )

        logger.info(
            "Preprocessing transformer created successfully."
        )

        return transformer