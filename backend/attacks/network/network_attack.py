"""
network_attack.py

Base class for all network-based cyber attacks.
"""

from __future__ import annotations

from abc import ABC

from backend.attacks.base_attack import BaseAttack
from backend.attacks.attack_type import AttackType
from backend.attacks.attack_target import AttackTarget


class NetworkAttack(BaseAttack, ABC):
    """
    Base class for all network attacks.

    Provides access to the communication controller
    shared by all network attack implementations.
    """

    def __init__(
        self,
        attack_id: str,
        attack_name: str,
        duration: float = 30.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name=attack_name,
            attack_type=AttackType.NETWORK,
            attack_target=AttackTarget.COMMUNICATION,
            duration=duration,
        )

        self.communication = None

    # ==================================================
    # Communication Controller
    # ==================================================

    def set_communication(
        self,
        controller,
    ) -> None:
        """
        Assign the communication controller.
        """

        self.communication = controller

    # ==================================================
    # Reset Communication
    # ==================================================

    def reset_communication(self) -> None:
        """
        Restore normal communication.
        """

        if self.communication is not None:

            self.communication.reset()

    # ==================================================
    # Stop
    # ==================================================

    def stop(self) -> None:

        self.reset_communication()

        super().stop()