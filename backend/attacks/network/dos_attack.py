"""
dos_attack.py

Advanced Denial of Service (DoS) Attack
"""

from __future__ import annotations

from backend.attacks.network.flood_engine import (
    FloodEngine,
)
from backend.attacks.network.network_attack import (
    NetworkAttack,
)
from backend.attacks.network.network_state import (
    NetworkState,
)


class DoSAttack(NetworkAttack):
    """
    Simulates a progressive Denial of Service attack
    using a network flood engine.
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

        self.flood_engine = FloodEngine(
            max_rate=5000,
        )

    # ==========================================
    # Lifecycle
    # ==========================================

    def start(self) -> None:

        self.flood_engine.start()

        super().start()

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

        self.flood_engine.update(
            progress,
        )

        NetworkState.delay = round(
            progress * self.max_delay,
            2,
        )

        NetworkState.packet_loss = round(
            progress * self.max_packet_loss,
            2,
        )

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            self.flood_engine.get_status()

        )

        return status

    # ==========================================
    # Stop
    # ==========================================

    def stop(
        self,
    ) -> None:

        self.flood_engine.stop()

        NetworkState.reset()

        super().stop()