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
                max_iter=2000,
                class_weight="balanced",
                solver="lbfgs",
            ),

            "decision_tree": DecisionTreeClassifier(
                random_state=RANDOM_STATE,
                class_weight="balanced",
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
            ),

            "random_forest": RandomForestClassifier(
                n_estimators=250,
                random_state=RANDOM_STATE,
                class_weight="balanced",
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features="sqrt",
                bootstrap=True,
                n_jobs=-1,
            ),
        }

        if XGBOOST_AVAILABLE:

            self.models["xgboost"] = XGBClassifier(

                # Reproducibility
                random_state=RANDOM_STATE,

                # Binary Classification
                objective="binary:logistic",
                eval_metric="logloss",

                # Boosting
                n_estimators=500,
                learning_rate=0.05,

                # Tree Complexity
                max_depth=8,
                min_child_weight=3,

                # Randomization
                subsample=0.8,
                colsample_bytree=0.8,

                # Regularization
                gamma=0.1,
                reg_alpha=0.1,
                reg_lambda=1.0,

                # Performance
                tree_method="hist",
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
            "Creating model: %s",
            model_name,
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