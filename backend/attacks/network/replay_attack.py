"""
replay_attack.py

Replay Attack
"""

from __future__ import annotations

import random

from backend.attacks.network.network_attack import NetworkAttack


class ReplayAttack(NetworkAttack):
    """
    Replays previously captured MQTT packets.
    """

    MAX_BUFFER = 100

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

        self.packet_buffer = []

    # ==========================================
    # Capture Packets
    # ==========================================

    def capture_packet(
        self,
        topic: str,
        payload,
    ) -> None:

        self.packet_buffer.append(
            {
                "topic": topic,
                "payload": payload,
            }
        )

        if len(self.packet_buffer) > self.MAX_BUFFER:
            self.packet_buffer.pop(0)

    # ==========================================
    # Modify Packet
    # ==========================================

    def modify_packet(
        self,
        topic: str,
        payload,
    ):
        """
        Return an old packet when replay attack
        is active.
        """

        if (
            self.is_running
            and self.packet_buffer
        ):
            packet = random.choice(
                self.packet_buffer
            )

            return (
                packet["topic"],
                packet["payload"],
            )

        return topic, payload

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:
        """
        Replay attack has no continuous effect.
        """
        pass

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        super().stop()