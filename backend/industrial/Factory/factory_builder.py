"""
factory_builder.py

Constructs the complete industrial digital twin.
"""

from __future__ import annotations

from backend.industrial.factory.factory import Factory
from backend.industrial.factory.production_line import ProductionLine
from backend.industrial.factory.sensor_registry import SensorRegistry

from backend.industrial.machines import (
    Motor,
    Pump,
    Tank,
    Conveyor,
    Valve,
    Compressor,
)


class FactoryBuilder:
    """
    Responsible for constructing the complete
    industrial factory hierarchy.
    """

    def __init__(self) -> None:

        self.factory: Factory | None = None
        self.production_line: ProductionLine | None = None

        self.machines: list = []

    # ==================================================
    # Factory
    # ==================================================

    def build_factory(self) -> Factory:

        self.factory = Factory(
            factory_code="FAC-001",
            name="LightX Smart Factory",
            description="Industrial Digital Twin",
        )

        return self.factory

    # ==================================================
    # Production Line
    # ==================================================

    def build_production_line(self) -> ProductionLine:

        self.production_line = ProductionLine(
            line_code="LINE-001",
            name="Production Line 1",
            description="Main Manufacturing Line",
        )

        return self.production_line

    # ==================================================
    # Machines
    # ==================================================

    def build_machines(self) -> list:

        self.machines = [

            Motor(
                machine_code="MTR-001",
            ),

            Pump(
                machine_code="PMP-001",
            ),

            Tank(
                machine_code="TNK-001",
            ),

            Conveyor(
                machine_code="CNV-001",
            ),

            Valve(
                machine_code="VLV-001",
            ),

            Compressor(
                machine_code="CMP-001",
            ),
        ]

        return self.machines

    # ==================================================
    # Assembly
    # ==================================================

    def assemble(self) -> Factory:
        """
        Construct the complete factory.
        """

        factory = self.build_factory()

        line = self.build_production_line()

        machines = self.build_machines()

        # ----------------------------------------------

        for machine in machines:

            SensorRegistry.attach_default_sensors(
                machine
            )

            line.add_machine(
                machine
            )

        # ----------------------------------------------

        factory.add_production_line(
            line
        )

        return factory

    # ==================================================
    # Access
    # ==================================================

    def get_factory(self) -> Factory:

        return self.factory

    def get_production_line(
        self,
    ) -> ProductionLine:

        return self.production_line

    def get_machines(self) -> list:

        return self.machines

    # ==================================================

    def get_status(self) -> dict:

        return {

            "factory": (
                self.factory.factory_code
                if self.factory
                else None
            ),

            "production_line": (
                self.production_line.line_code
                if self.production_line
                else None
            ),

            "machines": len(
                self.machines
            ),
        }