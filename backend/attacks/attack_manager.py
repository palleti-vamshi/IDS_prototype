"""
attack_manager.py

Central manager for all industrial cyber attacks.
"""

from __future__ import annotations

from backend.core.logger import setup_logger


class AttackManager:
    """
    Central controller responsible for
    managing all cyber attacks.
    """

    def __init__(self) -> None:

        self.logger = setup_logger(
            "AttackManager"
        )

        self.attacks = {}

    # ==================================================
    # Registration
    # ==================================================

    def register_attack(
        self,
        attack,
    ) -> None:

        self.attacks[
            attack.attack_id
        ] = attack

        self.logger.info(
            "Registered attack: %s",
            attack.attack_name,
        )

    # ==================================================
    # Remove
    # ==================================================

    def remove_attack(
        self,
        attack_id: str,
    ) -> None:

        self.attacks.pop(
            attack_id,
            None,
        )

    # ==================================================
    # Start
    # ==================================================

    def start_attack(
        self,
        attack_id: str,
    ) -> None:

        attack = self.attacks.get(
            attack_id
        )

        if attack:

            attack.start()

    # ==================================================
    # Stop
    # ==================================================

    def stop_attack(
        self,
        attack_id: str,
    ) -> None:

        attack = self.attacks.get(
            attack_id
        )

        if attack:

            attack.stop()

    # ==================================================
    # Update
    # ==================================================

    def update(
        self,
        dt: float,
    ) -> None:

        for attack in self.attacks.values():

            if attack.is_running:

                attack.update(dt)

                # Automatically stop completed attacks
                if attack.is_finished:

                    attack.stop()

    # ==================================================
    # Bulk Operations
    # ==================================================

    def stop_all(self) -> None:

        for attack in self.attacks.values():

            if attack.is_running:

                attack.stop()

    def clear(self) -> None:

        self.stop_all()

        self.attacks.clear()

    # ==================================================
    # Access
    # ==================================================

    def get_attack(
        self,
        attack_id: str,
    ):

        return self.attacks.get(
            attack_id
        )

    @property
    def total_attacks(self) -> int:

        return len(
            self.attacks
        )

    @property
    def active_attacks(self) -> int:

        return sum(
            attack.is_running
            for attack in self.attacks.values()
        )

    # ==================================================
    # Information
    # ==================================================

    def get_status(self) -> dict:

        return {

            "registered_attacks":
                self.total_attacks,

            "active_attacks":
                self.active_attacks,

            "attack_ids":
                list(
                    self.attacks.keys()
                ),
        }

    def __str__(self) -> str:

        return (
            f"AttackManager("
            f"{self.active_attacks}/"
            f"{self.total_attacks}"
            f" active)"
        )