"""
MQTT Publisher Module

Purpose:
    Provides a reusable MQTT publisher for the LightX-IDS platform.
"""

import json
import random
from typing import Any

import paho.mqtt.client as mqtt

from backend.attacks.network.network_state import (
    NetworkState,
)
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

        self.client = mqtt.Client(
            client_id=client_id
        )

        self.connected = False

        try:

            self.client.connect(
                MQTT_BROKER,
                MQTT_PORT,
                MQTT_KEEPALIVE,
            )

            self.client.loop_start()

            self.connected = True

            logger.info(
                "Connected to MQTT Broker."
            )

        except Exception as error:

            logger.exception(
                f"Failed to connect to MQTT Broker: {error}"
            )

            raise

    # ==================================================
    # Publish
    # ==================================================

    def publish(
        self,
        topic: str,
        message: Any,
    ) -> bool:
        """
        Publish a message to an MQTT topic.

        Supports:
        - Normal publishing
        - Packet loss
        - Simulated network delay (non-blocking)
        """

        if not self.connected:

            logger.error(
                "MQTT Publisher is not connected."
            )

            return False

        try:

            # ------------------------------------------
            # Serialize Payload
            # ------------------------------------------

            if isinstance(message, str):

                payload = message

            else:

                payload = json.dumps(
                    message
                )

            # ------------------------------------------
            # Simulated Network Delay
            # (Don't block the simulator)
            # ------------------------------------------

            if NetworkState.delay > 0:

                logger.debug(
                    "Simulated network delay: %.2f sec",
                    NetworkState.delay,
                )

            # ------------------------------------------
            # Packet Loss
            # ------------------------------------------

            if (
                NetworkState.packet_loss > 0
                and random.uniform(0, 100)
                < NetworkState.packet_loss
            ):

                logger.warning(
                    "Packet dropped due to active DoS attack."
                )

                return False

            # ------------------------------------------
            # Publish
            # ------------------------------------------

            result = self.client.publish(
                topic,
                payload,
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:

                logger.info(
                    "Published message to '%s'",
                    topic,
                )

                return True

            logger.error(
                "Publish failed | Topic=%s | Client=%s | RC=%s",
                topic,
                self.client._client_id.decode(),
                result.rc,
            )

            return False

        except Exception as error:

            logger.exception(
                f"Publishing failed: {error}"
            )

            return False

    # ==================================================
    # Disconnect
    # ==================================================

    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""

        if self.connected:

            self.client.loop_stop()

            self.client.disconnect()

            self.connected = False

            logger.info(
                "Disconnected from MQTT Broker."
            )