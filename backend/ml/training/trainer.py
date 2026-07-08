"""
LightX-IDS Model Trainer

Handles training of machine learning pipelines.
"""

import logging
import time
from typing import Any

from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Generic trainer for all supported machine learning models.
    """

    def train(
        self,
        pipeline: Pipeline,
        X_train: Any,
        y_train: Any,
        model_name: str = "Unknown",
    ) -> tuple[Pipeline, float]:
        """
        Train a machine learning pipeline.

        Parameters
        ----------
        pipeline : Pipeline
            Scikit-learn pipeline.

        X_train :
            Training features.

        y_train :
            Training labels.

        model_name : str
            Model name for logging.

        Returns
        -------
        tuple
            (
                trained_pipeline,
                training_time_seconds,
            )
        """

        logger.info(
            "Training %s...",
            model_name,
        )

        start_time = time.perf_counter()

        try:

            pipeline.fit(
                X_train,
                y_train,
            )

        except Exception as error:

            logger.exception(
                "Training failed for %s",
                model_name,
            )

            raise RuntimeError(
                f"Training failed for {model_name}"
            ) from error

        training_time = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "%s trained successfully in %.4f seconds.",
            model_name,
            training_time,
        )

        return pipeline, training_time