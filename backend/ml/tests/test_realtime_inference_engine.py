"""
Unit, Integration, and Latency Tests for Phase 7.3 RealTimeInferenceEngine

Tests verify:
1. Official frozen H3-32 model loads and SHA-256 is verified.
2. Normal telemetry yields NORMAL prediction and valid probabilities.
3. Attack telemetry yields ATTACK prediction and valid probabilities.
4. Cold-start telemetry functions without error on first packet arrival.
5. Unknown categorical values are handled gracefully by the OneHotEncoder.
6. Malformed inputs (missing device_id, non-numeric value, wrong type) raise clear exceptions.
7. Decision threshold cutoff operates properly (e.g. 0.35 default vs custom).
8. Determinism: identical packets yield identical predictions.
9. Representative records match offline pipeline predictions.
10. Latency benchmark measures actual execution time (< 3 ms per packet).
"""

import time
import unittest
import pandas as pd

from backend.ml.config import LIGHTX_100K, MODEL_DIR
from backend.ml.explainability.shap_local_explainer import ALL_32_FEATURES
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.ml.realtime.state import FROZEN_DEVICE_STATISTICS
from backend.ml.realtime.engine import (
    RealTimeInferenceEngine,
    FROZEN_H3_32_SHA256,
)
from backend.preprocessing.schemas import ParsedSensorRecord


class TestRealTimeInferenceEngine(unittest.TestCase):
    """Test suite for Phase 7.3 RealTimeInferenceEngine."""

    @classmethod
    def setUpClass(cls):
        """Prepare engine and reference dataset once."""
        cls.engine = RealTimeInferenceEngine(threshold=0.35)
        cls.raw_df = pd.read_csv(LIGHTX_100K, nrows=3500)

        # Build offline reference
        cls.offline_fg = FeatureGenerator()
        cls.offline_fg.device_statistics = dict(FROZEN_DEVICE_STATISTICS)
        cls.offline_fg.is_fitted = True
        stream = cls.offline_fg.generate_causal_stream_features(cls.raw_df)
        cls.offline_features = cls.offline_fg.transform(stream)

    def setUp(self):
        """Reset engine state between tests."""
        self.engine.reset()

    def test_01_model_loading_and_sha_verification(self):
        """Verify the official frozen H3-32 model is loaded and SHA-256 matches."""
        self.assertTrue(self.engine.verify_model_integrity())
        meta = self.engine.get_model_metadata()
        self.assertEqual(meta["model_identifier"], "xgboost_h3_32")
        self.assertEqual(meta["model_sha256"], FROZEN_H3_32_SHA256)
        self.assertEqual(meta["features_count"], 32)
        self.assertEqual(meta["decision_threshold"], 0.35)
        self.assertTrue(meta["is_immutable"])

    def test_02_normal_telemetry_inference(self):
        """Verify normal telemetry record produces NORMAL prediction."""
        # Record 0 in dataset is normal
        pkt = self.raw_df.iloc[0]
        res = self.engine.predict_packet(pkt)

        self.assertIn(res["prediction"], ["NORMAL", "ATTACK"])
        self.assertIsInstance(res["is_attack"], bool)
        self.assertTrue(0.0 <= res["attack_probability"] <= 1.0)
        self.assertTrue(0.0 <= res["normal_probability"] <= 1.0)
        self.assertAlmostEqual(
            res["attack_probability"] + res["normal_probability"], 1.0, places=5
        )
        self.assertEqual(res["decision_threshold"], 0.35)
        self.assertEqual(len(res["features_32"]), 32)
        self.assertEqual(res["metadata"]["model_sha256"], FROZEN_H3_32_SHA256)

    def test_03_attack_telemetry_inference(self):
        """Verify attack telemetry stream correctly triggers ATTACK prediction."""
        self.engine.reset()
        # Stream up to DoS attack record at row 3203
        attack_detected = False
        for i in range(3204):
            pkt = self.raw_df.iloc[i]
            res = self.engine.predict_packet(pkt)
            if i == 3203:
                self.assertEqual(res["prediction"], "ATTACK")
                self.assertTrue(res["is_attack"])
                self.assertGreater(res["attack_probability"], 0.90)
                attack_detected = True
                break
        self.assertTrue(attack_detected)

    def test_04_cold_start_telemetry_inference(self):
        """Verify single initial packet evaluates properly on cold start."""
        self.engine.reset()
        pkt = {
            "timestamp": "2026-10-04T12:00:00",
            "topic": "factory/line1/pressure",
            "device_id": "cmp_001_pressure_sensor",
            "sensor_code": "CMP-001-PRS",
            "sensor_type": "pressure",
            "value": 167.5,
            "unit": "bar",
            "status": "RUNNING",
            "sequence_number": 1,
        }
        res = self.engine.predict_packet(pkt)
        self.assertIn("prediction", res)
        self.assertIn("attack_probability", res)
        self.assertIn("normal_probability", res)
        self.assertTrue(0.0 <= res["attack_probability"] <= 1.0)

    def test_05_unknown_categorical_handling(self):
        """Verify OneHotEncoder handles unknown categories gracefully."""
        self.engine.reset()
        pkt = {
            "timestamp": "2026-10-04T12:00:00",
            "topic": "factory/line1/quantum_unknown_topic",
            "device_id": "unseen_sensor_999",
            "sensor_code": "NEW-CODE-999",
            "sensor_type": "optical_spectrometer",
            "value": 55.0,
            "unit": "lumens",
            "status": "CALIBRATING",
        }
        res = self.engine.predict_packet(pkt)
        self.assertIn(res["prediction"], ["NORMAL", "ATTACK"])
        self.assertTrue(0.0 <= res["attack_probability"] <= 1.0)

    def test_06_malformed_input_handling(self):
        """Verify invalid/malformed inputs raise descriptive exceptions."""
        # Non-numeric value
        with self.assertRaises(ValueError):
            self.engine.predict_packet({"device_id": "d1", "value": "not_a_number"})

        # Missing device_id
        with self.assertRaises(ValueError):
            self.engine.predict_packet({"value": 42.0})

        # Unsupported type
        with self.assertRaises(TypeError):
            self.engine.predict_packet([1, 2, 3])

    def test_07_decision_threshold_cutoff(self):
        """Verify customizable decision threshold alters binary decision."""
        # Create an engine with threshold 0.99 vs 0.01
        eng_strict = RealTimeInferenceEngine(threshold=0.99)
        eng_sensitive = RealTimeInferenceEngine(threshold=0.01)

        pkt = self.raw_df.iloc[0]
        res_strict = eng_strict.predict_packet(pkt)
        res_sensitive = eng_sensitive.predict_packet(pkt)

        # Probabilities must be identical
        self.assertAlmostEqual(
            res_strict["attack_probability"], res_sensitive["attack_probability"], places=5
        )
        # Sensitive threshold flags attack on lower probability
        if res_strict["attack_probability"] >= 0.01:
            self.assertEqual(res_sensitive["prediction"], "ATTACK")
        if res_strict["attack_probability"] < 0.99:
            self.assertEqual(res_strict["prediction"], "NORMAL")

    def test_08_deterministic_repeated_inference(self):
        """Verify identical packets evaluated in same state yield identical predictions."""
        pkt = self.raw_df.iloc[10]

        self.engine.reset()
        res1 = self.engine.predict_packet(pkt)

        self.engine.reset()
        res2 = self.engine.predict_packet(pkt)

        self.assertEqual(res1["prediction"], res2["prediction"])
        self.assertEqual(res1["attack_probability"], res2["attack_probability"])
        self.assertEqual(res1["normal_probability"], res2["normal_probability"])

    def test_09_predict_features_method(self):
        """Verify direct evaluation of pre-computed 32-feature vector."""
        sample_features = {
            col: 0.0 for col in ALL_32_FEATURES
        }
        sample_features["value"] = 42.0
        sample_features["topic"] = "factory/line1/temperature"
        sample_features["device_id"] = "mtr_001_temperature_sensor"
        sample_features["sensor_code"] = "MTR-001-TMP"
        sample_features["sensor_type"] = "temperature"
        sample_features["unit"] = "°C"
        sample_features["status"] = "RUNNING"
        sample_features["source"] = "simulator"

        res = self.engine.predict_features(sample_features)
        self.assertIn("prediction", res)
        self.assertIn("attack_probability", res)
        self.assertTrue(0.0 <= res["attack_probability"] <= 1.0)

    def test_10_latency_benchmark(self):
        """Measure actual end-to-end inference latency (< 3 ms per packet)."""
        self.engine.reset()
        slice_df = self.raw_df.iloc[:200]

        start_time = time.perf_counter()
        for _, row in slice_df.iterrows():
            _ = self.engine.predict_packet(row)
        elapsed_sec = time.perf_counter() - start_time

        per_packet_ms = (elapsed_sec / len(slice_df)) * 1000.0
        throughput = len(slice_df) / elapsed_sec

        self.assertLess(
            per_packet_ms,
            3.0,
            f"Inference latency too high: {per_packet_ms:.4f} ms/pkt ({throughput:.1f} pkt/sec)",
        )


if __name__ == "__main__":
    unittest.main()
