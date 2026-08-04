"""
dos_attack.py

Denial of Service (DoS) attack implementation.
"""

from __future__ import annotations

from backend.attacks.base_attack import BaseAttack
from backend.attacks.attack_type import AttackType
from backend.attacks.attack_target import AttackTarget


class DoSAttack(BaseAttack):
    """
    Simulates a Denial of Service attack by
    degrading the communication channel.
    """

    def __init__(
        self,
        attack_id: str = "ATTACK_001",
        duration: float = 30.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="DoS Attack",
            attack_type=AttackType.NETWORK,
            attack_target=AttackTarget.COMMUNICATION,
            duration=duration,
        )

        self.communication = None

        self.max_delay = 2.0

        self.max_packet_loss = 60.0

        self.max_congestion = 100.0

    # ==================================================
    # Communication
    # ==================================================

    def set_communication(
        self,
        controller,
    ) -> None:
        """
        Assign communication controller.
        """

        self.communication = controller

    # ==================================================
    # Runtime
    # ==================================================

    def apply(
        self,
        dt: float,
    ) -> None:
        """
        Apply DoS behaviour.
        """

        if self.communication is None:
            return

        progress = min(
            self.elapsed_time / self.duration,
            1.0,
        )

        delay = progress * self.max_delay

        packet_loss = (
            progress
            * self.max_packet_loss
        )

        congestion = (
            progress
            * self.max_congestion
        )

        self.communication.set_delay(
            delay
        )

        self.communication.set_packet_loss(
            packet_loss
        )

        self.communication.set_congestion(
            congestion
        )

    # ==================================================
    # Stop
    # ==================================================

    def stop(self) -> None:

        if self.communication is not None:

            self.communication.reset()

        super().stop()