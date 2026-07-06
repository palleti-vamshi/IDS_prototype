"""
Publishes attack state events over MQTT.
"""

import json
from datetime import datetime

from backend.industrial.mqtt.publisher import MQTTPublisher
from backend.industrial.config.mqtt_config import ATTACK_STATE_TOPIC


class AttackEventPublisher:
    """Publishes attack start/stop events."""

    def __init__(self):
        self.publisher = MQTTPublisher("attack_event_publisher")

    def publish_start(self, attack_name: str) -> None:
        """Publish attack start event."""

        payload = {
            "event": "start",
            "attack": attack_name,
            "timestamp": datetime.now().isoformat(),
        }

        self.publisher.publish(
            ATTACK_STATE_TOPIC,
            json.dumps(payload),
        )

    def publish_stop(self, attack_name: str) -> None:
        """Publish attack stop event."""

        payload = {
            "event": "stop",
            "attack": attack_name,
            "timestamp": datetime.now().isoformat(),
        }

        self.publisher.publish(
            ATTACK_STATE_TOPIC,
            payload,
        )