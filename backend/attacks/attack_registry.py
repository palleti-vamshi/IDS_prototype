"""
attack_registry.py

Registry for all supported cyber attacks.
"""

from __future__ import annotations

from backend.core.logger import setup_logger


class AttackRegistry:
    """
    Registry of all available attack classes.

    Responsible for:

    • Registering attack classes
    • Creating attack instances
    • Listing available attacks
    """

    def __init__(self) -> None:

        self.logger = setup_logger(
            "AttackRegistry"
        )

        self._registry = {}

    # ==================================================
    # Registration
    # ==================================================

    def register(
        self,
        name: str,
        attack_class,
    ) -> None:
        """
        Register an attack class.
        """

        self._registry[name] = attack_class

        self.logger.info(
            "Registered attack class: %s",
            name,
        )

    # ==================================================
    # Factory
    # ==================================================

    def create(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        """
        Create an attack instance.
        """

        attack_class = self._registry.get(name)

        if attack_class is None:

            raise ValueError(
                f"Unknown attack: {name}"
            )

        return attack_class(
            *args,
            **kwargs,
        )

    # ==================================================
    # Access
    # ==================================================

    def exists(
        self,
        name: str,
    ) -> bool:

        return name in self._registry

    def get_attack_class(
        self,
        name: str,
    ):

        return self._registry.get(name)

    def list_attacks(self) -> list[str]:

        return sorted(
            self._registry.keys()
        )

    def clear(self) -> None:

        self._registry.clear()

    @property
    def total_attacks(self) -> int:

        return len(
            self._registry
        )

    # ==================================================
    # Information
    # ==================================================

    def get_status(self) -> dict:

        return {

            "registered_attacks":
                self.total_attacks,

            "attacks":
                self.list_attacks(),
        }

    def __str__(self) -> str:

        return (
            f"AttackRegistry("
            f"{self.total_attacks} attacks)"
        )