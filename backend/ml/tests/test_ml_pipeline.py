"""
Unit and integration tests for the LightX-IDS Machine Learning Pipeline.
Tests schema, leakage prevention, splitting, threshold optimization, and models.
"""

import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline

from backend.ml.config import (
    LIGHTX_1K,
    LIGHTX_100K,
    LIGHTX_REQUIRED_COLUMNS,
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    DROP_COLUMNS,
    PRIMARY_THRESHOLD_METRIC,
)
from backend.ml.preprocessing.loader import DatasetLoader
from backend.ml.preprocessing.splitter import DatasetSplitter
from backend.ml.preprocessing.transformer import DatasetTransformer
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.ml.feature_engineering.feature_selector import FeatureSelector
from backend.ml.models.model_factory import ModelFactory
from backend.ml.optimization.threshold_optimizer import ThresholdOptimizer
from backend.ml.evaluation.evaluator import ModelEvaluator


class TestMLPipeline(unittest.TestCase):
    """Test suite for Phase 4 ML pipeline components."""

    @classmethod
    def setUpClass(cls):
        cls.loader = DatasetLoader()
        cls.df_1k = cls.loader.load(LIGHTX_1K, required_columns=LIGHTX_REQUIRED_COLUMNS)

    def test_sensor_code_configuration(self):
        """Verify sensor_code is in required schema and categorical features."""
        self.assertIn("sensor_code", LIGHTX_REQUIRED_COLUMNS)
        self.assertIn("sensor_code", CATEGORICAL_COLUMNS)
        self.assertIn("sensor_code", self.df_1k.columns)

    def test_dataset_path_100k(self):
        """Verify LIGHTX_100K points to existing lightx_ids_dataset_100k.csv."""
        self.assertTrue(LIGHTX_100K.exists(), f"Path {LIGHTX_100K} does not exist!")
        self.assertEqual(LIGHTX_100K.name, "lightx_ids_dataset_100k.csv")

    def test_feature_selector_no_label_leakage(self):
        """Verify FeatureSelector completely removes label and attack_type from features."""
        selector = FeatureSelector()
        X, y = selector.split(self.df_1k)
        self.assertNotIn("label", X.columns)
        self.assertNotIn("attack_type", X.columns)
        self.assertNotIn("record_id", X.columns)
        self.assertNotIn("timestamp", X.columns)
        self.assertNotIn("sequence_number", X.columns)
        self.assertEqual(len(y), len(self.df_1k))

    def test_dataset_splitter_proportions(self):
        """Verify 80/10/10 split proportions for stratified split."""
        splitter = DatasetSplitter()
        X = self.df_1k.drop(columns=["label"])
        y = self.df_1k["label"]
        X_train, X_val, X_test, y_train, y_val, y_test = splitter.split(X, y)

        self.assertEqual(len(X_train), 800)
        self.assertEqual(len(X_val), 100)
        self.assertEqual(len(X_test), 100)
        # Check stratification
        self.assertAlmostEqual(y_train.mean(), y_test.mean(), delta=0.05)

    def test_dataset_temporal_splitter(self):
        """Verify chronological ordering is preserved in temporal_split."""
        splitter = DatasetSplitter()
        X = self.df_1k.drop(columns=["label"])
        y = self.df_1k["label"]
        X_train, X_val, X_test, y_train, y_val, y_test = splitter.temporal_split(X, y)

        self.assertEqual(len(X_train), 800)
        self.assertEqual(len(X_val), 100)
        self.assertEqual(len(X_test), 100)
        # Strictly chronological
        self.assertTrue((X_train.index < X_val.index[0]).all())
        self.assertTrue((X_val.index < X_test.index[0]).all())

    def test_feature_generator_fit_leakage_safety(self):
        """Verify FeatureGenerator fits statistics only on training data."""
        gen = FeatureGenerator()
        X_train = self.df_1k.iloc[:500]
        gen.fit(X_train)
        self.assertTrue(gen.is_fitted)

        # Check devices present in training set are in device_statistics
        train_devices = set(X_train["device_id"].unique())
        self.assertEqual(set(gen.device_statistics.keys()), train_devices)

        # Transform unseen rows
        X_unseen = self.df_1k.iloc[500:600]
        transformed = gen.transform(X_unseen)
        self.assertIn("device_mean_deviation", transformed.columns)
        self.assertIn("z_score", transformed.columns)
        self.assertFalse(transformed["z_score"].isna().any())

    def test_threshold_optimizer_validation_only(self):
        """Verify ThresholdOptimizer selects threshold using validation data only."""
        optimizer = ThresholdOptimizer()

        # Create dummy pipeline
        generator = FeatureGenerator()
        df_feat = generator.fit_transform(self.df_1k)
        selector = FeatureSelector()
        X, y = selector.split(df_feat)

        splitter = DatasetSplitter()
        X_train, X_val, X_test, y_train, y_val, y_test = splitter.split(X, y)

        transformer = DatasetTransformer(
            numeric_features=[c for c in NUMERIC_COLUMNS if c in X_train.columns],
            categorical_features=[c for c in CATEGORICAL_COLUMNS if c in X_train.columns],
        ).build()

        pipeline = Pipeline([
            ("preprocessor", transformer),
            ("classifier", DecisionTreeClassifier(random_state=42)),
        ])

        pipeline.fit(X_train, y_train)

        res = optimizer.optimize(
            pipeline=pipeline,
            X_val=X_val,
            y_val=y_val,
            model_name="decision_tree",
            metric=PRIMARY_THRESHOLD_METRIC,
        )

        self.assertIsNotNone(res)
        self.assertIn("best_threshold", res)
        self.assertTrue(0.0 <= res["best_threshold"] <= 1.0)

    def test_model_factory_models_available(self):
        """Verify all 4 models are instantiate-able."""
        factory = ModelFactory()
        available = factory.available_models()
        self.assertIn("logistic_regression", available)
        self.assertIn("decision_tree", available)
        self.assertIn("random_forest", available)
        self.assertIn("xgboost", available)

        for model_name in available:
            model = factory.get(model_name)
            self.assertIsNotNone(model)


if __name__ == "__main__":
    unittest.main()
