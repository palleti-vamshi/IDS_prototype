"""
dependency_engine.py

Machine dependency engine for the
LightX-IDS Digital Twin.
"""

from __future__ import annotations

from backend.industrial.machines import (
    Motor,
    Conveyor,
    Pump,
    Valve,
    Tank,
)

from backend.industrial.physics.process_models import (
    ProcessModels,
)


class DependencyEngine:
    """
    Handles machine-to-machine physical
    dependencies.
    """

    def __init__(self) -> None:

        self.motor: Motor | None = None
        self.conveyor: Conveyor | None = None
        self.pump: Pump | None = None
        self.valve: Valve | None = None
        self.tank: Tank | None = None

    # ==================================================
    # Registration
    # ==================================================

    def register_machine(
        self,
        machine,
    ) -> None:

        if isinstance(machine, Motor):
            self.motor = machine

        elif isinstance(machine, Conveyor):
            self.conveyor = machine

        elif isinstance(machine, Pump):
            self.pump = machine

        elif isinstance(machine, Valve):
            self.valve = machine

        elif isinstance(machine, Tank):
            self.tank = machine

    # ==================================================
    # Physics Update
    # ==================================================

    def update(
        self,
        dt: float,
    ) -> None:

        # ------------------------------------------
        # Motor -> Conveyor
        # ------------------------------------------

        if self.motor and self.conveyor:

            self.motor.load = (
                ProcessModels.calculate_motor_load(
                    self.conveyor.load
                )
            )

        # ------------------------------------------
        # Motor -> Pump
        # ------------------------------------------

        if self.motor and self.pump:

            efficiency = (
                ProcessModels.calculate_pump_efficiency(
                    self.motor.health
                )
            )

            self.pump.flow_rate *= efficiency

        # ------------------------------------------
        # Pump -> Valve
        # ------------------------------------------

        if self.pump and self.valve:

            flow = (
                ProcessModels.calculate_flow(
                    self.pump.flow_rate,
                    self.valve.position,
                )
            )

            self.valve.flow_rate = flow

            self.pump.pressure = (
                ProcessModels.calculate_pressure(
                    flow,
                    self.valve.position,
                )
            )

        # ------------------------------------------
        # Valve -> Tank
        # ------------------------------------------

        if self.valve and self.tank:

            self.tank.inflow_rate = (
                self.valve.flow_rate
            )

            self.tank.current_level = (
                ProcessModels.calculate_tank_level(
                    self.tank.current_level,
                    self.tank.inflow_rate,
                    self.tank.outflow_rate,
                    dt,
                    self.tank.capacity,
                )
            )

            self.tank.level_percentage = round(
                (
                    self.tank.current_level
                    / self.tank.capacity
                )
                * 100,
                2,
            )