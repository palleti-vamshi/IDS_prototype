"""
Hyperparameter Tuner

Performs RandomizedSearchCV for supported ML models.
"""

import logging

from scipy.stats import randint, uniform

from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
)

logger = logging.getLogger(__name__)


class HyperparameterTuner:
    """
    Tunes machine learning models using RandomizedSearchCV.
    """

    def tune(
        self,
        pipeline,
        model_name,
        X_train,
        y_train,
    ):

        logger.info(
            "Hyperparameter tuning for %s...",
            model_name,
        )

        classifier = pipeline.named_steps[
            "classifier"
        ]

        params = self.parameter_space(
            model_name,
        )

        search = RandomizedSearchCV(

            estimator=pipeline,

            param_distributions=params,

            n_iter=20,

            scoring="accuracy",

            cv=StratifiedKFold(
                n_splits=5,
                shuffle=True,
                random_state=42,
            ),

            random_state=42,

            verbose=1,

            n_jobs=-1,

        )

        search.fit(
            X_train,
            y_train,
        )

        logger.info(
            "Best Accuracy : %.4f",
            search.best_score_,
        )

        logger.info(
            "Best Parameters : %s",
            search.best_params_,
        )

        return search.best_estimator_

    def parameter_space(
        self,
        model_name,
    ):

        if model_name == "decision_tree":

            return {

                "classifier__max_depth":
                    randint(5, 30),

                "classifier__min_samples_split":
                    randint(2, 10),

                "classifier__min_samples_leaf":
                    randint(1, 5),

            }

        if model_name == "random_forest":

            return {

                "classifier__n_estimators":
                    randint(200, 700),

                "classifier__max_depth":
                    randint(8, 30),

                "classifier__min_samples_split":
                    randint(2, 10),

                "classifier__min_samples_leaf":
                    randint(1, 5),

            }

        if model_name == "xgboost":

            return {

                "classifier__n_estimators":
                    randint(300, 800),

                "classifier__max_depth":
                    randint(4, 12),

                "classifier__learning_rate":
                    uniform(0.01, 0.15),

                "classifier__subsample":
                    uniform(0.7, 0.3),

                "classifier__colsample_bytree":
                    uniform(0.7, 0.3),

                "classifier__gamma":
                    uniform(0, 0.5),

            }

        return {}