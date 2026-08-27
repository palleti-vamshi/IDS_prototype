"""
MQTT Publisher Module

Purpose:
    Provides a reusable MQTT publisher for the LightX-IDS platform.

Phase 3 compatibility:
    • Supports industrial sensor publishing
    • Supports attack-state event publishing
    • Preserves network attack effects
    • Provides safe MQTT lifecycle handling
    • Remains backward compatible with existing callers
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
    """
    Reusable MQTT Publisher.

    Responsible for:

        1. Connecting to the MQTT broker
        2. Publishing MQTT messages
        3. Recording communication statistics
        4. Applying simulated network effects
        5. Managing MQTT lifecycle
    """

    def __init__(
        self,
        client_id: str,
        communication: CommunicationController | None = None,
    ) -> None:

        self.client_id = client_id

        self.client = mqtt.Client(
            client_id=client_id
        )

        self.connected = False

        # ==================================================
        # Shared Communication Engine
        # ==================================================

        if communication is None:

            self.communication = (
                CommunicationController()
            )

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

        # ==================================================
        # MQTT Connection
        # ==================================================

        self._connect()

    # ==================================================
    # Connection
    # ==================================================

    def _connect(self) -> None:
        """
        Connect to the MQTT broker.

        Connection is isolated from __init__ so the
        lifecycle is easier to manage and test.
        """

        try:

            self.client.connect(
                MQTT_BROKER,
                MQTT_PORT,
                MQTT_KEEPALIVE,
            )

            self.client.loop_start()

            self.connected = True

            logger.info(
                "MQTT Publisher connected | Client=%s",
                self.client_id,
            )

        except Exception as error:

            self.connected = False

            logger.exception(
                "Failed to connect MQTT Publisher | "
                "Client=%s | Error=%s",
                self.client_id,
                error,
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

        Returns:
            True  -> message successfully accepted by MQTT
            False -> publish failed or packet was simulated
                     as dropped
        """

        if not self.connected:

            logger.error(
                "MQTT Publisher is not connected | "
                "Client=%s",
                self.client_id,
            )

            return False

        if not topic:

            logger.error(
                "Cannot publish message with empty topic."
            )

            return False

        try:

            # ==================================================
            # Serialize Payload
            # ==================================================

            if isinstance(
                message,
                str,
            ):

                payload = message

            else:

                payload = json.dumps(
                    message
                )

            # ==================================================
            # Store Packet
            # ==================================================

            self.packet_buffer.add_packet(
                topic,
                message,
            )

            # ==================================================
            # Queue Packet
            # ==================================================

            self.packet_queue.enqueue(
                (
                    topic,
                    payload,
                )
            )

            packet = self.packet_queue.dequeue()

            if packet is None:

                logger.warning(
                    "Packet queue returned no packet."
                )

                return False

            topic, payload = packet

            # ==================================================
            # Simulated Network Delay
            # ==================================================

            if NetworkState.delay > 0:

                self.statistics.packet_delayed()

            # ==================================================
            # Simulated Packet Loss
            # ==================================================

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
                    "Packet dropped by simulated "
                    "network conditions | Topic=%s",
                    topic,
                )

                return False

            # ==================================================
            # MQTT Publish
            # ==================================================

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
                    "Published MQTT message | "
                    "Topic=%s | Client=%s",
                    topic,
                    self.client_id,
                )

                return True

            logger.error(
                "MQTT publish failed | "
                "Topic=%s | Client=%s | RC=%s",
                topic,
                self.client_id,
                result.rc,
            )

            return False

        except Exception as error:

            logger.exception(
                "MQTT publishing failed | "
                "Topic=%s | Client=%s | Error=%s",
                topic,
                self.client_id,
                error,
            )

            return False

    # ==================================================
    # Statistics
    # ==================================================

    def get_statistics(
        self,
    ) -> dict:
        """
        Return communication statistics.
        """

        return self.statistics.get_status()

    # ==================================================
    # Connection Status
    # ==================================================

    def is_connected(self) -> bool:
        """
        Return whether this publisher is currently connected.
        """

        return self.connected

    # ==================================================
    # Disconnect
    # ==================================================

    def disconnect(
        self,
    ) -> None:
        """
        Safely disconnect from the MQTT broker.
        """

        if not self.connected:

            return

        try:

            self.client.loop_stop()

            self.client.disconnect()

        except Exception as error:

            logger.exception(
                "MQTT disconnect failed | "
                "Client=%s | Error=%s",
                self.client_id,
                error,
            )

        finally:

            self.connected = False

            logger.info(
                "MQTT Publisher disconnected | "
                "Client=%s",
                self.client_id,
            )

    # ==================================================
    # Context Manager
    # ==================================================

    def __enter__(self):
        """
        Allow:

            with MQTTPublisher(...) as publisher:
                publisher.publish(...)
        """

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        self.disconnect()

    # ==================================================
    # String
    # ==================================================

    def __str__(self) -> str:

        return (
            f"MQTTPublisher("
            f"client_id={self.client_id}, "
            f"connected={self.connected})"
        )