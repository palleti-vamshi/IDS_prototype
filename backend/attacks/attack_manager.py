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

    AttackManager owns the registered attack objects
    and is responsible for their runtime updates.

    Phase 3 dataset generation uses this manager as
    the single execution point for attacks.
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
        """
        Register an attack with the manager.

        Existing attack IDs are replaced so that
        registration remains deterministic.
        """

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
        """
        Remove an attack from the manager.

        The attack is stopped first if it is currently
        running, then its resources are released.
        """

        attack = self.attacks.pop(
            attack_id,
            None,
        )

        if attack is None:
            return

        if attack.is_running:
            attack.stop()

        # Release resources owned by the attack.
        close_method = getattr(
            attack,
            "close",
            None,
        )

        if callable(close_method):
            close_method()

    # ==================================================
    # Start
    # ==================================================

    def start_attack(
        self,
        attack_id: str,
    ) -> bool:
        """
        Start a registered attack.

        Returns True when the attack exists and the
        start request was accepted.
        """

        attack = self.attacks.get(
            attack_id
        )

        if attack is None:

            self.logger.warning(
                "Attack not found: %s",
                attack_id,
            )

            return False

        if not attack.enabled:

            self.logger.warning(
                "Attack disabled: %s",
                attack.attack_name,
            )

            return False

        if attack.is_running:

            self.logger.info(
                "Attack already running: %s",
                attack.attack_name,
            )

            return False

        attack.start()

        return True

    # ==================================================
    # Stop
    # ==================================================

    def stop_attack(
        self,
        attack_id: str,
    ) -> bool:
        """
        Stop a registered attack.

        Returns True when the attack exists.
        """

        attack = self.attacks.get(
            attack_id
        )

        if attack is None:

            self.logger.warning(
                "Attack not found: %s",
                attack_id,
            )

            return False

        if attack.is_running:

            attack.stop()

        return True

    # ==================================================
    # Update
    # ==================================================

    def update(
        self,
        dt: float,
    ) -> None:
        """
        Update all currently running attacks.

        This method is called once per simulation tick.
        """

        for attack in list(
            self.attacks.values()
        ):

            if not attack.is_running:
                continue

            attack.update(dt)

            # ------------------------------------------
            # Automatically stop completed attacks
            # ------------------------------------------

            if attack.is_finished:

                attack.stop()

    # ==================================================
    # Bulk Operations
    # ==================================================

    def stop_all(
        self,
    ) -> None:
        """
        Stop all currently running attacks.
        """

        for attack in self.attacks.values():

            if attack.is_running:

                attack.stop()

    def clear(
        self,
    ) -> None:
        """
        Stop all attacks, release their resources,
        and remove them from the manager.
        """

        self.stop_all()

        for attack in self.attacks.values():

            close_method = getattr(
                attack,
                "close",
                None,
            )

            if callable(close_method):

                close_method()

        self.attacks.clear()

    # ==================================================
    # Access
    # ==================================================

    def get_attack(
        self,
        attack_id: str,
    ):
        """
        Return a registered attack by ID.
        """

        return self.attacks.get(
            attack_id
        )

    def get_attacks(self) -> list:
        """
        Return all registered attacks.
        """

        return list(
            self.attacks.values()
        )

    # ==================================================
    # Properties
    # ==================================================

    @property
    def total_attacks(
        self,
    ) -> int:

        return len(
            self.attacks
        )

    @property
    def active_attacks(
        self,
    ) -> int:

        return sum(
            attack.is_running
            for attack in self.attacks.values()
        )

    # ==================================================
    # Information
    # ==================================================

    def get_status(
        self,
    ) -> dict:
        """
        Return attack manager status.
        """

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

    # ==================================================
    # String
    # ==================================================

    def __str__(
        self,
    ) -> str:

        return (
            f"AttackManager("
            f"{self.active_attacks}/"
            f"{self.total_attacks}"
            f" active)"
        )