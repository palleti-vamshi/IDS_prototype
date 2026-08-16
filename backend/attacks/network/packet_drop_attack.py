"""
packet_drop_attack.py

Advanced Packet Drop Attack
"""

from __future__ import annotations

from backend.attacks.network.network_attack import (
    NetworkAttack,
)
from backend.attacks.network.network_state import (
    NetworkState,
)


class PacketDropAttack(NetworkAttack):
    """
    Simulates progressively increasing
    packet loss across the IIoT network.
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

        self.current_packet_loss = 0.0

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

        self.current_packet_loss = round(
            progress * self.max_packet_loss,
            2,
        )

        NetworkState.packet_loss = (
            self.current_packet_loss
        )

        if (
            self.communication is not None
            and self.communication.statistics
            is not None
        ):

            self.communication.statistics.packet_dropped()

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "current_packet_loss":
                    self.current_packet_loss,
            }

        )

        return status

    # ==========================================
    # Stop
    # ==========================================

    def stop(
        self,
    ) -> None:

        self.current_packet_loss = 0.0

        NetworkState.packet_loss = 0.0

        super().stop()