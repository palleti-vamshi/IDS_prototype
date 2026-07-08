"""
LightX-IDS Model Factory

Creates and manages all supported machine learning models.
"""

import logging

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from backend.ml.config import (
    RANDOM_STATE,
    SUPPORTED_MODELS,
)

logger = logging.getLogger(__name__)

try:
    from xgboost import XGBClassifier

    XGBOOST_AVAILABLE = True

except ImportError:

    XGBOOST_AVAILABLE = False


class ModelFactory:
    """
    Factory class responsible for creating
    machine learning models.
    """

    def __init__(self):

        self.models = {

            "logistic_regression": LogisticRegression(
                random_state=RANDOM_STATE,
                max_iter=1000,
                class_weight="balanced",
                solver="lbfgs",
            ),

            "decision_tree": DecisionTreeClassifier(
                random_state=RANDOM_STATE,
                class_weight="balanced",
                max_depth=12,
                min_samples_split=4,
                min_samples_leaf=2,
            ),

            "random_forest": RandomForestClassifier(
                n_estimators=200,
                random_state=RANDOM_STATE,
                class_weight="balanced",
                n_jobs=-1,
                max_depth=15,
                min_samples_split=4,
            ),
        }

        if XGBOOST_AVAILABLE:

            self.models["xgboost"] = XGBClassifier(
                random_state=RANDOM_STATE,
                eval_metric="logloss",
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                n_jobs=-1,
            )

    def get(self, model_name: str):
        """
        Return a machine learning model.
        """

        model_name = model_name.lower()

        if model_name not in self.models:

            raise ValueError(
                f"Unsupported model: {model_name}"
            )

        logger.info(
            f"Creating model: {model_name}"
        )

        return self.models[model_name]

    def available_models(self):
        """
        Return all available models.
        """

        models = []

        for model in SUPPORTED_MODELS:

            if model == "xgboost" and not XGBOOST_AVAILABLE:
                continue

            models.append(model)

        return models