"""
TON-IoT Machine Learning Pipeline

Builds preprocessing + model pipeline.
"""

import logging

from sklearn.pipeline import Pipeline

from backend.ml.ton_iot.preprocessing import (
    TONPreprocessor,
)

logger = logging.getLogger(__name__)


class TONPipeline:
    """
    Creates complete TON-IoT ML pipeline.
    """

    def __init__(self):

        self.preprocessor = (
            TONPreprocessor()
            .build()
        )

    def build(self, model):
        """
        Build complete pipeline.
        """

        logger.info(
            "Creating TON-IoT pipeline..."
        )

        pipeline = Pipeline(
            steps=[
                (
                    "preprocessor",
                    self.preprocessor,
                ),
                (
                    "classifier",
                    model,
                ),
            ]
        )

        logger.info(
            "TON-IoT pipeline created."
        )

        return pipeline