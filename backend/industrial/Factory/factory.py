"""
factory.py

Represents the Digital Twin of a Smart Factory.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional
from uuid import uuid4

from backend.industrial.common import OperationalState
from .production_line import ProductionLine

logger = logging.getLogger(__name__)


class Factory:
    """
    Represents a single smart factory.

    A factory owns one or more production lines and manages
    their lifecycle.
    """

    def __init__(
        self,
        factory_code: str,
        name: str,
        description: str = "",
    ) -> None:

        # -----------------------------
        # Identity
        # -----------------------------
        self.uuid = str(uuid4())
        self.factory_code = factory_code
        self.name = name
        self.description = description

        # -----------------------------
        # State
        # -----------------------------
        self.state = OperationalState.STOPPED

        # -----------------------------
        # Factory Components
        # -----------------------------
        self.production_lines: Dict[str, ProductionLine] = {}

        logger.info(
            "Factory created: %s (%s)",
            self.name,
            self.factory_code,
        )

    # ====================================================
    # Lifecycle
    # ====================================================

    def start(self) -> None:
        """Start the factory."""

        logger.info("Starting factory: %s", self.name)

        self.state = OperationalState.RUNNING

        for line in self.production_lines.values():
            line.start()

    def stop(self) -> None:
        """Stop the factory."""

        logger.info("Stopping factory: %s", self.name)

        for line in self.production_lines.values():
            line.stop()

        self.state = OperationalState.STOPPED

    # ====================================================
    # Production Line Management
    # ====================================================

    def add_production_line(
        self,
        line: ProductionLine,
    ) -> None:
        """Register a production line."""

        if line.line_code in self.production_lines:
            raise ValueError(
                f"Production line '{line.line_code}' already exists."
            )

        self.production_lines[line.line_code] = line

        logger.info(
            "Production line '%s' added to factory '%s'.",
            line.name,
            self.name,
        )

    def remove_production_line(
        self,
        line_code: str,
    ) -> None:
        """Remove a production line."""

        self.production_lines.pop(line_code, None)

    def get_production_line(
        self,
        line_code: str,
    ) -> Optional[ProductionLine]:
        """Return a production line."""

        return self.production_lines.get(line_code)

    def list_production_lines(self) -> list[ProductionLine]:
        """Return all production lines."""

        return list(self.production_lines.values())

    # ====================================================
    # Statistics
    # ====================================================

    @property
    def total_lines(self) -> int:
        return len(self.production_lines)

    def get_status(self) -> dict:
        """Return factory status."""

        return {
            "uuid": self.uuid,
            "factory_code": self.factory_code,
            "name": self.name,
            "state": self.state.value,
            "production_lines": self.total_lines,
        }

    # ====================================================

    def __str__(self) -> str:
        return (
            f"Factory("
            f"{self.factory_code}, "
            f"{self.name}, "
            f"Lines={self.total_lines})"
        )