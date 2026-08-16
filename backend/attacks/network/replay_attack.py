"""
replay_attack.py

Advanced Replay Attack
"""

from __future__ import annotations

import random

from backend.attacks.network.network_attack import (
    NetworkAttack,
)


class ReplayAttack(NetworkAttack):
    """
    Replays previously transmitted MQTT packets
    captured by the Communication Engine.
    """

    def __init__(
        self,
        attack_id: str = "NET_002",
        duration: float = 20.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Replay Attack",
            duration=duration,
        )

        self.replayed_packets = 0

    # ==========================================
    # Replay Packet
    # ==========================================

    def modify_packet(
        self,
        topic: str,
        payload,
    ):

        if (
            not self.is_running
            or self.communication is None
            or self.communication.packet_buffer is None
        ):

            return topic, payload

        packets = (
            self.communication
            .packet_buffer
            .get_all()
        )

        if not packets:

            return topic, payload

        packet = random.choice(
            packets
        )

        self.replayed_packets += 1

        if (
            self.communication.statistics
            is not None
        ):

            self.communication.statistics.packet_replayed()

        return (
            packet["topic"],
            packet["payload"],
        )

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        pass

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "replayed_packets":
                    self.replayed_packets
            }

        )

        return status

    # ==========================================
    # Stop
    # ==========================================

    def stop(
        self,
    ) -> None:

        self.replayed_packets = 0

        super().stop()