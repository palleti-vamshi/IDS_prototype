"""
MQTT Traffic Collector for LightX-IDS.
"""

from datetime import datetime
import logging
from typing import Callable

import paho.mqtt.client as mqtt

from backend.industrial.config.mqtt_config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_KEEPALIVE,
    MQTT_TOPICS,
    COLLECTOR_CLIENT,
)

from backend.preprocessing.schemas import RawMQTTMessage

logger = logging.getLogger(__name__)


class MQTTCollector:
    """Collects MQTT traffic and forwards raw messages."""

    def __init__(self, message_callback: Callable[[RawMQTTMessage], None]):
        self.message_callback = message_callback

        self.client = mqtt.Client(client_id=COLLECTOR_CLIENT)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self) -> None:
        """Connect to MQTT broker."""
        print("🔄 Connecting to MQTT Broker...")

        self.client.connect(
            MQTT_BROKER,
            MQTT_PORT,
            MQTT_KEEPALIVE,
        )

    def start(self) -> None:
        """Start listening."""
        print("🚀 Starting MQTT Collector...")
        self.client.loop_forever()

    def stop(self) -> None:
        """Disconnect from broker."""
        print("🛑 Collector Stopped")
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, rc):
        print(f"✅ Connected Callback Received | RC = {rc}")

        if rc == 0:
            print("✅ Connected Successfully!")

            for topic in MQTT_TOPICS:
                client.subscribe(topic)
                print(f"📡 Subscribed -> {topic}")

        else:
            print(f"❌ Connection Failed | RC={rc}")

    def _on_message(self, client, userdata, msg):
        print(f"📩 Message Received -> {msg.topic}")

        raw_message = RawMQTTMessage(
            timestamp=datetime.now().isoformat(),
            topic=msg.topic,
            payload=msg.payload.decode(),
            qos=msg.qos,
            retain=msg.retain,
        )

        self.message_callback(raw_message)