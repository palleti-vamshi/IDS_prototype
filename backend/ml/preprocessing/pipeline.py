"""
Machine Learning Pipeline

Creates complete preprocessing + model pipelines.
"""

import logging

from sklearn.pipeline import Pipeline

from backend.ml.preprocessing.transformer import (
    DatasetTransformer,
)

logger = logging.getLogger(__name__)


class MLPipeline:
    """Creates complete ML pipelines."""

    def __init__(self):

        self.transformer = (
            DatasetTransformer()
            .build()
        )

    def build(self, model):

        logger.info(
            "Creating ML Pipeline..."
        )

        pipeline = Pipeline(
            steps=[
                (
                    "preprocessor",
                    self.transformer,
                ),
                (
                    "classifier",
                    model,
                ),
            ]
        )

        logger.info(
            "Pipeline created successfully."
        )

        return pipeline