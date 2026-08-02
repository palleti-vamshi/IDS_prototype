"""
production_line.py

Represents a production line inside a smart factory.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from uuid import uuid4

from backend.industrial.common import OperationalState

logger = logging.getLogger(__name__)


class ProductionLine:
    """
    Represents a production line.

    A production line owns:
    - One PLC
    - Multiple Machines
    - Multiple Sensors
    """

    def __init__(
        self,
        line_code: str,
        name: str,
        description: str = "",
    ) -> None:

        # -----------------------------
        # Identity
        # -----------------------------
        self.uuid = str(uuid4())
        self.line_code = line_code
        self.name = name
        self.description = description

        # -----------------------------
        # Operational State
        # -----------------------------
        self.state = OperationalState.STOPPED

        # -----------------------------
        # Industrial Assets
        # -----------------------------
        self.plc: Optional[Any] = None

        self.machines: Dict[str, Any] = {}
        self.sensors: Dict[str, Any] = {}

        logger.info(
            "Production Line created: %s (%s)",
            self.name,
            self.line_code,
        )

    # ====================================================
    # Lifecycle
    # ====================================================

    def start(self) -> None:
        """Start the production line."""

        self.state = OperationalState.RUNNING

        logger.info(
            "Production line '%s' started.",
            self.name,
        )

    def stop(self) -> None:
        """Stop the production line."""

        self.state = OperationalState.STOPPED

        logger.info(
            "Production line '%s' stopped.",
            self.name,
        )

    # ====================================================
    # PLC
    # ====================================================

    def set_plc(self, plc: Any) -> None:
        """Assign a PLC to this production line."""

        self.plc = plc

    # ====================================================
    # Machine Management
    # ====================================================

    def add_machine(self, machine: Any) -> None:
        """Add a machine."""

        self.machines[machine.machine_code] = machine

    def remove_machine(self, machine_code: str) -> None:
        """Remove a machine."""

        self.machines.pop(machine_code, None)

    def get_machine(self, machine_code: str) -> Optional[Any]:
        """Return a machine."""

        return self.machines.get(machine_code)

    # ====================================================
    # Sensor Management
    # ====================================================

    def add_sensor(self, sensor: Any) -> None:
        """Add a production-line sensor."""

        self.sensors[sensor.sensor_code] = sensor

    def remove_sensor(self, sensor_code: str) -> None:
        """Remove a sensor."""

        self.sensors.pop(sensor_code, None)

    def get_sensor(self, sensor_code: str) -> Optional[Any]:
        """Return a sensor."""

        return self.sensors.get(sensor_code)

    # ====================================================
    # Statistics
    # ====================================================

    @property
    def total_machines(self) -> int:
        return len(self.machines)

    @property
    def total_sensors(self) -> int:
        return len(self.sensors)

    def get_status(self) -> dict:
        """Return production line status."""

        return {
            "uuid": self.uuid,
            "line_code": self.line_code,
            "name": self.name,
            "state": self.state.value,
            "machines": self.total_machines,
            "sensors": self.total_sensors,
            "plc_connected": self.plc is not None,
        }

    # ====================================================

    def __str__(self) -> str:
        return (
            f"ProductionLine("
            f"{self.line_code}, "
            f"{self.name})"
        )