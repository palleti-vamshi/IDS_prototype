"""
MQTT Publisher Module

Purpose:
    Provides a reusable MQTT publisher for the LightX-IDS platform.
"""

import json
from typing import Any

import paho.mqtt.client as mqtt

from backend.core.logger import setup_logger
from backend.industrial.config.mqtt_config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_KEEPALIVE,
)

logger = setup_logger("MQTT Publisher")


class MQTTPublisher:
    """Reusable MQTT Publisher."""

    def __init__(self, client_id: str):
        self.client = mqtt.Client(client_id=client_id)
        self.connected = False

        try:
            self.client.connect(
                MQTT_BROKER,
                MQTT_PORT,
                MQTT_KEEPALIVE,
            )

            # Maintain a persistent MQTT connection
            self.client.loop_start()
            self.connected = True

            logger.info("Connected to MQTT Broker.")

        except Exception as error:
            logger.exception(
                f"Failed to connect to MQTT Broker: {error}"
            )
            raise

    def publish(self, topic: str, message: Any) -> bool:
        """
        Publish a message to an MQTT topic.

        Accepts either:
        - Python dictionary
        - JSON string
        """

        if not self.connected:
            logger.error("MQTT Publisher is not connected.")
            return False

        try:

            # If already JSON string, send directly.
            if isinstance(message, str):
                payload = message

            # Otherwise serialize dictionary/object.
            else:
                payload = json.dumps(message)

            result = self.client.publish(topic, payload)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published message to '{topic}'")
                return True

            logger.error(
                f"Publish failed with code: {result.rc}"
            )
            return False

        except Exception as error:
            logger.exception(
                f"Publishing failed: {error}"
            )
            return False

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""

        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()

            self.connected = False

            logger.info("Disconnected from MQTT Broker.")