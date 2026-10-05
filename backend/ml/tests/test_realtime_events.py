"""
Test Suite for Real-Time Detection Events & Alert Dispatching (Phase 7.5)

Tests:
1. Normal packet event generation.
2. Attack packet event generation.
3. Threshold boundary behavior (prob < 0.35 -> NORMAL, prob >= 0.35 -> ATTACK).
4. Deterministic severity calculation (NORMAL, LOW, MEDIUM, HIGH).
5. Cold-start packet handling.
6. Unknown categorical values and missing optional metadata.
7. Malformed input error handling.
8. Selective SHAP behavior (on_attack, always, never, on_demand, explicit override).
9. State preservation: features_32 reuse prevents double state updates.
10. Event deduplication and cooldown suppression vs default event-per-detection.
11. Listener callbacks: all-event subscribers vs alert-only subscribers.
12. Determinism and serialization (to_dict, to_json, from_dict).
13. Model SHA immutability and metadata propagation.
14. Representative attacks validation (DoS, Replay, Sensor Freeze, Motor Overload, Slow Drift, Normal).
"""

import json
from pathlib import Path
import unittest
import pandas as pd
import numpy as np

from backend.ml.config import LIGHTX_100K, MODEL_DIR
from backend.ml.realtime.engine import (
    RealTimeInferenceEngine,
    FROZEN_H3_32_SHA256,
    DEFAULT_DECISION_THRESHOLD,
    MODEL_IDENTIFIER,
)
from backend.ml.realtime.events import (
    DetectionEvent,
    EventSeverity,
    calculate_severity,
    RealTimeAlertDispatcher,
)
from backend.ml.realtime.explainer import RealTimeExplainer
from backend.preprocessing.schemas import ParsedSensorRecord


class TestRealTimeEvents(unittest.TestCase):
    """Unit and integration tests for Phase 7.5 RealTimeAlertDispatcher and DetectionEvent."""

    @classmethod
    def setUpClass(cls):
        """Load telemetry data for representative attacks and normal packets."""
        cls.raw_df = pd.read_csv(LIGHTX_100K)

    def setUp(self):
        """Instantiate a fresh dispatcher for each test."""
        self.dispatcher = RealTimeAlertDispatcher(
            threshold=DEFAULT_DECISION_THRESHOLD,
            explain_mode="on_attack",
            dedup_window_seconds=0.0,
            verify_hash=True,
        )

    def test_01_severity_calculation(self):
        """Verify deterministic confidence-based severity levels."""
        self.assertEqual(calculate_severity(0.00), "NORMAL")
        self.assertEqual(calculate_severity(0.3499), "NORMAL")
        self.assertEqual(calculate_severity(0.35), "LOW")
        self.assertEqual(calculate_severity(0.5999), "LOW")
        self.assertEqual(calculate_severity(0.60), "MEDIUM")
        self.assertEqual(calculate_severity(0.8499), "MEDIUM")
        self.assertEqual(calculate_severity(0.85), "HIGH")
        self.assertEqual(calculate_severity(1.00), "HIGH")

    def test_02_normal_packet_event(self):
        """Verify normal telemetry packet generates non-attack DetectionEvent without SHAP."""
        normal_pkt = self.raw_df.iloc[93364].to_dict()
        event = self.dispatcher.process_packet(normal_pkt, record_id=93364)

        self.assertIsInstance(event, DetectionEvent)
        self.assertEqual(event.prediction, "NORMAL")
        self.assertFalse(event.is_attack)
        self.assertLess(event.attack_probability, 0.35)
        self.assertEqual(event.severity, "NORMAL")
        self.assertEqual(event.device_id, str(normal_pkt["device_id"]))
        self.assertEqual(event.model_sha256, FROZEN_H3_32_SHA256)
        self.assertEqual(event.decision_threshold, 0.35)

        # In 'on_attack' mode, normal packet must NOT trigger SHAP
        self.assertIsNone(event.explanation)
        self.assertIsNone(event.human_readable)
        self.assertIn("features_32", event.to_dict())

    def test_03_attack_packet_event_with_selective_shap(self):
        """Verify attack telemetry generates ATTACK event with attached SHAP explanation."""
        # Warm up state up to DoS attack at row 3203
        for i in range(3203):
            self.dispatcher.engine.feature_adapter.transform_packet(self.raw_df.iloc[i])

        attack_pkt = self.raw_df.iloc[3203].to_dict()
        event = self.dispatcher.process_packet(
            attack_pkt,
            record_id=3203,
            attack_type="DoS",
        )

        self.assertIsInstance(event, DetectionEvent)
        self.assertEqual(event.prediction, "ATTACK")
        self.assertTrue(event.is_attack)
        self.assertGreaterEqual(event.attack_probability, 0.35)
        self.assertEqual(event.severity, "HIGH")  # DoS is >0.99
        self.assertEqual(event.model_sha256, FROZEN_H3_32_SHA256)

        # In 'on_attack' mode, attack packet MUST trigger SHAP
        self.assertIsNotNone(event.explanation)
        self.assertIsNotNone(event.human_readable)
        self.assertIn("top_attack_contributors", event.explanation)
        self.assertGreater(len(event.explanation["top_attack_contributors"]), 0)
        self.assertIn("Attack detected", event.human_readable["summary"])

    def test_04_cold_start_packet(self):
        """Verify first packet on uninitialized state processes cleanly."""
        first_pkt = self.raw_df.iloc[0].to_dict()
        event = self.dispatcher.process_packet(first_pkt, record_id=0)

        self.assertIsInstance(event, DetectionEvent)
        self.assertIn(event.prediction, ("NORMAL", "ATTACK"))
        self.assertEqual(event.model_sha256, FROZEN_H3_32_SHA256)
        self.assertIsNotNone(event.event_id)

    def test_05_unknown_categorical_and_missing_metadata(self):
        """Verify unknown categorical values and missing optional fields are handled safely."""
        synthetic_packet = {
            "device_id": "unknown_experimental_dev_999",
            "sensor_type": "quantum_graviton_flux",  # unknown category
            "value": 42.0,
            "unit": "gravitons",
            "status": "UNKNOWN_STATE",
            "timestamp": "2026-10-04T12:00:00Z",
            # missing: topic, sensor_code, record_id
        }

        event = self.dispatcher.process_packet(synthetic_packet)
        self.assertIsInstance(event, DetectionEvent)
        self.assertEqual(event.device_id, "unknown_experimental_dev_999")
        self.assertIsNone(event.sensor_code)
        self.assertIsNone(event.topic)
        self.assertEqual(event.model_sha256, FROZEN_H3_32_SHA256)

    def test_06_malformed_input_rejection(self):
        """Verify malformed input missing device_id or non-numeric value raises ValueError."""
        with self.assertRaises(ValueError):
            self.dispatcher.process_packet({"value": 10.0})  # missing device_id

        with self.assertRaises(ValueError):
            self.dispatcher.process_packet({
                "device_id": "mtr_001",
                "value": "corrupted_string_not_a_float",
            })

        with self.assertRaises(TypeError):
            self.dispatcher.process_packet(["invalid_list_packet"])

    def test_07_selective_shap_modes(self):
        """Verify all explain_mode configurations and explicit overrides."""
        normal_pkt = self.raw_df.iloc[93364].to_dict()

        # Mode 'never': even if explicit_explain=None, never explain
        never_dispatcher = RealTimeAlertDispatcher(explain_mode="never")
        ev_never = never_dispatcher.process_packet(normal_pkt)
        self.assertIsNone(ev_never.explanation)

        # Mode 'always': explains even normal packets
        always_dispatcher = RealTimeAlertDispatcher(explain_mode="always")
        ev_always = always_dispatcher.process_packet(normal_pkt)
        self.assertIsNotNone(ev_always.explanation)

        # Explicit override explain=True overrides 'never' mode
        ev_override_true = never_dispatcher.process_packet(normal_pkt, explain=True)
        self.assertIsNotNone(ev_override_true.explanation)

        # Explicit override explain=False overrides 'always' mode
        ev_override_false = always_dispatcher.process_packet(normal_pkt, explain=False)
        self.assertIsNone(ev_override_false.explanation)

    def test_08_state_preservation_no_duplicate_updates(self):
        """Verify that selective SHAP does not cause double-updates to rolling windows."""
        pkt = self.raw_df.iloc[100].to_dict()

        # Process packet without explanation
        disp1 = RealTimeAlertDispatcher(explain_mode="never")
        ev1 = disp1.process_packet(pkt)
        window_len_1 = len(disp1.engine.feature_adapter.state_tracker.get_device_state(str(pkt["device_id"])).val_hist)

        # Process identical packet with explanation
        disp2 = RealTimeAlertDispatcher(explain_mode="always")
        ev2 = disp2.process_packet(pkt)
        window_len_2 = len(disp2.engine.feature_adapter.state_tracker.get_device_state(str(pkt["device_id"])).val_hist)

        # Window lengths must be identical (exactly 1 element added per packet)
        self.assertEqual(window_len_1, 1)
        self.assertEqual(window_len_2, 1)
        self.assertEqual(ev1.features_32, ev2.features_32)

    def test_09_deduplication_and_cooldown(self):
        """Verify alert deduplication / cooldown suppression when enabled vs default."""
        attack_pkt_1 = {
            "device_id": "mtr_001_vibration_sensor",
            "sensor_type": "vibration",
            "value": 999.0,  # anomalous spike
            "timestamp": "100.0",
        }
        attack_pkt_2 = {
            "device_id": "mtr_001_vibration_sensor",
            "sensor_type": "vibration",
            "value": 999.0,
            "timestamp": "102.0",  # 2 seconds later
        }

        # 1. Default (cooldown = 0.0): both alerts are unsuppressed (event-per-detection)
        disp_default = RealTimeAlertDispatcher(dedup_window_seconds=0.0)
        ev1 = disp_default.process_packet(attack_pkt_1)
        ev2 = disp_default.process_packet(attack_pkt_2)
        if ev1.is_attack and ev2.is_attack:
            self.assertFalse(ev1.is_suppressed)
            self.assertFalse(ev2.is_suppressed)

        # 2. Cooldown = 5.0 seconds: second alert within 2s is marked as suppressed
        disp_dedup = RealTimeAlertDispatcher(dedup_window_seconds=5.0)
        ev1_d = disp_dedup.process_packet(attack_pkt_1)
        ev2_d = disp_dedup.process_packet(attack_pkt_2)
        if ev1_d.is_attack and ev2_d.is_attack:
            self.assertFalse(ev1_d.is_suppressed)
            self.assertTrue(ev2_d.is_suppressed)
            self.assertTrue(ev2_d.is_duplicate)

    def test_10_listener_subscriptions(self):
        """Verify callback dispatching for all-event and alert-only subscribers."""
        all_events_received = []
        alerts_received = []

        self.dispatcher.subscribe(lambda ev: all_events_received.append(ev))
        self.dispatcher.subscribe_alerts(lambda ev: alerts_received.append(ev))

        # Send 1 normal packet
        normal_pkt = self.raw_df.iloc[93364].to_dict()
        self.dispatcher.process_packet(normal_pkt)

        self.assertEqual(len(all_events_received), 1)
        self.assertEqual(len(alerts_received), 0)

        # Send 1 attack packet
        for i in range(3203):
            self.dispatcher.engine.feature_adapter.transform_packet(self.raw_df.iloc[i])
        attack_pkt = self.raw_df.iloc[3203].to_dict()
        self.dispatcher.process_packet(attack_pkt)

        self.assertEqual(len(all_events_received), 2)
        self.assertEqual(len(alerts_received), 1)
        self.assertTrue(alerts_received[0].is_attack)

    def test_11_determinism_and_serialization(self):
        """Verify deterministic event ID, to_dict, to_json, and from_dict roundtrip."""
        pkt = self.raw_df.iloc[100].to_dict()

        ev1 = self.dispatcher.process_packet(pkt, record_id=100, event_id="custom_evt_100")
        self.dispatcher.reset()
        ev2 = self.dispatcher.process_packet(pkt, record_id=100, event_id="custom_evt_100")

        self.assertEqual(ev1.event_id, ev2.event_id)
        self.assertEqual(ev1.prediction, ev2.prediction)
        self.assertEqual(ev1.attack_probability, ev2.attack_probability)
        self.assertEqual(ev1.severity, ev2.severity)

        # Serialization roundtrip
        d = ev1.to_dict()
        json_str = ev1.to_json()
        self.assertIsInstance(json_str, str)
        reconstructed_dict = json.loads(json_str)

        ev_reconstructed = DetectionEvent.from_dict(reconstructed_dict)
        self.assertEqual(ev_reconstructed.event_id, ev1.event_id)
        self.assertEqual(ev_reconstructed.prediction, ev1.prediction)
        self.assertAlmostEqual(ev_reconstructed.attack_probability, ev1.attack_probability, places=6)

    def test_12_representative_attack_scenarios(self):
        """Verify event generation across all representative attack categories."""
        cases = [
            ("DoS", 3203, "ATTACK", "HIGH"),
            ("Replay", 10977, "ATTACK", "HIGH"),
            ("Sensor Freeze", 48510, "ATTACK", "HIGH"),
            ("Motor Overload", 75660, "ATTACK", "MEDIUM"),
            ("Slow Drift", 88360, "ATTACK", "HIGH"),
            ("Normal", 93364, "NORMAL", "NORMAL"),
        ]

        for attack_name, row_idx, expected_pred, expected_sev in cases:
            # Recreate dispatcher with warm state up to row_idx
            disp = RealTimeAlertDispatcher(explain_mode="on_attack")
            # Warm up
            start_row = max(0, row_idx - 100)
            for i in range(start_row, row_idx):
                disp.engine.feature_adapter.transform_packet(self.raw_df.iloc[i])

            pkt = self.raw_df.iloc[row_idx].to_dict()
            ev = disp.process_packet(pkt, record_id=row_idx, attack_type=attack_name)

            self.assertEqual(ev.prediction, expected_pred, f"Failed on {attack_name}")
            self.assertEqual(ev.severity, expected_sev, f"Failed on {attack_name}")
            self.assertEqual(ev.model_sha256, FROZEN_H3_32_SHA256)

            if expected_pred == "ATTACK":
                self.assertTrue(ev.is_attack)
                self.assertIsNotNone(ev.explanation)
                self.assertIsNotNone(ev.human_readable)
            else:
                self.assertFalse(ev.is_attack)
                self.assertIsNone(ev.explanation)

    def test_13_parsed_sensor_record_input(self):
        """Verify ParsedSensorRecord dataclass instances are processed cleanly."""
        rec = ParsedSensorRecord(
            timestamp="2026-10-04T12:00:00Z",
            topic="factory/conveyor/motor_01/temperature",
            device_id="mtr_001_temperature_sensor",
            sensor_type="temperature",
            value=65.5,
            unit="C",
            status="NORMAL",
            sensor_code="MTR-001-TMP",
        )
        ev = self.dispatcher.process_packet(rec, record_id=555)
        self.assertIsInstance(ev, DetectionEvent)
        self.assertEqual(ev.device_id, "mtr_001_temperature_sensor")
        self.assertEqual(ev.sensor_code, "MTR-001-TMP")
        self.assertEqual(ev.sensor_type, "temperature")
        self.assertEqual(ev.topic, "factory/conveyor/motor_01/temperature")
        self.assertEqual(ev.record_id, 555)


if __name__ == "__main__":
    unittest.main()
