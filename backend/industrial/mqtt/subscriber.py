"""
MQTT Subscriber Module

Purpose:
    Provides a reusable MQTT subscriber for the LightX-IDS platform.
"""

import json
from collections.abc import Callable
from typing import Any

import paho.mqtt.client as mqtt

from backend.core.logger import setup_logger
from backend.industrial.config.mqtt_config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_KEEPALIVE,
)

logger = setup_logger("MQTT Subscriber")


class MQTTSubscriber:
    """Reusable MQTT Subscriber."""

    def __init__(
        self,
        client_id: str,
        message_handler: Callable[[str, dict[str, Any]], None] | None = None,
    ):
        self.client = mqtt.Client(client_id=client_id)
        self.connected = False
        self.message_handler = message_handler

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        try:
            self.client.connect(
                MQTT_BROKER,
                MQTT_PORT,
                MQTT_KEEPALIVE,
            )

            self.client.loop_start()
            self.connected = True

            logger.info("Connected to MQTT Broker.")

        except Exception as error:
            logger.exception(f"Failed to connect to MQTT Broker: {error}")
            raise

    def subscribe(self, topic: str) -> None:
        """Subscribe to an MQTT topic."""

        if not self.connected:
            logger.error("MQTT Subscriber is not connected.")
            return

        self.client.subscribe(topic)
        logger.info(f"Subscribed to '{topic}'")

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        logger.info("MQTT connection established.")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())

            logger.info(f"Message received from '{msg.topic}'")

            if self.message_handler:
                self.message_handler(msg.topic, payload)

        except Exception as error:
            logger.exception(f"Failed to process incoming message: {error}")

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""

        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()

            self.connected = False

            logger.info("Disconnected from MQTT Broker.")