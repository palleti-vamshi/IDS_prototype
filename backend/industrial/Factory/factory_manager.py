"""
factory_manager.py

Central manager responsible for all factories in LightX-IDS.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from .factory import Factory

logger = logging.getLogger(__name__)


class FactoryManager:
    """
    Manages all factories in the system.

    Responsibilities:
        - Register factories
        - Remove factories
        - Lookup factories
        - Start all factories
        - Stop all factories
    """

    def __init__(self) -> None:
        self.factories: Dict[str, Factory] = {}

        logger.info("FactoryManager initialized.")

    # --------------------------------------------------
    # Factory Management
    # --------------------------------------------------

    def register_factory(self, factory: Factory) -> None:
        if factory.factory_code in self.factories:
            raise ValueError(
                f"Factory '{factory.factory_code}' already exists."
            )

        self.factories[factory.factory_code] = factory

        logger.info(
            "Factory '%s' registered.",
            factory.name,
        )

    def remove_factory(self, factory_code: str) -> None:
        self.factories.pop(factory_code, None)

        logger.info(
            "Factory '%s' removed.",
            factory_code,
        )

    def get_factory(
        self,
        factory_code: str,
    ) -> Optional[Factory]:
        return self.factories.get(factory_code)

    def list_factories(self) -> list[Factory]:
        return list(self.factories.values())

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def start_all(self) -> None:
        logger.info("Starting all factories...")

        for factory in self.factories.values():
            factory.start()

    def stop_all(self) -> None:
        logger.info("Stopping all factories...")

        for factory in self.factories.values():
            factory.stop()

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    @property
    def total_factories(self) -> int:
        return len(self.factories)

    def get_statistics(self) -> dict:
        total_lines = sum(
            factory.total_lines
            for factory in self.factories.values()
        )

        return {
            "factories": self.total_factories,
            "production_lines": total_lines,
        }

    def __str__(self) -> str:
        return (
            f"FactoryManager("
            f"Factories={self.total_factories})"
        )