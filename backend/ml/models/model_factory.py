"""
Model Factory

Creates machine learning models for LightX-IDS.
"""

import logging

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from backend.ml.config import RANDOM_STATE

logger = logging.getLogger(__name__)

try:
    from xgboost import XGBClassifier

    XGBOOST_AVAILABLE = True

except ImportError:

    XGBOOST_AVAILABLE = False


class ModelFactory:
    """Creates ML models."""

    def get(self, model_name: str):

        model_name = model_name.lower()

        if model_name == "logistic_regression":

            return LogisticRegression(
                random_state=RANDOM_STATE,
                max_iter=1000,
            )

        if model_name == "decision_tree":

            return DecisionTreeClassifier(
                random_state=RANDOM_STATE,
            )

        if model_name == "random_forest":

            return RandomForestClassifier(
                n_estimators=200,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            )

        if model_name == "xgboost":

            if not XGBOOST_AVAILABLE:
                raise ImportError(
                    "XGBoost is not installed."
                )

            return XGBClassifier(
                random_state=RANDOM_STATE,
                eval_metric="logloss",
            )

        raise ValueError(
            f"Unsupported model: {model_name}"
        )

    def available_models(self):

        models = [
            "logistic_regression",
            "decision_tree",
            "random_forest",
        ]

        if XGBOOST_AVAILABLE:
            models.append("xgboost")

        return models