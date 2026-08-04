"""
dos_attack.py

Denial of Service (DoS) Attack
"""

from __future__ import annotations

from backend.attacks.network.network_attack import NetworkAttack
from backend.attacks.network.network_state import NetworkState


class DoSAttack(NetworkAttack):
    """
    Simulates a Denial of Service attack by
    degrading network communication.
    """

    def __init__(
        self,
        attack_id: str = "NET_001",
        duration: float = 30.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="DoS Attack",
            duration=duration,
        )

        self.max_delay = 2.0
        self.max_packet_loss = 60.0

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

        NetworkState.packet_loss = (
            progress * self.max_packet_loss
        )

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        NetworkState.reset()

        super().stop()