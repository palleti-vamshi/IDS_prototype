"""
base_machine.py

Abstract base class for all industrial machines in LightX-IDS.
"""

from __future__ import annotations

import logging
from abc import ABC
from typing import Any
from uuid import uuid4

from backend.industrial.common import OperationalState

logger = logging.getLogger(__name__)


class BaseMachine(ABC):
    """
    Base class for all industrial machines.

    Provides:
    - Lifecycle management
    - Runtime tracking
    - Health monitoring
    - Sensor attachment
    - Telemetry interface
    """

    def __init__(
        self,
        machine_code: str,
        name: str,
        description: str = "",
    ) -> None:

        # ==================================================
        # Identity
        # ==================================================

        self.uuid = str(uuid4())
        self.machine_code = machine_code
        self.name = name
        self.description = description

        # ==================================================
        # Operational State
        # ==================================================

        self.state = OperationalState.STOPPED
        self.is_active = False

        # ==================================================
        # Health
        # ==================================================

        self.health = 100.0
        self.runtime_hours = 0.0

        # ==================================================
        # Connected Sensors
        # ==================================================

        self.sensors: dict[str, Any] = {}

        logger.info(
            "%s (%s) created.",
            self.name,
            self.machine_code,
        )

    # ==================================================
    # Lifecycle
    # ==================================================

    def start(self) -> None:
        """Start machine."""

        self.state = OperationalState.RUNNING
        self.is_active = True

        logger.info("%s started.", self.name)

    def stop(self) -> None:
        """Stop machine."""

        self.state = OperationalState.STOPPED
        self.is_active = False

        logger.info("%s stopped.", self.name)

    def maintenance(self) -> None:
        """Switch machine to maintenance mode."""

        self.state = OperationalState.MAINTENANCE

        logger.info("%s under maintenance.", self.name)

    def fault(self) -> None:
        """Switch machine to fault state."""

        self.state = OperationalState.FAULT

        logger.warning("%s entered FAULT state.", self.name)

    # ==================================================
    # Runtime
    # ==================================================

    def update_runtime(self, hours: float) -> None:
        """Update runtime."""

        if hours < 0:
            raise ValueError(
                "Runtime cannot be negative."
            )

        self.runtime_hours += hours

    # ==================================================
    # Health
    # ==================================================

    def update_health(
        self,
        value: float,
    ) -> None:
        """Update machine health."""

        self.health = max(
            0.0,
            min(100.0, value),
        )

    # ==================================================
    # Sensors
    # ==================================================

    def attach_sensor(
        self,
        sensor: Any,
    ) -> None:
        """Attach a sensor."""

        self.sensors[sensor.sensor_code] = sensor

    def remove_sensor(
        self,
        sensor_code: str,
    ) -> None:
        """Remove attached sensor."""

        self.sensors.pop(sensor_code, None)

    def get_sensors(self) -> list[Any]:
        """Return all attached sensors."""

        return list(self.sensors.values())

    # ==================================================
    # Telemetry
    # ==================================================

    def update_telemetry(
        self,
        **kwargs,
    ) -> None:
        """Update telemetry dynamically."""

        for key, value in kwargs.items():

            if hasattr(self, key):
                setattr(self, key, value)

    def get_telemetry(self) -> dict:
        """Return telemetry only."""

        excluded = {
            "uuid",
            "machine_code",
            "name",
            "description",
            "state",
            "health",
            "runtime_hours",
            "is_active",
            "sensors",
        }

        telemetry = {}

        for key, value in self.__dict__.items():

            if key not in excluded:
                telemetry[key] = value

        return telemetry

    # ==================================================
    # Status
    # ==================================================

    def get_status(self) -> dict:
        """Return complete machine status."""

        return {
            "uuid": self.uuid,
            "machine_code": self.machine_code,
            "name": self.name,
            "state": self.state.value,
            "health": self.health,
            "runtime_hours": self.runtime_hours,
            "is_active": self.is_active,
            "attached_sensors": len(self.sensors),
            "telemetry": self.get_telemetry(),
        }

    # ==================================================

    def __str__(self) -> str:
        return (
            f"{self.name} "
            f"({self.machine_code})"
        )