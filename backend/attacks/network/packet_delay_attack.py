"""
packet_delay_attack.py

Advanced Packet Delay Attack
"""

from __future__ import annotations

from backend.attacks.network.network_attack import (
    NetworkAttack,
)
from backend.attacks.network.network_state import (
    NetworkState,
)


class PacketDelayAttack(NetworkAttack):
    """
    Simulates progressively increasing
    network latency.
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

        self.current_delay = 0.0

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

        self.current_delay = round(
            progress * self.max_delay,
            2,
        )

        NetworkState.delay = self.current_delay

        if (
            self.communication is not None
            and self.communication.statistics
            is not None
        ):

            self.communication.statistics.packet_delayed()

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "current_delay":
                    self.current_delay,
            }

        )

        return status

    # ==========================================
    # Stop
    # ==========================================

    def stop(
        self,
    ) -> None:

        self.current_delay = 0.0

        NetworkState.delay = 0.0

        super().stop()