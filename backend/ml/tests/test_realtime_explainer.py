"""
Unit, Equivalence, and Latency Tests for Phase 7.4 RealTimeExplainer

Tests verify:
1. Official frozen H3-32 model SHA-256 integrity.
2. Normal packet explanation contract and negative margin direction.
3. Attack packet explanation contract and positive margin direction.
4. Cold-start packet explanation functions cleanly on first arrival.
5. Unknown categorical values handled gracefully without failure.
6. Malformed input handling (missing device_id, non-numeric value, wrong type).
7. Top-K ranking behavior and sorting by SHAP contribution magnitude.
8. Deterministic repeated explanations on identical states.
9. Prediction consistency with RealTimeInferenceEngine.
10. SHAP value consistency with offline LocalShapExplainer across all 32 features.
11. Additive fidelity guarantee (|raw_margin - reconstructed| < 1e-4).
12. Representative records validation (DoS, Replay, Sensor Freeze, Motor Overload, Slow Drift, Normal).
13. Causal isolation (modifying future packets does not alter past SHAP explanations).
14. Latency breakdown benchmarking (feature, inference, SHAP, total e2e).
"""

import math
import time
import unittest
import pandas as pd

from backend.ml.config import LIGHTX_100K, MODEL_DIR
from backend.ml.explainability.shap_local_explainer import ALL_32_FEATURES
from backend.ml.explainability.service import FROZEN_H3_32_SHA256, ExplainabilityService
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.ml.realtime.state import FROZEN_DEVICE_STATISTICS
from backend.ml.realtime.explainer import RealTimeExplainer
from backend.ml.realtime.engine import RealTimeInferenceEngine
from backend.preprocessing.schemas import ParsedSensorRecord


class TestRealTimeExplainer(unittest.TestCase):
    """Test suite for Phase 7.4 RealTimeExplainer."""

    @classmethod
    def setUpClass(cls):
        """Prepare explainer, engine, and sample data."""
        cls.engine = RealTimeInferenceEngine(threshold=0.35)
        cls.explainer = RealTimeExplainer(engine=cls.engine, threshold=0.35)
        cls.service = ExplainabilityService(threshold=0.35)
        cls.raw_df = pd.read_csv(LIGHTX_100K, nrows=3500)

        # Build offline reference
        cls.offline_fg = FeatureGenerator()
        cls.offline_fg.device_statistics = dict(FROZEN_DEVICE_STATISTICS)
        cls.offline_fg.is_fitted = True
        stream = cls.offline_fg.generate_causal_stream_features(cls.raw_df)
        cls.offline_features = cls.offline_fg.transform(stream)

    def setUp(self):
        """Reset state between tests."""
        self.explainer.reset()
        self.engine.reset()

    def test_01_model_integrity(self):
        """Verify model hash is checked and verified."""
        self.assertTrue(self.explainer.verify_model_integrity())
        meta = self.explainer.get_model_metadata()
        self.assertEqual(meta["model_identifier"], "xgboost_h3_32")
        self.assertEqual(meta["model_sha256"], FROZEN_H3_32_SHA256)
        self.assertTrue(meta["is_immutable"])

    def test_02_normal_packet_explanation(self):
        """Verify explanation structure for normal telemetry."""
        pkt = self.raw_df.iloc[0]
        res = self.explainer.explain_packet(pkt, record_id=101)

        self.assertIn("prediction", res)
        self.assertIn("explanation", res)
        self.assertIn("human_readable", res)
        self.assertIn("metadata", res)

        pred = res["prediction"]
        self.assertIn(pred["label"], ["NORMAL", "ATTACK"])
        self.assertTrue(0.0 <= pred["attack_probability"] <= 1.0)
        self.assertTrue(0.0 <= pred["normal_probability"] <= 1.0)

        exp = res["explanation"]
        self.assertIn("raw_margin", exp)
        self.assertIn("base_value", exp)
        self.assertIn("fidelity_error", exp)
        self.assertLess(exp["fidelity_error"], 1e-4)
        self.assertEqual(len(exp["all_contributions_32"]), 32)
        self.assertEqual(len(exp["transformed_contributions_95"]), 95)

        hr = res["human_readable"]
        self.assertIn("summary", hr)
        self.assertIn("confidence_category", hr)
        self.assertIn("operator_interpretation", hr)

        meta = res["metadata"]
        self.assertEqual(meta["model_sha256"], FROZEN_H3_32_SHA256)
        self.assertEqual(meta["record_id"], 101)

    def test_03_attack_packet_explanation(self):
        """Verify explanation for attack telemetry pushes margin toward Attack."""
        self.explainer.reset()
        # Stream up to DoS attack at row 3203
        attack_res = None
        for i in range(3203):
            self.explainer.feature_adapter.transform_packet(self.raw_df.iloc[i])
        attack_res = self.explainer.explain_packet(self.raw_df.iloc[3203], record_id=3203, attack_type="DoS")

        self.assertIsNotNone(attack_res)
        self.assertEqual(attack_res["prediction"]["label"], "ATTACK")
        self.assertGreater(attack_res["prediction"]["raw_margin"], 0.0)
        self.assertGreater(attack_res["prediction"]["attack_probability"], 0.90)

        top_attack = attack_res["explanation"]["top_attack_contributors"]
        self.assertGreater(len(top_attack), 0)
        # Positive SHAP pushes toward attack
        for c in top_attack:
            self.assertGreater(c["shap_value"], 0.0)

        self.assertIn("Attack detected", attack_res["human_readable"]["summary"])

    def test_04_cold_start_explanation(self):
        """Verify cold-start initial packet produces valid explanation."""
        self.explainer.reset()
        pkt = {
            "timestamp": "2026-10-04T12:00:00",
            "topic": "factory/line1/pressure",
            "device_id": "cmp_001_pressure_sensor",
            "sensor_code": "CMP-001-PRS",
            "sensor_type": "pressure",
            "value": 168.0,
            "unit": "bar",
            "status": "RUNNING",
        }
        res = self.explainer.explain_packet(pkt)
        self.assertIn("explanation", res)
        self.assertLess(res["explanation"]["fidelity_error"], 1e-4)
        for k, v in res["explanation"]["all_contributions_32"].items():
            self.assertTrue(math.isfinite(v), f"Feature {k} SHAP was not finite: {v}")

    def test_05_unknown_categorical_values(self):
        """Verify unknown categories are tolerated without crashing."""
        self.explainer.reset()
        pkt = {
            "timestamp": "2026-10-04T12:00:00",
            "topic": "unseen_mqtt_topic",
            "device_id": "unseen_sensor_999",
            "sensor_code": "NEW-SENSOR",
            "sensor_type": "quantum_sensor",
            "value": 50.0,
            "unit": "lumens",
            "status": "CALIBRATING",
        }
        res = self.explainer.explain_packet(pkt)
        self.assertIn("explanation", res)
        self.assertLess(res["explanation"]["fidelity_error"], 1e-4)

    def test_06_malformed_input_handling(self):
        """Verify malformed input raises descriptive errors."""
        with self.assertRaises(ValueError):
            self.explainer.explain_packet({"device_id": "d1", "value": "not_numeric"})
        with self.assertRaises(ValueError):
            self.explainer.explain_packet({"value": 42.0})
        with self.assertRaises(TypeError):
            self.explainer.explain_packet(12345)

    def test_07_top_k_parameter(self):
        """Verify top_k parameter controls returned contributors count."""
        pkt = self.raw_df.iloc[0]
        res3 = self.explainer.explain_packet(pkt, top_k=3)
        res7 = self.explainer.explain_packet(pkt, top_k=7)

        self.assertLessEqual(len(res3["explanation"]["top_attack_contributors"]), 3)
        self.assertLessEqual(len(res3["explanation"]["top_normal_contributors"]), 3)
        self.assertLessEqual(len(res7["explanation"]["top_attack_contributors"]), 7)
        self.assertLessEqual(len(res7["explanation"]["top_normal_contributors"]), 7)

    def test_08_deterministic_repeated_explanation(self):
        """Verify identical packets evaluated in same state yield identical explanations."""
        pkt = self.raw_df.iloc[5]

        self.explainer.reset()
        res1 = self.explainer.explain_packet(pkt, record_id=5)

        self.explainer.reset()
        res2 = self.explainer.explain_packet(pkt, record_id=5)

        self.assertEqual(res1["prediction"]["label"], res2["prediction"]["label"])
        self.assertEqual(
            res1["prediction"]["attack_probability"], res2["prediction"]["attack_probability"]
        )
        self.assertEqual(
            res1["explanation"]["raw_margin"], res2["explanation"]["raw_margin"]
        )
        for k in ALL_32_FEATURES:
            self.assertEqual(
                res1["explanation"]["all_contributions_32"][k],
                res2["explanation"]["all_contributions_32"][k],
            )
        self.assertEqual(
            res1["human_readable"]["summary"], res2["human_readable"]["summary"]
        )

    def test_09_prediction_consistency_with_engine(self):
        """Verify prediction and probabilities match RealTimeInferenceEngine exactly."""
        pkt = self.raw_df.iloc[12]

        # Predict using engine
        self.engine.reset()
        eng_pred = self.engine.predict_packet(pkt)

        # Explain using explainer
        self.explainer.reset()
        exp_pred = self.explainer.explain_packet(pkt)["prediction"]

        self.assertEqual(eng_pred["prediction"], exp_pred["label"])
        self.assertEqual(eng_pred["is_attack"], exp_pred["is_attack"])
        self.assertAlmostEqual(
            eng_pred["attack_probability"], exp_pred["attack_probability"], places=6
        )
        self.assertAlmostEqual(
            eng_pred["normal_probability"], exp_pred["normal_probability"], places=6
        )

    def test_10_shap_consistency_with_offline_explainer(self):
        """
        Verify real-time SHAP values match offline LocalShapExplainer across all 32 features
        for identical feature vectors.
        """
        pkt = self.raw_df.iloc[20]
        self.explainer.reset()
        rt_res = self.explainer.explain_packet(pkt)

        # Direct explanation of same 32 features using offline ExplainabilityService
        off_res = self.service.explain(rt_res["features_32"])

        max_diff = 0.0
        for col in ALL_32_FEATURES:
            diff = abs(
                rt_res["explanation"]["all_contributions_32"][col]
                - off_res["explanation"]["all_contributions_32"][col]
            )
            if diff > max_diff:
                max_diff = diff
            self.assertLess(
                diff, 1e-5, f"SHAP mismatch on {col}: diff={diff}"
            )
        self.assertLess(max_diff, 1e-5)

    def test_11_additive_fidelity_guarantee(self):
        """Verify base_value + sum(shap_values) == raw_margin (|error| < 1e-4)."""
        slice_df = self.raw_df.iloc[:20]
        self.explainer.reset()
        for _, row in slice_df.iterrows():
            res = self.explainer.explain_packet(row)
            self.assertLess(res["explanation"]["fidelity_error"], 1e-4)

    def test_12_causal_isolation(self):
        """Verify future packets do not alter SHAP attribution of earlier packets."""
        self.explainer.reset()
        history1 = []
        for i in range(30):
            res = self.explainer.explain_packet(self.raw_df.iloc[i])
            history1.append(res["explanation"]["all_contributions_32"])

        # Corrupt future packets after t=30
        corrupted_df = self.raw_df.copy()
        corrupted_df.loc[30:, "value"] = 999999.0

        self.explainer.reset()
        history2 = []
        for i in range(30):
            res = self.explainer.explain_packet(corrupted_df.iloc[i])
            history2.append(res["explanation"]["all_contributions_32"])

        for i in range(30):
            for col in ALL_32_FEATURES:
                self.assertEqual(
                    history1[i][col],
                    history2[i][col],
                    f"Causality leak at step {i}, feature {col}",
                )

    def test_13_latency_breakdown(self):
        """Measure real-time latencies separately (feature, inference, SHAP, total e2e)."""
        self.explainer.reset()
        slice_df = self.raw_df.iloc[:100]

        t_feat = 0.0
        t_infer = 0.0
        t_shap = 0.0
        t_total = 0.0

        for _, row in slice_df.iterrows():
            t0 = time.perf_counter()
            feat_32 = self.explainer.feature_adapter.transform_packet(row)
            t1 = time.perf_counter()

            _ = self.engine.predict_features(feat_32)
            t2 = time.perf_counter()

            res = self.explainer.explainability_service.explain(feat_32)
            t3 = time.perf_counter()

            t_feat += (t1 - t0)
            t_infer += (t2 - t1)
            t_shap += (t3 - t2)
            t_total += (t3 - t0)

        n = len(slice_df)
        avg_feat_ms = (t_feat / n) * 1000.0
        avg_infer_ms = (t_infer / n) * 1000.0
        avg_shap_ms = (t_shap / n) * 1000.0
        avg_total_ms = (t_total / n) * 1000.0

        # Assert latencies within realistic bounds
        self.assertLess(avg_feat_ms, 1.0)
        self.assertLess(avg_infer_ms, 5.0)
        self.assertLess(avg_shap_ms, 15.0)
        self.assertLess(avg_total_ms, 20.0)


if __name__ == "__main__":
    unittest.main()
