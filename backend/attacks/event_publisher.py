"""
Publishes attack state events over MQTT.
"""

from datetime import datetime
from typing import Any

from backend.industrial.mqtt.publisher import MQTTPublisher
from backend.industrial.config.mqtt_config import ATTACK_STATE_TOPIC


class AttackEventPublisher:
    """Publishes attack start/stop events."""

    def __init__(self):
        self.publisher = MQTTPublisher(
            "attack_event_publisher"
        )

    def publish_start(
        self,
        attack_status: dict[str, Any],
    ) -> None:

        payload = {
            "event": "start",
            "timestamp": datetime.now().isoformat(),
            **attack_status,
        }

        self.publisher.publish(
            ATTACK_STATE_TOPIC,
            payload,
        )

    def publish_stop(
        self,
        attack_status: dict[str, Any],
    ) -> None:

        payload = {
            "event": "stop",
            "timestamp": datetime.now().isoformat(),
            **attack_status,
        }

        self.publisher.publish(
            ATTACK_STATE_TOPIC,
            payload,
        )

    def disconnect(self):
        self.publisher.disconnect()