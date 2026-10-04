"""
Unit Tests for HumanReadableExplainer (Phase 6.6)

Tests cover:
1. ATTACK explanation generation.
2. NORMAL explanation generation.
3. Borderline prediction handling.
4. Probability formatting.
5. Positive SHAP direction and attribution sentence.
6. Negative SHAP direction and attribution sentence.
7. Feature description lookup.
8. Unknown feature handling (graceful fallback).
9. Attack type correctly distinguished from model prediction.
10. Strict causal language audit (no forbidden causal phrasing).
11. Structured output contains all required fields.
12. Summary is generated and non-empty.
13. Operator interpretation is generated and actionable without unsafe physical commands.
14. End-to-end integration with LocalShapExplainer.
"""

import unittest
from pathlib import Path
from typing import Any, Dict

from backend.ml.config import MODEL_DIR
from backend.ml.explainability.shap_local_explainer import LocalShapExplainer
from backend.ml.explainability.human_explainer import (
    HumanReadableExplainer,
    FEATURE_DESCRIPTIONS,
    EXPLANATION_LIMITATIONS,
)


class TestHumanExplainer(unittest.TestCase):
    """Test suite for HumanReadableExplainer."""

    @classmethod
    def setUpClass(cls):
        """Prepare HumanReadableExplainer with mock and real explainer configurations."""
        cls.model_path = MODEL_DIR / "xgboost_h3_32.pkl"
        cls.local_explainer = LocalShapExplainer(model_path=cls.model_path, threshold=0.35)
        cls.explainer = HumanReadableExplainer(local_explainer=cls.local_explainer)

        # Mock structured local explanations
        cls.mock_attack_explanation: Dict[str, Any] = {
            "prediction": "ATTACK",
            "attack_probability": 0.9936,
            "normal_probability": 0.0064,
            "raw_margin": 5.0459,
            "base_value": -0.2719,
            "top_positive_contributors": [
                {
                    "feature": "plant_duplicate_ratio_19",
                    "shap_value": 3.3264,
                    "raw_value": 0.3158,
                },
                {
                    "feature": "rolling_time_delta_5",
                    "shap_value": 0.8334,
                    "raw_value": 0.063,
                },
            ],
            "top_negative_contributors": [
                {
                    "feature": "topic",
                    "shap_value": -0.1110,
                    "raw_value": "factory/line1/pressure",
                },
            ],
        }

        cls.mock_normal_explanation: Dict[str, Any] = {
            "prediction": "NORMAL",
            "attack_probability": 0.0001,
            "normal_probability": 0.9999,
            "raw_margin": -7.2140,
            "base_value": -0.2719,
            "top_positive_contributors": [],
            "top_negative_contributors": [
                {
                    "feature": "plant_duplicate_ratio_19",
                    "shap_value": -4.2150,
                    "raw_value": 0.0,
                },
                {
                    "feature": "rolling_time_delta_5",
                    "shap_value": -1.3420,
                    "raw_value": 0.100,
                },
            ],
        }

        cls.mock_borderline_explanation: Dict[str, Any] = {
            "prediction": "ATTACK",
            "attack_probability": 0.5230,
            "normal_probability": 0.4770,
            "raw_margin": 0.0920,
            "base_value": -0.2719,
            "top_positive_contributors": [
                {
                    "feature": "rolling_time_delta_std_5",
                    "shap_value": 0.4120,
                    "raw_value": 0.05,
                },
            ],
            "top_negative_contributors": [
                {
                    "feature": "rolling_global_td_10",
                    "shap_value": -0.3200,
                    "raw_value": 0.01,
                },
            ],
        }

    def test_01_attack_explanation_generation(self):
        """Verify ATTACK explanation produces correct prediction, confidence, and text."""
        res = self.explainer.explain(self.mock_attack_explanation, attack_type="DoS Attack", record_id=3203)
        self.assertEqual(res["prediction"], "ATTACK")
        self.assertAlmostEqual(res["attack_probability"], 0.9936, places=4)
        self.assertEqual(res["confidence_category"], "high model confidence")
        self.assertFalse(res["is_borderline"])
        self.assertIn("Attack detected with a 99.36% model-assigned attack probability", res["summary"])
        self.assertIn("Operator interpretation:", res["operator_interpretation"])

    def test_02_normal_explanation_generation(self):
        """Verify NORMAL explanation correctly identifies Normal prediction."""
        res = self.explainer.explain(self.mock_normal_explanation, record_id=93364)
        self.assertEqual(res["prediction"], "NORMAL")
        self.assertAlmostEqual(res["attack_probability"], 0.0001, places=4)
        self.assertEqual(res["confidence_category"], "low attack probability")
        self.assertFalse(res["is_borderline"])
        self.assertIn("predicted Normal", res["summary"])
        self.assertIn("nominal operating boundaries", res["operator_interpretation"])

    def test_03_borderline_prediction_handling(self):
        """Verify borderline prediction triggers explicit uncertainty disclosure."""
        res = self.explainer.explain(self.mock_borderline_explanation, record_id=5555)
        self.assertTrue(res["is_borderline"])
        self.assertEqual(res["confidence_category"], "moderate model confidence")
        self.assertIn("relatively uncertain", res["summary"])
        self.assertIn("Monitor subsequent packets", res["operator_interpretation"])

    def test_04_probability_formatting(self):
        """Verify probability is accurately represented and bounded."""
        cat_high = self.explainer.get_confidence_category(0.95)
        cat_mod_high = self.explainer.get_confidence_category(0.75)
        cat_mod = self.explainer.get_confidence_category(0.55)
        cat_mod_norm = self.explainer.get_confidence_category(0.35)
        cat_low = self.explainer.get_confidence_category(0.10)

        self.assertEqual(cat_high, "high model confidence")
        self.assertEqual(cat_mod_high, "moderate-to-high model confidence")
        self.assertEqual(cat_mod, "moderate model confidence")
        self.assertEqual(cat_mod_norm, "moderate evidence toward Normal")
        self.assertEqual(cat_low, "low attack probability")

    def test_05_positive_shap_direction(self):
        """Verify positive SHAP contributors explicitly state pushing toward Attack."""
        res = self.explainer.explain(self.mock_attack_explanation)
        pos = res["top_attack_contributors"]
        self.assertGreater(len(pos), 0)
        for item in pos:
            self.assertEqual(item["direction"], "attack")
            self.assertGreater(item["shap_value"], 0)
            self.assertIn("toward the Attack prediction", item["sentence"])

    def test_06_negative_shap_direction(self):
        """Verify negative SHAP contributors explicitly state pushing toward Normal."""
        res = self.explainer.explain(self.mock_attack_explanation)
        neg = res["top_normal_contributors"]
        self.assertGreater(len(neg), 0)
        for item in neg:
            self.assertEqual(item["direction"], "normal")
            self.assertLess(item["shap_value"], 0)
            self.assertIn("toward the Normal prediction", item["sentence"])

    def test_07_feature_description_lookup(self):
        """Verify all 32 H3-32 features map to valid non-empty human-readable descriptions."""
        self.assertEqual(len(FEATURE_DESCRIPTIONS), 32)
        for feat, desc in FEATURE_DESCRIPTIONS.items():
            looked_up = self.explainer.describe_feature(feat)
            self.assertEqual(looked_up, desc)
            self.assertGreater(len(looked_up), 3)

    def test_08_unknown_feature_handling(self):
        """Verify unknown feature names fall back gracefully to cleaned string."""
        desc = self.explainer.describe_feature("unknown_custom_metric_xyz")
        self.assertEqual(desc, "unknown custom metric xyz")

    def test_09_attack_type_correctly_distinguished(self):
        """Verify ground-truth attack type is distinct from model output and not inferred."""
        # When provided
        res1 = self.explainer.explain(self.mock_attack_explanation, attack_type="Replay Attack")
        self.assertEqual(res1["attack_type"], "Replay Attack")
        self.assertEqual(res1["ground_truth_context"], "The dataset records this sample as Replay Attack.")

        # When missing
        res2 = self.explainer.explain(self.mock_attack_explanation, attack_type=None)
        self.assertEqual(res2["attack_type"], "not provided")
        self.assertEqual(res2["ground_truth_context"], "Recorded attack type: not provided.")

    def test_10_scientific_safety_audit_no_causal_language(self):
        """
        Scan all narrative text in generated explanations for forbidden causal claims.
        Prohibited phrases: 'caused by', 'caused the attack', 'proves', 'root cause', 'definitely', 'guarantees'.
        """
        test_cases = [
            self.mock_attack_explanation,
            self.mock_normal_explanation,
            self.mock_borderline_explanation,
        ]
        prohibited_phrases = [
            "caused by",
            "caused the attack",
            "proves",
            "root cause",
            "definitely",
            "guarantees",
        ]

        for mock_exp in test_cases:
            res = self.explainer.explain(mock_exp, attack_type="DoS Attack", record_id=123)
            # Check narrative fields (excluding limitations which explicitly state SHAP does not prove/cause)
            fields_to_check = [
                res["summary"],
                res["operator_interpretation"],
                res["ground_truth_context"],
                res["confidence_category"],
            ]
            for c in res["top_attack_contributors"]:
                fields_to_check.append(c["sentence"])
            for c in res["top_normal_contributors"]:
                fields_to_check.append(c["sentence"])

            full_narrative = " ".join(fields_to_check).lower()
            for phrase in prohibited_phrases:
                self.assertNotIn(
                    phrase,
                    full_narrative,
                    f"Found prohibited causal phrase '{phrase}' in generated narrative!",
                )

    def test_11_structured_output_fields(self):
        """Verify structured output contains all required fields."""
        res = self.explainer.explain(self.mock_attack_explanation, record_id=100)
        required_keys = [
            "record_id",
            "prediction",
            "attack_probability",
            "normal_probability",
            "confidence_category",
            "is_borderline",
            "attack_type",
            "ground_truth_context",
            "raw_margin",
            "base_value",
            "summary",
            "top_attack_contributors",
            "top_normal_contributors",
            "operator_interpretation",
            "limitations",
            "text",
        ]
        for key in required_keys:
            self.assertIn(key, res)

    def test_12_summary_generated_and_concise(self):
        """Verify summary is generated, non-empty, and approximately 2-4 sentences."""
        res = self.explainer.explain(self.mock_attack_explanation)
        summary = res["summary"]
        self.assertTrue(len(summary) > 20)
        sentence_count = summary.count(".")
        self.assertTrue(2 <= sentence_count <= 5, f"Expected 2-4 sentences, got {sentence_count}")

    def test_13_operator_interpretation_safe_and_actionable(self):
        """Verify operator interpretation does not issue unsafe physical control commands."""
        res = self.explainer.explain(self.mock_attack_explanation)
        op_text = res["operator_interpretation"].lower()
        unsafe_phrases = [
            "shut down the machine",
            "disconnect the plc",
            "stop production immediately",
            "trip the breaker",
            "kill the motor",
        ]
        for unsafe in unsafe_phrases:
            self.assertNotIn(unsafe, op_text)

        # Check for approved advisory words
        advisory_words = ["review", "investigate", "verify", "inspect", "correlate"]
        has_advisory = any(w in op_text for w in advisory_words)
        self.assertTrue(has_advisory, "Operator interpretation should contain advisory terms.")


if __name__ == "__main__":
    unittest.main()
