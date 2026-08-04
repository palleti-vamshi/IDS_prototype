"""
packet_drop_attack.py

Packet Drop Attack
"""

from __future__ import annotations

from backend.attacks.network.network_attack import NetworkAttack
from backend.attacks.network.network_state import (
    NetworkState,
)


class PacketDropAttack(NetworkAttack):
    """
    Simulates packet loss without adding latency.
    """

    def __init__(
        self,
        attack_id: str = "NET_004",
        duration: float = 20.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Packet Drop Attack",
            duration=duration,
        )

        self.max_packet_loss = 100.0

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

        NetworkState.packet_loss = (
            progress * self.max_packet_loss
        )

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        NetworkState.packet_loss = 0.0

        super().stop()