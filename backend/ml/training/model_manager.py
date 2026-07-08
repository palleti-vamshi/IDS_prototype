"""
LightX-IDS Model Manager

Handles saving, loading, versioning,
and metadata management of trained models.
"""

import json
import logging
from pathlib import Path
from typing import Any

import joblib

from backend.ml.config import MODEL_DIR

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Handles all trained model operations.
    """

    def __init__(self):

        MODEL_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        pipeline: Any,
        model_name: str,
        metadata: dict,
    ) -> Path:
        """
        Save a trained model and its metadata.
        """

        model_path = MODEL_DIR / f"{model_name}.pkl"
        metadata_path = MODEL_DIR / f"{model_name}.json"

        try:

            joblib.dump(
                pipeline,
                model_path,
            )

            with open(
                metadata_path,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    metadata,
                    file,
                    indent=4,
                )

            logger.info(
                "Saved model: %s",
                model_path.name,
            )

            return model_path

        except Exception as error:

            logger.exception(
                "Failed to save %s",
                model_name,
            )

            raise RuntimeError(
                f"Unable to save model: {model_name}"
            ) from error

    def load(
        self,
        model_name: str,
    ) -> Any:
        """
        Load a trained model.
        """

        model_path = MODEL_DIR / f"{model_name}.pkl"

        if not model_path.exists():

            raise FileNotFoundError(
                model_path
            )

        logger.info(
            "Loading model: %s",
            model_name,
        )

        return joblib.load(model_path)

    def load_metadata(
        self,
        model_name: str,
    ) -> dict:
        """
        Load metadata JSON.
        """

        metadata_path = MODEL_DIR / f"{model_name}.json"

        if not metadata_path.exists():

            raise FileNotFoundError(
                metadata_path
            )

        with open(
            metadata_path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    def exists(
        self,
        model_name: str,
    ) -> bool:
        """
        Check whether a model exists.
        """

        return (
            MODEL_DIR / f"{model_name}.pkl"
        ).exists()

    def size_mb(
        self,
        model_name: str,
    ) -> float:
        """
        Return model size in MB.
        """

        model_path = MODEL_DIR / f"{model_name}.pkl"

        if not model_path.exists():
            return 0.0

        size = (
            model_path.stat().st_size
            / (1024 * 1024)
        )

        return round(size, 3)

    def list_models(
        self,
    ) -> list[str]:
        """
        Return all saved models.
        """

        return sorted(
            [
                model.stem
                for model in MODEL_DIR.glob("*.pkl")
            ]
        )

    def delete(
        self,
        model_name: str,
    ) -> None:
        """
        Delete model and metadata.
        """

        model_path = MODEL_DIR / f"{model_name}.pkl"
        metadata_path = MODEL_DIR / f"{model_name}.json"

        if model_path.exists():
            model_path.unlink()

        if metadata_path.exists():
            metadata_path.unlink()

        logger.info(
            "Deleted model: %s",
            model_name,
        )