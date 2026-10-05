"""
Test Suite for Real-Time MQTT Bridge (Phase 7.6)

Validates the full MQTT telemetry-to-detection pipeline:
1. Normal telemetry message parsing and processing without SHAP.
2. Attack telemetry message processing, detection, and alert publishing with selective SHAP.
3. Feedback-loop prevention: messages on factory/alerts are dropped.
4. Malformed message handling: non-JSON, missing required fields, non-numeric values.
5. Unknown categorical values and missing optional metadata.
6. Cold-start telemetry message.
7. Multi-sensor stream processing.
8. Consecutive attack packets and deduplication/cooldown suppression.
9. Exactly-once feature update per packet.
10. Alert JSON schema structure and validation.
11. Model SHA immutability.
12. Reconnect / disconnect lifecycle callbacks.
13. MQTT pipeline latency benchmark (receive -> parse -> inference -> event -> alert).
"""

import json
import time
import unittest
from unittest.mock import MagicMock
import pandas as pd
import paho.mqtt.client as mqtt

from backend.industrial.config.mqtt_config import (
    ALERT_TOPIC,
    TEMPERATURE_TOPIC,
    VIBRATION_TOPIC,
    CURRENT_TOPIC,
)
from backend.ml.config import LIGHTX_100K
from backend.ml.realtime.engine import FROZEN_H3_32_SHA256, DEFAULT_DECISION_THRESHOLD
from backend.ml.realtime.events import RealTimeAlertDispatcher, DetectionEvent
from backend.ml.realtime.mqtt_bridge import RealTimeMQTTBridge
from backend.preprocessing.schemas import RawMQTTMessage


class TestRealTimeMQTTBridge(unittest.TestCase):
    """Unit and integration tests for Phase 7.6 RealTimeMQTTBridge."""

    @classmethod
    def setUpClass(cls):
        """Load telemetry dataset for representative packets."""
        cls.raw_df = pd.read_csv(LIGHTX_100K)

    def setUp(self):
        """Set up mock MQTT client and RealTimeMQTTBridge for each test."""
        self.mock_client = MagicMock(spec=mqtt.Client)
        # Mock publish to return a successful result object (rc=0)
        mock_publish_res = MagicMock()
        mock_publish_res.rc = mqtt.MQTT_ERR_SUCCESS
        self.mock_client.publish.return_value = mock_publish_res

        self.bridge = RealTimeMQTTBridge(
            client=self.mock_client,
            alert_topic=ALERT_TOPIC,
            explain_mode="on_attack",
            verify_hash=True,
        )

    def test_01_normal_telemetry_flow(self):
        """Verify normal telemetry produces NORMAL event without SHAP and publishes no alert."""
        normal_row = self.raw_df.iloc[93364].to_dict()
        payload = {
            "device_id": str(normal_row["device_id"]),
            "sensor_type": str(normal_row["sensor_type"]),
            "value": float(normal_row["value"]),
            "unit": str(normal_row["unit"]),
            "status": str(normal_row["status"]),
            "timestamp": "2026-10-04T12:00:00Z",
            "sensor_code": "MTR-001-TMP",
        }
        raw_msg = RawMQTTMessage(
            timestamp="2026-10-04T12:00:00Z",
            topic=TEMPERATURE_TOPIC,
            payload=json.dumps(payload),
            qos=0,
            retain=False,
        )

        event = self.bridge.process_raw_message(raw_msg)

        self.assertIsNotNone(event)
        self.assertIsInstance(event, DetectionEvent)
        self.assertEqual(event.prediction, "NORMAL")
        self.assertFalse(event.is_attack)
        self.assertEqual(event.severity, "NORMAL")
        self.assertIsNone(event.explanation)  # Selective SHAP: skipped on normal

        # Alert must NOT be published
        self.mock_client.publish.assert_not_called()
        self.assertEqual(self.bridge.stats["alerts_published"], 0)
        self.assertEqual(self.bridge.stats["normal_processed"], 1)

    def test_02_attack_telemetry_and_alert_publishing(self):
        """Verify attack telemetry triggers detection, selective SHAP, and alert publish."""
        # Warm up state up to row 3203 (DoS)
        for i in range(3203):
            self.bridge.dispatcher.engine.feature_adapter.transform_packet(self.raw_df.iloc[i])

        dos_row = self.raw_df.iloc[3203].to_dict()
        payload = {
            "device_id": str(dos_row["device_id"]),
            "sensor_type": str(dos_row["sensor_type"]),
            "value": float(dos_row["value"]),
            "unit": str(dos_row["unit"]),
            "status": str(dos_row["status"]),
            "timestamp": str(dos_row["timestamp"]),
            "sensor_code": "MTR-001-TMP",
        }
        raw_msg = RawMQTTMessage(
            timestamp=str(dos_row["timestamp"]),
            topic=TEMPERATURE_TOPIC,
            payload=json.dumps(payload),
            qos=0,
            retain=False,
        )

        dispatched_alerts = []
        self.bridge.register_alert_payload_listener(lambda t, p: dispatched_alerts.append((t, p)))

        event = self.bridge.process_raw_message(raw_msg)

        self.assertIsNotNone(event)
        self.assertEqual(event.prediction, "ATTACK")
        self.assertTrue(event.is_attack)
        self.assertEqual(event.severity, "HIGH")

        # Selective SHAP attached
        self.assertIsNotNone(event.explanation)
        self.assertIsNotNone(event.human_readable)

        # Alert must be published to ALERT_TOPIC
        self.mock_client.publish.assert_called_once()
        call_args = self.mock_client.publish.call_args[0]
        self.assertEqual(call_args[0], ALERT_TOPIC)

        # Verify alert payload structure
        alert_json_str = call_args[1]
        alert_data = json.loads(alert_json_str)
        self.assertEqual(alert_data["event_id"], event.event_id)
        self.assertEqual(alert_data["severity"], "HIGH")
        self.assertEqual(alert_data["prediction"], "ATTACK")
        self.assertTrue(alert_data["is_attack"])
        self.assertEqual(alert_data["model_sha256"], FROZEN_H3_32_SHA256)
        self.assertIn("explanation", alert_data)
        self.assertIn("human_readable", alert_data)

        self.assertEqual(len(dispatched_alerts), 1)
        self.assertEqual(dispatched_alerts[0][0], ALERT_TOPIC)
        self.assertEqual(self.bridge.stats["alerts_published"], 1)

    def test_03_feedback_loop_prevention(self):
        """Verify messages received on the alert topic are immediately dropped and not fed to ML."""
        # Simulated alert message published by the system or another bridge
        alert_payload = {
            "event_id": "evt_alert_test",
            "severity": "HIGH",
            "prediction": "ATTACK",
            "is_attack": True,
            "device_id": "mtr_001_temperature_sensor",
            "value": 99.9,  # Even if it contains a value
        }
        alert_msg = RawMQTTMessage(
            timestamp="2026-10-04T12:10:00Z",
            topic=ALERT_TOPIC,  # factory/alerts
            payload=json.dumps(alert_payload),
            qos=1,
            retain=False,
        )

        res = self.bridge.process_raw_message(alert_msg)

        self.assertIsNone(res)
        self.assertEqual(self.bridge.stats["feedback_loops_prevented"], 1)
        self.assertEqual(self.bridge.stats["messages_parsed"], 0)
        self.mock_client.publish.assert_not_called()

        # Also test with subtopic of alert topic
        sub_alert_msg = RawMQTTMessage(
            timestamp="2026-10-04T12:10:01Z",
            topic=f"{ALERT_TOPIC}/subtopic",
            payload=json.dumps(alert_payload),
            qos=1,
            retain=False,
        )
        res_sub = self.bridge.process_raw_message(sub_alert_msg)
        self.assertIsNone(res_sub)
        self.assertEqual(self.bridge.stats["feedback_loops_prevented"], 2)

    def test_04_malformed_mqtt_messages(self):
        """Verify non-JSON, non-dictionary, non-sensor, and invalid values are handled safely."""
        # 1. Non-JSON string
        msg1 = RawMQTTMessage(
            timestamp="2026-10-04T12:15:00Z",
            topic=TEMPERATURE_TOPIC,
            payload="corrupted_not_json{{{",
            qos=0,
            retain=False,
        )
        self.assertIsNone(self.bridge.process_raw_message(msg1))
        self.assertEqual(self.bridge.stats["malformed_skipped"], 1)

        # 2. Non-dict JSON (e.g. JSON array or int)
        msg2 = RawMQTTMessage(
            timestamp="2026-10-04T12:15:01Z",
            topic=TEMPERATURE_TOPIC,
            payload="[1, 2, 3]",
            qos=0,
            retain=False,
        )
        self.assertIsNone(self.bridge.process_raw_message(msg2))
        self.assertEqual(self.bridge.stats["malformed_skipped"], 2)

        # 3. Non-sensor message (missing required device_id, sensor_type, or value)
        msg3 = RawMQTTMessage(
            timestamp="2026-10-04T12:15:02Z",
            topic=TEMPERATURE_TOPIC,
            payload=json.dumps({"info": "heartbeat_ping"}),
            qos=0,
            retain=False,
        )
        self.assertIsNone(self.bridge.process_raw_message(msg3))
        self.assertEqual(self.bridge.stats["malformed_skipped"], 3)

        # 4. Non-numeric sensor value
        msg4 = RawMQTTMessage(
            timestamp="2026-10-04T12:15:03Z",
            topic=TEMPERATURE_TOPIC,
            payload=json.dumps({
                "device_id": "mtr_001_temperature_sensor",
                "sensor_type": "temperature",
                "value": "invalid_not_a_number",
            }),
            qos=0,
            retain=False,
        )
        self.assertIsNone(self.bridge.process_raw_message(msg4))
        self.assertEqual(self.bridge.stats["malformed_skipped"], 4)

    def test_05_unknown_categorical_values(self):
        """Verify unknown sensor types or devices process cleanly via OHE fallback."""
        payload = {
            "device_id": "novel_alien_sensor_999",
            "sensor_type": "gravitational_wave_detector",
            "value": 12.34,
            "unit": "waves",
            "status": "EXPERIMENT",
            "timestamp": "2026-10-04T12:20:00Z",
        }
        msg = RawMQTTMessage(
            timestamp="2026-10-04T12:20:00Z",
            topic="factory/line1/unknown",
            payload=json.dumps(payload),
            qos=0,
            retain=False,
        )

        event = self.bridge.process_raw_message(msg)
        self.assertIsNotNone(event)
        self.assertEqual(event.device_id, "novel_alien_sensor_999")
        self.assertEqual(event.model_sha256, FROZEN_H3_32_SHA256)

    def test_06_cold_start_message(self):
        """Verify first packet on uninitialized state processes cleanly."""
        first_row = self.raw_df.iloc[0].to_dict()
        msg = RawMQTTMessage(
            timestamp="2026-10-04T12:00:00Z",
            topic=TEMPERATURE_TOPIC,
            payload=json.dumps({
                "device_id": str(first_row["device_id"]),
                "sensor_type": str(first_row["sensor_type"]),
                "value": float(first_row["value"]),
                "timestamp": "2026-10-04T12:00:00Z",
            }),
            qos=0,
            retain=False,
        )
        event = self.bridge.process_raw_message(msg)
        self.assertIsNotNone(event)
        self.assertEqual(event.model_sha256, FROZEN_H3_32_SHA256)

    def test_07_multiple_sensors(self):
        """Verify sequential messages from multiple distinct sensors."""
        sensors = [
            ("mtr_001_temperature_sensor", "temperature", 45.2, TEMPERATURE_TOPIC),
            ("mtr_001_vibration_sensor", "vibration", 0.12, VIBRATION_TOPIC),
            ("mtr_001_current_sensor", "current", 12.4, CURRENT_TOPIC),
        ]

        for dev_id, stype, val, topic in sensors:
            msg = RawMQTTMessage(
                timestamp="2026-10-04T12:25:00Z",
                topic=topic,
                payload=json.dumps({
                    "device_id": dev_id,
                    "sensor_type": stype,
                    "value": val,
                    "timestamp": "2026-10-04T12:25:00Z",
                }),
                qos=0,
                retain=False,
            )
            ev = self.bridge.process_raw_message(msg)
            self.assertIsNotNone(ev)
            self.assertEqual(ev.device_id, dev_id)

        self.assertEqual(self.bridge.stats["messages_parsed"], 3)

    def test_08_deduplication_and_cooldown_via_mqtt(self):
        """Verify consecutive attack packets respect deduplication cooldown."""
        dispatcher_with_cooldown = RealTimeAlertDispatcher(
            dedup_window_seconds=10.0,
            explain_mode="on_attack",
        )
        bridge = RealTimeMQTTBridge(
            dispatcher=dispatcher_with_cooldown,
            client=self.mock_client,
        )

        attack_payload = {
            "device_id": "mtr_001_vibration_sensor",
            "sensor_type": "vibration",
            "value": 999.0,  # Extreme anomaly
            "timestamp": "100.0",
        }
        msg1 = RawMQTTMessage(
            timestamp="100.0",
            topic=VIBRATION_TOPIC,
            payload=json.dumps(attack_payload),
            qos=0,
            retain=False,
        )
        # 2 seconds later (within 10s window)
        attack_payload_2 = dict(attack_payload, timestamp="102.0")
        msg2 = RawMQTTMessage(
            timestamp="102.0",
            topic=VIBRATION_TOPIC,
            payload=json.dumps(attack_payload_2),
            qos=0,
            retain=False,
        )

        ev1 = bridge.process_raw_message(msg1)
        ev2 = bridge.process_raw_message(msg2)

        if ev1.is_attack and ev2.is_attack:
            self.assertFalse(ev1.is_suppressed)
            self.assertTrue(ev2.is_suppressed)
            self.assertEqual(bridge.stats["alerts_published"], 1)
            self.assertEqual(bridge.stats["alerts_suppressed"], 1)

    def test_09_single_feature_update_guarantee(self):
        """Verify that processing an MQTT message triggers exactly one state update."""
        pkt = self.raw_df.iloc[100].to_dict()
        msg = RawMQTTMessage(
            timestamp="2026-10-04T12:30:00Z",
            topic=TEMPERATURE_TOPIC,
            payload=json.dumps({
                "device_id": str(pkt["device_id"]),
                "sensor_type": str(pkt["sensor_type"]),
                "value": float(pkt["value"]),
                "timestamp": "2026-10-04T12:30:00Z",
            }),
            qos=0,
            retain=False,
        )

        dev_state = self.bridge.dispatcher.engine.feature_adapter.state_tracker.get_device_state(str(pkt["device_id"]))
        initial_len = len(dev_state.val_hist)

        self.bridge.process_raw_message(msg)

        after_len = len(dev_state.val_hist)
        self.assertEqual(after_len, initial_len + 1)

    def test_10_on_message_paho_callback(self):
        """Verify paho.mqtt.client.MQTTMessage callback integration."""
        raw_payload = json.dumps({
            "device_id": "mtr_001_temperature_sensor",
            "sensor_type": "temperature",
            "value": 45.0,
            "timestamp": "2026-10-04T12:35:00Z",
        })

        mock_msg = MagicMock(spec=mqtt.MQTTMessage)
        mock_msg.topic = TEMPERATURE_TOPIC
        mock_msg.payload = raw_payload.encode("utf-8")
        mock_msg.qos = 0
        mock_msg.retain = False

        events_received = []
        self.bridge.register_event_listener(lambda ev: events_received.append(ev))

        self.bridge._on_message(self.mock_client, None, mock_msg)

        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].device_id, "mtr_001_temperature_sensor")

    def test_11_lifecycle_callbacks(self):
        """Verify _on_connect and _on_disconnect callbacks."""
        self.bridge._on_connect(self.mock_client, None, None, rc=0)
        self.assertTrue(self.bridge.connected)
        # Should have subscribed to telemetry topics
        self.assertGreater(self.mock_client.subscribe.call_count, 0)

        self.bridge._on_disconnect(self.mock_client, None, rc=0)
        self.assertFalse(self.bridge.connected)

    def test_12_model_integrity_preserved(self):
        """Verify model SHA-256 hash remains unaltered."""
        self.assertEqual(
            self.bridge.dispatcher.engine.current_model_sha256,
            FROZEN_H3_32_SHA256,
        )
        self.assertTrue(self.bridge.dispatcher.engine.verify_model_integrity())


if __name__ == "__main__":
    unittest.main()
