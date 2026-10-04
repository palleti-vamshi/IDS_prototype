"""
Unit Tests for LocalShapExplainer

Tests:
1. Model loads successfully
2. Single observation works (dict, Series, DataFrame)
3. Prediction is valid ('NORMAL' or 'ATTACK')
4. Probability is between 0 and 1 (and sums to 1.0)
5. SHAP values have correct dimensionality (95 transformed, 32 aggregated)
6. Top-k output works as configured
7. Positive/negative directions are mathematically correct
8. Original feature mapping works
9. One-hot categorical aggregation works
10. Additive fidelity passes (< 1e-4 error)
11. Waterfall plot generation works
"""

import os
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from backend.ml.config import (
    LIGHTX_100K,
    MODEL_DIR,
)
from backend.ml.explainability.shap_local_explainer import (
    LocalShapExplainer,
    ALL_32_FEATURES,
    ACTIVE_NUMERIC_COLUMNS,
    ACTIVE_CATEGORICAL_COLUMNS,
)
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.ml.feature_engineering.feature_selector import FeatureSelector


class TestLocalShapExplainer(unittest.TestCase):
    """Test suite for LocalShapExplainer."""

    @classmethod
    def setUpClass(cls):
        """Load model and prepare representative test records once."""
        cls.model_path = MODEL_DIR / "xgboost_h3_32.pkl"
        cls.explainer = LocalShapExplainer(model_path=cls.model_path, threshold=0.35)

        # Prepare small slice from authoritative dataset for testing
        df = pd.read_csv(LIGHTX_100K, nrows=200).sort_values("record_id").reset_index(drop=True)
        fg = FeatureGenerator()
        stream = fg.generate_causal_stream_features(df)
        fg.fit(stream)
        stream_trans = fg.transform(stream)

        fs = FeatureSelector()
        X_sel, y_sel = fs.split(stream_trans)
        cls.X_32 = X_sel[ALL_32_FEATURES].copy()
        cls.y = y_sel.to_numpy()

        # Find at least one sample
        cls.sample_normal = cls.X_32.iloc[0]
        cls.sample_idx = 0

    def test_01_model_loads_successfully(self):
        """Verify model loads and components are properly initialized."""
        self.assertIsNotNone(self.explainer.pipeline)
        self.assertIsNotNone(self.explainer.preprocessor)
        self.assertIsNotNone(self.explainer.classifier)
        self.assertEqual(len(self.explainer.transformed_feature_names), 95)
        self.assertIsInstance(self.explainer.base_value, float)

    def test_02_single_observation_input_formats(self):
        """Verify single observation works from Series, dict, and DataFrame."""
        # From Series
        res_series = self.explainer.explain_instance(self.sample_normal, top_k=5)
        self.assertIn("prediction", res_series)

        # From dict
        res_dict = self.explainer.explain_instance(self.sample_normal.to_dict(), top_k=5)
        self.assertEqual(res_series["prediction"], res_dict["prediction"])
        self.assertAlmostEqual(res_series["attack_probability"], res_dict["attack_probability"], places=5)

        # From 1-row DataFrame
        df_row = pd.DataFrame([self.sample_normal.to_dict()])
        res_df = self.explainer.explain_instance(df_row, top_k=5)
        self.assertEqual(res_series["prediction"], res_df["prediction"])

    def test_03_prediction_validity(self):
        """Verify prediction is either NORMAL or ATTACK."""
        res = self.explainer.explain_instance(self.sample_normal)
        self.assertIn(res["prediction"], ["NORMAL", "ATTACK"])

    def test_04_probability_bounds_and_sum(self):
        """Verify probability is bounded in [0, 1] and sums to 1.0."""
        res = self.explainer.explain_instance(self.sample_normal)
        p_att = res["attack_probability"]
        p_norm = res["normal_probability"]
        self.assertGreaterEqual(p_att, 0.0)
        self.assertLessEqual(p_att, 1.0)
        self.assertGreaterEqual(p_norm, 0.0)
        self.assertLessEqual(p_norm, 1.0)
        self.assertAlmostEqual(p_att + p_norm, 1.0, places=6)

    def test_05_shap_values_dimensionality(self):
        """Verify SHAP output dimensions match 95 transformed and 32 aggregated features."""
        res = self.explainer.explain_instance(self.sample_normal)
        self.assertEqual(len(res["shap_values_95"]), 95)
        self.assertEqual(len(res["all_contributions_32"]), 32)

    def test_06_top_k_output(self):
        """Verify top_k parameter restricts positive and negative contributor lists."""
        for k in [1, 3, 5, 10]:
            res = self.explainer.explain_instance(self.sample_normal, top_k=k)
            self.assertLessEqual(len(res["top_positive_contributors"]), k)
            self.assertLessEqual(len(res["top_negative_contributors"]), k)

    def test_07_positive_negative_directions(self):
        """Verify positive contributors have positive SHAP and negative have negative SHAP."""
        res = self.explainer.explain_instance(self.sample_normal, top_k=10)
        for item in res["top_positive_contributors"]:
            self.assertGreater(item["shap_value"], 0.0)
        for item in res["top_negative_contributors"]:
            self.assertLess(item["shap_value"], 0.0)

    def test_08_original_feature_mapping(self):
        """Verify all 32 original features are present in the aggregated results."""
        res = self.explainer.explain_instance(self.sample_normal)
        keys_32 = set(res["all_contributions_32"].keys())
        self.assertEqual(keys_32, set(ALL_32_FEATURES))

    def test_09_one_hot_categorical_aggregation(self):
        """Verify categorical one-hot attributions sum to the parent categorical feature."""
        res = self.explainer.explain_instance(self.sample_normal)
        shap_95 = res["shap_values_95"]

        for cat in ACTIVE_CATEGORICAL_COLUMNS:
            member_indices = self.explainer.original_to_indices[cat]
            member_names = [self.explainer.transformed_feature_names[i] for i in member_indices]
            expected_sum = sum(shap_95[m] for m in member_names)
            actual_agg = res["all_contributions_32"][cat]
            self.assertAlmostEqual(expected_sum, actual_agg, places=6)

    def test_10_additive_fidelity(self):
        """Verify base_value + sum(shap_values_95) approximately equals raw margin."""
        res = self.explainer.explain_instance(self.sample_normal, check_fidelity=True)
        self.assertLess(res["fidelity_error"], 1e-4)

    def test_11_waterfall_plot_generation(self):
        """Verify waterfall plot generation creates a valid non-empty image file."""
        res = self.explainer.explain_instance(self.sample_normal)
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_agg = Path(tmp_dir) / "waterfall_agg.png"
            out_std = Path(tmp_dir) / "waterfall_std.png"

            # Aggregated plot
            self.explainer.generate_waterfall_plot(res, out_agg, aggregated=True)
            self.assertTrue(out_agg.exists())
            self.assertGreater(out_agg.stat().st_size, 1000)

            # Standard 95 plot
            self.explainer.generate_waterfall_plot(res, out_std, aggregated=False)
            self.assertTrue(out_std.exists())
            self.assertGreater(out_std.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
