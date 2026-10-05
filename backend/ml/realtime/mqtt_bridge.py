"""
Real-Time MQTT Bridge for LightX-IDS (Phase 7.6)

Connects the industrial MQTT telemetry stream to the real-time intrusion detection pipeline:
1. Subscribes to industrial sensor telemetry topics (e.g., factory/line1/+).
2. Parses raw messages through the existing MessageParser.
3. Passes valid ParsedSensorRecord objects into RealTimeAlertDispatcher (Phase 7.5).
4. Selectively generates TreeSHAP explanations on detected attacks.
5. Publishes structured security alerts to factory/alerts.
6. Enforces feedback-loop protection: alert topics are never ingested as telemetry.

Architectural Guarantees:
- Decoupled Transport: DetectionEvent remains independent of MQTT.
- Strict Reuse: Reuses existing MessageParser, schemas, and frozen Phase 5 H3-32 pipeline.
- Single Feature Update: Guarantees exactly one feature-adapter state update per telemetry packet.
- Loop Prevention: Inbound messages on the alert topic are immediately dropped.
- Isolated Testing: Supports simulated/mock message processing without requiring live broker.
"""

from datetime import datetime
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union

import paho.mqtt.client as mqtt

from backend.industrial.config.mqtt_config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_KEEPALIVE,
    ALERT_TOPIC,
    MQTT_TOPICS,
)
from backend.ml.realtime.events import (
    DetectionEvent,
    RealTimeAlertDispatcher,
    _to_serializable,
)
from backend.preprocessing.parser import MessageParser
from backend.preprocessing.schemas import RawMQTTMessage, ParsedSensorRecord

logger = logging.getLogger(__name__)

DEFAULT_BRIDGE_CLIENT_ID = "lightx_ids_realtime_bridge"


class RealTimeMQTTBridge:
    """
    Real-Time MQTT Bridge connecting industrial telemetry to the LightX-IDS pipeline.
    """

    def __init__(
        self,
        dispatcher: Optional[RealTimeAlertDispatcher] = None,
        client: Optional[mqtt.Client] = None,
        alert_topic: str = ALERT_TOPIC,
        telemetry_topics: Optional[List[str]] = None,
        broker: str = MQTT_BROKER,
        port: int = MQTT_PORT,
        keepalive: int = MQTT_KEEPALIVE,
        client_id: str = DEFAULT_BRIDGE_CLIENT_ID,
        publish_alerts: bool = True,
        explain_mode: str = "on_attack",
        verify_hash: bool = True,
    ) -> None:
        """
        Initialize the RealTimeMQTTBridge.

        Args:
            dispatcher: Optional pre-configured RealTimeAlertDispatcher instance.
            client: Optional pre-configured or mock paho.mqtt.client.Client instance.
            alert_topic: Destination topic for security alerts (default 'factory/alerts').
            telemetry_topics: List of topics to subscribe to. If None, subscribes to
                              all sensor topics excluding alert_topic.
            broker: MQTT broker hostname or IP.
            port: MQTT broker port.
            keepalive: MQTT keepalive interval in seconds.
            client_id: MQTT client identifier.
            publish_alerts: Whether to publish detected attack events to alert_topic.
            explain_mode: SHAP explanation policy ('on_attack', 'always', 'never', 'on_demand').
            verify_hash: Verify frozen model SHA-256 on initialization.
        """
        if dispatcher is not None:
            self.dispatcher = dispatcher
        else:
            self.dispatcher = RealTimeAlertDispatcher(
                explain_mode=explain_mode,
                verify_hash=verify_hash,
            )

        self.alert_topic = str(alert_topic).strip()
        self.broker = str(broker)
        self.port = int(port)
        self.keepalive = int(keepalive)
        self.client_id = str(client_id)
        self.publish_alerts = bool(publish_alerts)

        # Configure telemetry subscription topics (exclude alert topic to prevent loops)
        if telemetry_topics is not None:
            self.telemetry_topics = [t for t in telemetry_topics if t != self.alert_topic]
        else:
            # Default to standard factory topics excluding alert topic
            self.telemetry_topics = [t for t in MQTT_TOPICS if t != self.alert_topic]

        # MQTT Client initialization
        if client is not None:
            self.client = client
        else:
            self.client = mqtt.Client(client_id=self.client_id)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self.connected = False
        self._loop_started = False

        # Operational metrics
        self.stats = {
            "messages_received": 0,
            "messages_parsed": 0,
            "malformed_skipped": 0,
            "feedback_loops_prevented": 0,
            "attacks_detected": 0,
            "alerts_published": 0,
            "alerts_suppressed": 0,
            "normal_processed": 0,
        }

        # Optional listener callbacks for testing / monitoring: (event: DetectionEvent) -> None
        self._event_listeners: List[Callable[[DetectionEvent], None]] = []
        self._alert_payload_listeners: List[Callable[[str, Dict[str, Any]], None]] = []

    def register_event_listener(self, listener: Callable[[DetectionEvent], None]) -> None:
        """Register a callback invoked whenever a DetectionEvent is generated."""
        self._event_listeners.append(listener)

    def register_alert_payload_listener(self, listener: Callable[[str, Dict[str, Any]], None]) -> None:
        """Register a callback invoked when an alert payload is dispatched: listener(topic, payload)."""
        self._alert_payload_listeners.append(listener)

    def connect(self) -> None:
        """Connect the MQTT client to the configured broker."""
        logger.info("Connecting RealTimeMQTTBridge to broker %s:%d...", self.broker, self.port)
        try:
            self.client.connect(self.broker, self.port, self.keepalive)
            self.connected = True
        except Exception as e:
            self.connected = False
            logger.error("Failed to connect RealTimeMQTTBridge: %s", e)
            raise

    def start(self, background: bool = True) -> None:
        """
        Start processing MQTT messages.

        Args:
            background: If True, starts client.loop_start() non-blocking thread.
                        If False, calls client.loop_forever() blocking call.
        """
        if not self.connected:
            self.connect()

        if background:
            self.client.loop_start()
            self._loop_started = True
            logger.info("RealTimeMQTTBridge background loop started.")
        else:
            logger.info("RealTimeMQTTBridge entering blocking loop_forever.")
            self.client.loop_forever()

    def stop(self) -> None:
        """Disconnect and stop the MQTT client."""
        logger.info("Stopping RealTimeMQTTBridge...")
        if self._loop_started:
            self.client.loop_stop()
            self._loop_started = False
        if self.connected:
            try:
                self.client.disconnect()
            except Exception:
                pass
            self.connected = False
        logger.info("RealTimeMQTTBridge stopped.")

    def reset_state(self) -> None:
        """Reset internal feature adapter state and counters."""
        self.dispatcher.reset()
        for k in self.stats:
            self.stats[k] = 0

    def format_alert_payload(self, event: DetectionEvent) -> Dict[str, Any]:
        """
        Format a DetectionEvent into a structured JSON dictionary for MQTT publishing.
        Omits bulky raw arrays; retains top-K SHAP contributors and operator narrative.
        """
        payload = {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "severity": event.severity,
            "prediction": event.prediction,
            "is_attack": event.is_attack,
            "attack_probability": round(float(event.attack_probability), 4),
            "normal_probability": round(float(event.normal_probability), 4),
            "decision_threshold": float(event.decision_threshold),
            "device_id": event.device_id,
            "sensor_code": event.sensor_code,
            "sensor_type": event.sensor_type,
            "telemetry_topic": event.topic,
            "record_id": event.record_id,
            "model_id": event.model_id,
            "model_version": event.model_version,
            "model_sha256": event.model_sha256,
            "explanation": event.explanation,
            "human_readable": event.human_readable,
        }
        return _to_serializable(payload)

    def publish_alert(self, event: DetectionEvent) -> bool:
        """
        Publish a structured detection alert to the alert topic.
        """
        if not self.publish_alerts or not event.is_attack:
            return False

        if event.is_suppressed:
            self.stats["alerts_suppressed"] += 1
            return False

        alert_dict = self.format_alert_payload(event)
        alert_json = json.dumps(alert_dict)

        # Notify any in-memory test/audit listeners
        for listener in self._alert_payload_listeners:
            try:
                listener(self.alert_topic, alert_dict)
            except Exception as e:
                logger.error("Error in alert payload listener: %s", e)

        # MQTT Publish
        try:
            res = self.client.publish(self.alert_topic, alert_json, qos=1)
            self.stats["alerts_published"] += 1
            logger.info(
                "🚨 Published security alert to %s | EventID=%s | Dev=%s | Sev=%s",
                self.alert_topic,
                event.event_id,
                event.device_id,
                event.severity,
            )
            return True
        except Exception as e:
            logger.error("Failed to publish alert to %s: %s", self.alert_topic, e)
            return False

    def process_raw_message(self, raw_message: RawMQTTMessage) -> Optional[DetectionEvent]:
        """
        Core message pipeline for a single raw MQTT message:
        1. Feedback loop check (reject self.alert_topic).
        2. MessageParser validation.
        3. RealTimeAlertDispatcher processing (Inference + Event + Selective SHAP).
        4. Alert publishing if attack detected.
        5. Return DetectionEvent or None if rejected/non-sensor.

        Args:
            raw_message: RawMQTTMessage object.

        Returns:
            DetectionEvent if successfully parsed and processed, None otherwise.
        """
        self.stats["messages_received"] += 1

        # Step 1: Feedback loop prevention
        if raw_message.topic == self.alert_topic or raw_message.topic.startswith(f"{self.alert_topic}/"):
            self.stats["feedback_loops_prevented"] += 1
            logger.warning(
                "Feedback loop prevented: Dropping message received on alert topic: %s",
                raw_message.topic,
            )
            return None

        # Step 2: MessageParser validation
        parsed_record: Optional[ParsedSensorRecord] = MessageParser.parse(raw_message)
        if parsed_record is None:
            self.stats["malformed_skipped"] += 1
            logger.debug("Skipping unparseable or non-sensor message on topic: %s", raw_message.topic)
            return None

        self.stats["messages_parsed"] += 1

        # Step 3: RealTimeAlertDispatcher processing
        event: DetectionEvent = self.dispatcher.process_packet(parsed_record)

        if event.is_attack:
            self.stats["attacks_detected"] += 1
            # Step 4: Publish alert if attack
            self.publish_alert(event)
        else:
            self.stats["normal_processed"] += 1

        # Step 5: Notify in-memory listeners
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error("Error in event listener: %s", e)

        return event

    def _on_connect(self, client: mqtt.Client, userdata: Any, flags: Any, rc: int) -> None:
        """Handle MQTT connection callback and subscribe to telemetry topics."""
        if rc == 0:
            self.connected = True
            logger.info("✅ RealTimeMQTTBridge connected successfully (rc=0).")
            for topic in self.telemetry_topics:
                client.subscribe(topic, qos=0)
                logger.info("📡 Subscribed to telemetry topic -> %s", topic)
        else:
            self.connected = False
            logger.error("❌ RealTimeMQTTBridge connection failed (rc=%d).", rc)

    def _on_disconnect(self, client: mqtt.Client, userdata: Any, rc: int) -> None:
        """Handle MQTT disconnection callback."""
        self.connected = False
        if rc != 0:
            logger.warning("⚠️ RealTimeMQTTBridge unexpected disconnect (rc=%d).", rc)
        else:
            logger.info("RealTimeMQTTBridge cleanly disconnected.")

    def _on_message(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        """Handle incoming MQTT message and dispatch to processing pipeline."""
        try:
            payload_str = msg.payload.decode("utf-8", errors="replace")
            raw_msg = RawMQTTMessage(
                timestamp=datetime.now().isoformat(),
                topic=msg.topic,
                payload=payload_str,
                qos=msg.qos,
                retain=bool(msg.retain),
            )
            self.process_raw_message(raw_msg)
        except Exception as e:
            logger.error("Unexpected error in MQTT message handler: %s", e)
