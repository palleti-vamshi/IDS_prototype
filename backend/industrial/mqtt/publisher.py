"""
MQTT Publisher Module

Purpose:
    Provides a reusable MQTT publisher for the LightX-IDS platform.
"""

from __future__ import annotations

import json
import random
from typing import Any

import paho.mqtt.client as mqtt

from backend.attacks.network.network_state import (
    NetworkState,
)
from backend.core.logger import setup_logger
from backend.industrial.communication.communication_controller import (
    CommunicationController,
)
from backend.industrial.communication.packet_buffer import (
    PacketBuffer,
)
from backend.industrial.communication.packet_queue import (
    PacketQueue,
)
from backend.industrial.communication.traffic_statistics import (
    TrafficStatistics,
)
from backend.industrial.config.mqtt_config import (
    MQTT_BROKER,
    MQTT_KEEPALIVE,
    MQTT_PORT,
)

logger = setup_logger("MQTT Publisher")


class MQTTPublisher:
    """Reusable MQTT Publisher."""

    def __init__(
        self,
        client_id: str,
        communication: CommunicationController | None = None,
    ):

        self.client = mqtt.Client(
            client_id=client_id
        )

        self.connected = False

        # ==========================================
        # Shared Communication Engine
        # ==========================================

        if communication is None:

            self.communication = CommunicationController()

            self.packet_buffer = PacketBuffer()

            self.packet_queue = PacketQueue()

            self.statistics = TrafficStatistics()

            self.communication.set_packet_buffer(
                self.packet_buffer
            )

            self.communication.set_packet_queue(
                self.packet_queue
            )

            self.communication.set_statistics(
                self.statistics
            )

        else:

            self.communication = communication

            self.packet_buffer = (
                communication.packet_buffer
            )

            self.packet_queue = (
                communication.packet_queue
            )

            self.statistics = (
                communication.statistics
            )

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

        if not self.connected:

            logger.error(
                "MQTT Publisher is not connected."
            )

            return False

        try:

            if isinstance(
                message,
                str,
            ):

                payload = message

            else:

                payload = json.dumps(
                    message
                )

            # Store packet

            self.packet_buffer.add_packet(
                topic,
                message,
            )

            # Queue packet

            self.packet_queue.enqueue(
                (
                    topic,
                    payload,
                )
            )

            packet = self.packet_queue.dequeue()

            if packet is None:

                return False

            topic, payload = packet

            # Delay statistics

            if NetworkState.delay > 0:

                self.statistics.packet_delayed()

            # Packet loss

            if (
                NetworkState.packet_loss > 0
                and random.uniform(
                    0,
                    100,
                )
                < NetworkState.packet_loss
            ):

                self.statistics.packet_dropped()

                logger.warning(
                    "Packet dropped."
                )

                return False

            result = self.client.publish(
                topic,
                payload,
            )

            if (
                result.rc
                == mqtt.MQTT_ERR_SUCCESS
            ):

                self.statistics.packet_sent()

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
    # Statistics
    # ==================================================

    def get_statistics(
        self,
    ) -> dict:

        return self.statistics.get_status()

    # ==================================================
    # Disconnect
    # ==================================================

    def disconnect(
        self,
    ) -> None:

        if self.connected:

            self.client.loop_stop()

            self.client.disconnect()

            self.connected = False

            logger.info(
                "Disconnected from MQTT Broker."
            )