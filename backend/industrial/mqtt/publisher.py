"""
MQTT Publisher Module

Purpose:
    Provides a reusable MQTT publisher for the LightX-IDS platform.

Phase 3 compatibility:
    - Supports industrial sensor publishing
    - Supports attack-state event publishing
    - Preserves network attack effects
    - Supports replay and topic hijacking effects
    - Supports shared communication effects
    - Provides communication statistics
    - Provides safe MQTT lifecycle handling
    - Remains backward compatible with existing callers
"""

from __future__ import annotations

import json
import random
import time
from typing import Any

import paho.mqtt.client as mqtt

from backend.attacks.network.network_state import NetworkState

from backend.core.logger import setup_logger

from backend.industrial.communication.communication_controller import (
    CommunicationController,
)

from backend.industrial.communication.packet_buffer import PacketBuffer

from backend.industrial.communication.packet_queue import PacketQueue

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
        5. Managing replay and topic hijacking
        6. Managing MQTT lifecycle
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

            # --------------------------------------------------
            # Defensive initialization
            # --------------------------------------------------
            # A shared CommunicationController may have been
            # created before its components were attached.
            # Initialize them once and attach them back to the
            # shared controller.
            # --------------------------------------------------

            if communication.packet_buffer is None:

                communication.set_packet_buffer(
                    PacketBuffer()
                )

            if communication.packet_queue is None:

                communication.set_packet_queue(
                    PacketQueue()
                )

            if communication.statistics is None:

                communication.set_statistics(
                    TrafficStatistics()
                )

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
    # Replay Attack
    # ==================================================

    def _apply_replay(
        self,
        topic: str,
        payload: str,
    ) -> tuple[str, str]:
        """
        Apply the currently active replay attack state.

        When replay is enabled, an earlier packet from the
        shared packet buffer is selected and published
        instead of the current packet.
        """

        if not NetworkState.replay_enabled:

            return topic, payload

        packets = self.packet_buffer.get_all()

        if not packets:

            return topic, payload

        replay_packet = random.choice(packets)

        replay_topic = replay_packet.get(
            "topic",
            topic,
        )

        replay_payload = replay_packet.get(
            "payload",
            payload,
        )

        if not isinstance(
            replay_payload,
            str,
        ):

            replay_payload = json.dumps(
                replay_payload
            )

        self.statistics.packet_replayed()

        logger.warning(
            "Replayed MQTT packet | "
            "OriginalTopic=%s | ReplayTopic=%s | Client=%s",
            topic,
            replay_topic,
            self.client_id,
        )

        return (
            replay_topic,
            replay_payload,
        )

    # ==================================================
    # MQTT Topic Hijacking
    # ==================================================

    def _apply_topic_hijacking(
        self,
        topic: str,
    ) -> str:
        """
        Apply the currently active MQTT topic hijacking state.
        """

        if not NetworkState.hijacked_topic:

            return topic

        hijacked_topic = NetworkState.hijacked_topic

        logger.warning(
            "MQTT topic hijacked | "
            "OriginalTopic=%s | HijackedTopic=%s | Client=%s",
            topic,
            hijacked_topic,
            self.client_id,
        )

        return hijacked_topic

    # ==================================================
    # Packet Drop
    # ==================================================

    def _should_drop_packet(self) -> bool:
        """
        Determine whether the current packet should be dropped.

        Packet loss is controlled exclusively by the shared
        CommunicationController.
        """

        packet_loss = float(
            self.communication.packet_loss
        )

        if packet_loss <= 0:

            return False

        if packet_loss >= 100:

            return True

        return (
            random.uniform(
                0.0,
                100.0,
            )
            < packet_loss
        )

    # ==================================================
    # Packet Duplicate
    # ==================================================

    def _should_duplicate_packet(self) -> bool:
        """
        Determine whether a successfully transmitted packet
        should be duplicated.

        Duplication probability is controlled by the shared
        CommunicationController.
        """

        duplicate_rate = float(
            self.communication.packet_duplicate
        )

        if duplicate_rate <= 0:

            return False

        if duplicate_rate >= 100:

            return True

        return (
            random.uniform(
                0.0,
                100.0,
            )
            < duplicate_rate
        )

    # ==================================================
    # Packet Delay
    # ==================================================

    def _apply_delay(self) -> None:
        """
        Apply communication delay.

        The delay value comes from the shared
        CommunicationController.
        """

        delay = float(
            self.communication.delay
        )

        if delay <= 0:

            return

        self.statistics.packet_delayed()

        logger.debug(
            "Applying MQTT packet delay | "
            "Delay=%.3f seconds | Client=%s",
            delay,
            self.client_id,
        )

        time.sleep(delay)

    # ==================================================
    # Freeze
    # ==================================================

    def _is_frozen(self) -> bool:
        """
        Determine whether communication is currently frozen.
        """

        return bool(
            self.communication.freeze
        )

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

        Communication effects are applied in this order:

            1. Serialize payload
            2. Store original packet
            3. Freeze check
            4. Replay
            5. Topic hijacking
            6. Queue packet
            7. Apply delay
            8. Apply packet loss
            9. MQTT publish
            10. Optional packet duplication

        Returns:

            True:
                Packet successfully published.

            False:
                Packet was rejected, dropped, frozen,
                or MQTT publishing failed.
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
            # Store Original Packet
            # ==================================================
            # Store before network effects so replay attacks
            # have access to historical packets.
            # ==================================================

            self.packet_buffer.add_packet(
                topic,
                message,
            )

            # ==================================================
            # Freeze Communication
            # ==================================================

            if self._is_frozen():

                self.statistics.packet_dropped()

                logger.warning(
                    "Packet blocked because communication "
                    "is frozen | Topic=%s | Client=%s",
                    topic,
                    self.client_id,
                )

                return False

            # ==================================================
            # Replay Attack
            # ==================================================

            topic, payload = self._apply_replay(
                topic,
                payload,
            )

            # ==================================================
            # MQTT Topic Hijacking
            # ==================================================

            topic = self._apply_topic_hijacking(
                topic
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
            # Communication Delay
            # ==================================================

            self._apply_delay()

            # ==================================================
            # Communication Packet Loss
            # ==================================================

            if self._should_drop_packet():

                self.statistics.packet_dropped()

                logger.warning(
                    "Packet dropped by simulated "
                    "network conditions | "
                    "Loss=%.2f%% | Topic=%s | Client=%s",
                    self.communication.packet_loss,
                    topic,
                    self.client_id,
                )

                return False

            # ==================================================
            # MQTT Publish
            # ==================================================

            result = self.client.publish(
                topic,
                payload,
            )

            if result.rc != mqtt.MQTT_ERR_SUCCESS:

                logger.error(
                    "MQTT publish failed | "
                    "Topic=%s | Client=%s | RC=%s",
                    topic,
                    self.client_id,
                    result.rc,
                )

                return False

            self.statistics.packet_sent()

            logger.info(
                "Published MQTT message | "
                "Topic=%s | Client=%s",
                topic,
                self.client_id,
            )

            # ==================================================
            # Packet Duplication
            # ==================================================

            if self._should_duplicate_packet():

                duplicate_result = self.client.publish(
                    topic,
                    payload,
                )

                if (
                    duplicate_result.rc
                    == mqtt.MQTT_ERR_SUCCESS
                ):

                    self.statistics.packet_duplicated()

                    logger.warning(
                        "Duplicated MQTT packet | "
                        "Topic=%s | Client=%s",
                        topic,
                        self.client_id,
                    )

                else:

                    logger.error(
                        "MQTT duplicate publish failed | "
                        "Topic=%s | Client=%s | RC=%s",
                        topic,
                        self.client_id,
                        duplicate_result.rc,
                    )

            return True

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

    def get_statistics(self) -> dict:
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

    def disconnect(self) -> None:
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
                "Client=%s",
                self.client_id,
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