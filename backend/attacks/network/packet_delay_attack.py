"""
packet_delay_attack.py

Packet Delay Attack
"""

from __future__ import annotations

from backend.attacks.network.network_attack import NetworkAttack
from backend.attacks.network.network_state import (
    NetworkState,
)


class PacketDelayAttack(NetworkAttack):
    """
    Simulates increasing network latency.
    """

    def __init__(
        self,
        attack_id: str = "NET_003",
        duration: float = 20.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Packet Delay Attack",
            duration=duration,
        )

        self.max_delay = 5.0

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        progress = min(
            self.elapsed_time / self.duration,
            1.0,
        )

        NetworkState.delay = (
            progress * self.max_delay
        )

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        NetworkState.delay = 0.0

        super().stop()