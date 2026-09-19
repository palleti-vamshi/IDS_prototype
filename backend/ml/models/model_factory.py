"""
LightX-IDS Model Factory

Creates and manages all supported machine-learning models.

The factory keeps model construction centralized so that
benchmark experiments use a consistent model configuration.
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


# ============================================================
# OPTIONAL XGBOOST
# ============================================================

try:

    from xgboost import XGBClassifier

    XGBOOST_AVAILABLE = True

except ImportError:

    XGBOOST_AVAILABLE = False

    logger.warning(
        "XGBoost is not installed. "
        "The XGBoost benchmark will be skipped."
    )


class ModelFactory:
    """
    Factory responsible for creating all supported
    LightX-IDS machine-learning models.
    """

    def __init__(self):

        # ====================================================
        # LOGISTIC REGRESSION
        # ====================================================

        self.models = {

            "logistic_regression": (
                LogisticRegression(
                    random_state=RANDOM_STATE,
                    max_iter=3000,
                    solver="lbfgs",
                    class_weight="balanced",
                    C=50,
                )
            ),

            # =================================================
            # DECISION TREE
            # =================================================

            "decision_tree": (
                DecisionTreeClassifier(
                    random_state=RANDOM_STATE,
                    criterion="entropy",
                    class_weight="balanced",
                    max_depth=10,
                    min_samples_split=10,
                    min_samples_leaf=1,
                    max_features=None,
                )
            ),

            # =================================================
            # RANDOM FOREST
            # =================================================

            "random_forest": (
                RandomForestClassifier(
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
                )
            ),
        }

        # ====================================================
        # XGBOOST
        # ====================================================

        if XGBOOST_AVAILABLE:

            self.models["xgboost"] = (
                XGBClassifier(

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
            )

    # ========================================================
    # GET MODEL
    # ========================================================

    def get(
        self,
        model_name: str,
    ):
        """
        Return a fresh machine-learning model.

        A clone is returned so that training one benchmark
        model cannot mutate the factory's stored estimator.
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

        # ----------------------------------------------------
        # sklearn.clone creates an unfitted estimator with
        # exactly the same hyperparameters.
        # ----------------------------------------------------

        from sklearn.base import clone

        return clone(
            self.models[model_name]
        )

    # ========================================================
    # AVAILABLE MODELS
    # ========================================================

    def available_models(self) -> list[str]:
        """
        Return all models supported by the current
        environment and configured benchmark.
        """

        models = []

        for model_name in SUPPORTED_MODELS:

            if (
                model_name == "xgboost"
                and not XGBOOST_AVAILABLE
            ):
                continue

            if model_name not in self.models:
                continue

            models.append(
                model_name
            )

        return models