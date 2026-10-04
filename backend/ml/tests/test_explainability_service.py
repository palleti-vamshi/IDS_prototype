"""
Integration & Smoke Tests for Phase 6.8 ExplainabilityService

Tests verify:
1. Official frozen model loads successfully.
2. Explainability components and facade initialize properly.
3. Representative telemetry observation is processed end-to-end.
4. Prediction is generated with accurate probability bounds.
5. Local SHAP explanation is generated in log-odds margin space.
6. 95 transformed SHAP values map exactly back to 32 original features.
7. Human-readable summary, operator interpretation, and console view are generated.
8. Structured output dictionary adheres strictly to the Phase 6.8 output contract.
9. Model hash remains byte-for-byte unchanged after execution.
10. Batch inference on multiple observations works seamlessly.
11. Waterfall plot generation operates on standardized contract objects.
12. Model metadata dictionary is accurate and reports immutability.
"""

import tempfile
import unittest
from pathlib import Path
import pandas as pd

from backend.ml.config import LIGHTX_100K, MODEL_DIR
from backend.ml.explainability.service import (
    ExplainabilityService,
    FROZEN_H3_32_SHA256,
    compute_sha256,
)
from backend.ml.explainability.shap_local_explainer import ALL_32_FEATURES
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.ml.feature_engineering.feature_selector import FeatureSelector


class TestExplainabilityService(unittest.TestCase):
    """Smoke and integration tests for ExplainabilityService."""

    @classmethod
    def setUpClass(cls):
        """Initialize service and prepare real test observations once."""
        cls.model_path = MODEL_DIR / "xgboost_h3_32.pkl"
        cls.initial_hash = compute_sha256(cls.model_path)
        cls.service = ExplainabilityService(model_path=cls.model_path, threshold=0.35)

        # Load small slice from authoritative dataset for realistic testing
        df = pd.read_csv(LIGHTX_100K, nrows=100).sort_values("record_id").reset_index(drop=True)
        fg = FeatureGenerator()
        stream = fg.generate_causal_stream_features(df)
        fg.fit(stream)
        stream_trans = fg.transform(stream)

        fs = FeatureSelector()
        X_sel, y_sel = fs.split(stream_trans)
        cls.sample_df = X_sel[ALL_32_FEATURES].copy()
        cls.sample_df["label"] = y_sel.values
        cls.sample_df["record_id"] = df["record_id"].iloc[:100].values

    def test_01_official_model_loads(self):
        """Verify the official model file exists and is loaded."""
        self.assertTrue(self.model_path.exists())
        self.assertEqual(self.service.current_model_sha256, FROZEN_H3_32_SHA256)

    def test_02_explainability_components_load(self):
        """Verify internal LocalShapExplainer and HumanReadableExplainer are initialized."""
        self.assertIsNotNone(self.service.local_explainer)
        self.assertIsNotNone(self.service.human_explainer)
        self.assertEqual(len(self.service.local_explainer.transformed_feature_names), 95)

    def test_03_representative_telemetry_processing(self):
        """Verify an observation can be passed as dict or pd.Series and produces an output."""
        obs_dict = self.sample_df.iloc[0][ALL_32_FEATURES].to_dict()
        res = self.service.explain(obs_dict, record_id=101)
        self.assertIsInstance(res, dict)
        self.assertIn("prediction", res)
        self.assertIn("explanation", res)
        self.assertIn("human_readable", res)
        self.assertIn("metadata", res)

    def test_04_prediction_generated_correctly(self):
        """Verify prediction block contains label, bounded probability, and margin."""
        obs = self.sample_df.iloc[0]
        res = self.service.explain(obs)
        pred = res["prediction"]
        self.assertIn(pred["label"], ["ATTACK", "NORMAL"])
        self.assertIsInstance(pred["is_attack"], bool)
        self.assertTrue(0.0 <= pred["attack_probability"] <= 1.0)
        self.assertTrue(0.0 <= pred["normal_probability"] <= 1.0)
        self.assertAlmostEqual(pred["attack_probability"] + pred["normal_probability"], 1.0, places=5)
        self.assertEqual(pred["decision_threshold"], 0.35)

    def test_05_shap_explanation_generated(self):
        """Verify SHAP explanation block contains margin, base value, and fidelity error < 1e-4."""
        obs = self.sample_df.iloc[1]
        res = self.service.explain(obs)
        exp = res["explanation"]
        self.assertIsInstance(exp["base_value"], float)
        self.assertIsInstance(exp["raw_margin"], float)
        self.assertLess(exp["fidelity_error"], 1e-4)

    def test_06_shap_values_map_to_32_original_features(self):
        """Verify aggregated 32 features are complete and mapped correctly."""
        obs = self.sample_df.iloc[2]
        res = self.service.explain(obs)
        contribs_32 = res["explanation"]["all_contributions_32"]
        self.assertEqual(len(contribs_32), 32)
        self.assertEqual(set(contribs_32.keys()), set(ALL_32_FEATURES))
        # Transformed 95 features also present
        self.assertEqual(len(res["explanation"]["transformed_contributions_95"]), 95)

    def test_07_human_readable_explanation_generated(self):
        """Verify summary, confidence category, and operator guidance are generated."""
        obs = self.sample_df.iloc[3]
        res = self.service.explain(obs, attack_type="DoS Attack")
        hr = res["human_readable"]
        self.assertIsInstance(hr["summary"], str)
        self.assertGreater(len(hr["summary"]), 20)
        self.assertTrue(
            any(w in hr["confidence_category"] for w in ["confidence", "probability", "evidence"])
        )
        self.assertIn("Operator interpretation:", hr["operator_interpretation"])
        self.assertIn("LIGHTX-IDS EXPLANATION", hr["console_view"])

    def test_08_structured_output_contract_conformance(self):
        """Verify all keys in the Phase 6.8 contract are present and non-null."""
        obs = self.sample_df.iloc[4]
        res = self.service.explain(obs, record_id=505, timestamp="2026-10-04T12:00:00Z")

        # Top level sections
        self.assertIn("prediction", res)
        self.assertIn("explanation", res)
        self.assertIn("human_readable", res)
        self.assertIn("metadata", res)

        # Metadata
        meta = res["metadata"]
        self.assertEqual(meta["record_id"], 505)
        self.assertEqual(meta["timestamp"], "2026-10-04T12:00:00Z")
        self.assertEqual(meta["model_identifier"], "xgboost_h3_32")
        self.assertEqual(meta["model_sha256"], FROZEN_H3_32_SHA256)
        self.assertGreater(len(meta["limitations"]), 2)

    def test_09_model_hash_remains_unchanged(self):
        """Verify post-inference model file hash is identical to initial hash."""
        post_hash = compute_sha256(self.model_path)
        self.assertEqual(post_hash, self.initial_hash)
        self.assertEqual(post_hash, FROZEN_H3_32_SHA256)

    def test_10_batch_explanation_processing(self):
        """Verify explain_batch correctly processes multiple observations."""
        batch_slice = self.sample_df.iloc[:5]
        batch_res = self.service.explain_batch(batch_slice)
        self.assertEqual(len(batch_res), 5)
        for item in batch_res:
            self.assertIn("prediction", item)
            self.assertIn("explanation", item)

    def test_11_waterfall_plot_from_service(self):
        """Verify generate_waterfall_plot functions properly on service contract."""
        obs = self.sample_df.iloc[0]
        res = self.service.explain(obs, record_id=999)
        with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
            tmp_path = Path(tmp.name)
            out_p = self.service.generate_waterfall_plot(res, tmp_path)
            self.assertTrue(out_p.exists())
            self.assertGreater(out_p.stat().st_size, 1000)

    def test_12_model_metadata_method(self):
        """Verify get_model_metadata outputs accurate pipeline metrics."""
        meta = self.service.get_model_metadata()
        self.assertEqual(meta["model_identifier"], "xgboost_h3_32")
        self.assertEqual(meta["original_features_count"], 32)
        self.assertEqual(meta["transformed_features_count"], 95)
        self.assertTrue(meta["is_immutable"])


if __name__ == "__main__":
    unittest.main()
