"""
Hyperparameter Optimizer

Tunes supported machine learning models using
RandomizedSearchCV.
"""

import logging

from sklearn.model_selection import RandomizedSearchCV

logger = logging.getLogger(__name__)


class HyperparameterOptimizer:
    """
    Performs hyperparameter optimization
    for supported ML models.
    """

    def optimize(
        self,
        pipeline,
        X_train,
        y_train,
        model_name: str,
    ):
        
        model_name = model_name.lower()

        logger.info(
            "Optimizing %s...",
            model_name,
        )

        classifier = pipeline.named_steps[
            "classifier"
        ]

        parameters = self._get_parameters(
            model_name,
        )

        if parameters is None:

            logger.info(
                "No optimization configured."
            )

            pipeline.fit(
                X_train,
                y_train,
            )

            return pipeline, {}

        search = RandomizedSearchCV(

            estimator=pipeline,

            param_distributions=parameters,

            n_iter=10,

            cv=5,

            scoring="f1",

            random_state=42,

            n_jobs=-1,

            verbose=0,

        )

        search.fit(
            X_train,
            y_train,
        )

        logger.info(
            "Best Parameters: %s",
            search.best_params_,
        )

        logger.info(
            "Best Score: %.4f",
            search.best_score_,
        )

        return (
            search.best_estimator_,
            search.best_params_,
        )

    def _get_parameters(
        self,
        model_name,
    ):
        

        if model_name == "logistic_regression":

            return {

                "classifier__C": [
                    0.001,
                    0.01,
                    0.05,
                    0.1,
                    0.5,
                    1,
                    2,
                    5,
                    10,
                    20,
                    50,
                    100,
                ],

                "classifier__solver": [
                    "lbfgs",
                    "liblinear",
                    "newton-cg",
                    "saga",
                ],

                "classifier__penalty": [
                    "l2",
                ],

                "classifier__class_weight": [
                    None,
                    "balanced",
                ],

                "classifier__max_iter": [
                    2000,
                    3000,
                    4000,
                ],
            }

        if model_name == "decision_tree":

            return {

                "classifier__criterion": [
                    "gini",
                    "entropy",
                ],

                "classifier__max_depth": [
                    5,
                    10,
                    15,
                    20,
                    None,
                ],

                "classifier__min_samples_split": [
                    2,
                    5,
                    10,
                ],

                "classifier__min_samples_leaf": [
                    1,
                    2,
                    4,
                ],
            }

        if model_name == "random_forest":

            return {

                "classifier__n_estimators": [
                    200,
                    300,
                    400,
                    500,
                    600,
                    800,
                ],

                "classifier__criterion": [
                    "gini",
                    "entropy",
                ],

                "classifier__max_depth": [
                    10,
                    15,
                    18,
                    20,
                    25,
                    None,
                ],

                "classifier__min_samples_split": [
                    2,
                    5,
                    8,
                    10,
                    15,
                ],

                "classifier__min_samples_leaf": [
                    1,
                    2,
                    3,
                    4,
                ],

                "classifier__max_features": [
                    "sqrt",
                    "log2",
                    None,
                ],

                "classifier__bootstrap": [
                    True,
                    False,
                ],
            }

        if model_name == "xgboost":

            return {

                "classifier__n_estimators": [
                    300,
                    400,
                    500,
                    600,
                    800,
                ],

                "classifier__learning_rate": [
                    0.01,
                    0.02,
                    0.03,
                    0.05,
                    0.08,
                    0.1,
                ],

                "classifier__max_depth": [
                    4,
                    5,
                    6,
                    7,
                    8,
                    10,
                ],

                "classifier__min_child_weight": [
                    1,
                    2,
                    3,
                    5,
                    7,
                ],

                "classifier__subsample": [
                    0.7,
                    0.8,
                    0.9,
                    1.0,
                ],

                "classifier__colsample_bytree": [
                    0.7,
                    0.8,
                    0.9,
                    1.0,
                ],

                "classifier__gamma": [
                    0,
                    0.05,
                    0.1,
                    0.2,
                    0.3,
                    0.5,
                ],

                "classifier__reg_alpha": [
                    0,
                    0.01,
                    0.05,
                    0.1,
                    0.5,
                ],

                "classifier__reg_lambda": [
                    1,
                    1.5,
                    2,
                    3,
                    5,
                ],
            }

        return None