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

            # --------------------------------------------------
            # Logistic Regression
            # --------------------------------------------------

            "logistic_regression": LogisticRegression(
                random_state=RANDOM_STATE,
                max_iter=3000,
                solver="lbfgs",
                class_weight="balanced",
                C=50,
            ),

            # --------------------------------------------------
            # Decision Tree
            # --------------------------------------------------

            "decision_tree": DecisionTreeClassifier(
                random_state=RANDOM_STATE,
                criterion="entropy",
                class_weight="balanced",
                max_depth=10,
                min_samples_split=10,
                min_samples_leaf=1,
                max_features=None,
            ),

            # --------------------------------------------------
            # Random Forest
            # --------------------------------------------------

            "random_forest": RandomForestClassifier(
                n_estimators=200,
                random_state=RANDOM_STATE,
                criterion="entropy",
                class_weight="balanced",
                max_depth=None,
                min_samples_split=8,
                min_samples_leaf=2,
                max_features="sqrt",
                bootstrap=False,
                n_jobs=-1,
            ),
        }

        # ------------------------------------------------------
        # XGBoost
        # ------------------------------------------------------

        if XGBOOST_AVAILABLE:

            self.models["xgboost"] = XGBClassifier(

                random_state=RANDOM_STATE,

                objective="binary:logistic",
                eval_metric="logloss",

                n_estimators=300,
                learning_rate=0.05,

                max_depth=8,
                min_child_weight=3,

                subsample=0.90,
                colsample_bytree=0.90,

                gamma=0,
                reg_alpha=0.10,
                reg_lambda=3,

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

            if (
                model == "xgboost"
                and not XGBOOST_AVAILABLE
            ):
                continue

            models.append(model)

        return models