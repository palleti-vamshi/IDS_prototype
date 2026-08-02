"""
behavior_engine.py

Central behavior engine for all industrial machines.
"""

from __future__ import annotations

from backend.industrial.behavior.state_models import BehaviorState

from backend.industrial.behavior.motor_behavior import MotorBehavior
from backend.industrial.behavior.pump_behavior import PumpBehavior
from backend.industrial.behavior.tank_behavior import TankBehavior
from backend.industrial.behavior.conveyor_behavior import ConveyorBehavior
from backend.industrial.behavior.valve_behavior import ValveBehavior
from backend.industrial.behavior.compressor_behavior import CompressorBehavior

from backend.industrial.machines import (
    Motor,
    Pump,
    Tank,
    Conveyor,
    Valve,
    Compressor,
)


class BehaviorEngine:
    """
    Central controller responsible for updating
    every machine behavior model.
    """

    def __init__(self) -> None:

        self.behaviors = {}

    # ==================================================
    # Registration
    # ==================================================

    def register_machine(
        self,
        machine,
    ) -> None:
        """
        Register a machine with its behavior model.
        """

        if isinstance(machine, Motor):

            behavior = MotorBehavior(machine)

        elif isinstance(machine, Pump):

            behavior = PumpBehavior(machine)

        elif isinstance(machine, Tank):

            behavior = TankBehavior(machine)

        elif isinstance(machine, Conveyor):

            behavior = ConveyorBehavior(machine)

        elif isinstance(machine, Valve):

            behavior = ValveBehavior(machine)

        elif isinstance(machine, Compressor):

            behavior = CompressorBehavior(machine)

        else:

            raise TypeError(
                f"Unsupported machine type: {type(machine).__name__}"
            )

        self.behaviors[machine.machine_code] = behavior

    # ==================================================
    # Lifecycle
    # ==================================================

    def start_all(self) -> None:
        """
        Move every registered behavior from
        STOPPED to STARTING.
        """

        for behavior in self.behaviors.values():

            behavior.set_state(
                BehaviorState.STARTING
            )

    def stop_all(self) -> None:
        """
        Stop every registered behavior.
        """

        for behavior in self.behaviors.values():

            behavior.set_state(
                BehaviorState.STOPPED
            )

    # ==================================================
    # Update
    # ==================================================

    def update(
        self,
        dt: float,
    ) -> None:
        """
        Update every registered behavior.
        """

        for behavior in self.behaviors.values():

            behavior.update(dt)

    # ==================================================
    # Access
    # ==================================================

    def get_behavior(
        self,
        machine_code: str,
    ):

        return self.behaviors.get(machine_code)

    def remove_machine(
        self,
        machine_code: str,
    ) -> None:

        self.behaviors.pop(machine_code, None)

    def clear(self) -> None:

        self.behaviors.clear()

    @property
    def total_behaviors(self) -> int:

        return len(self.behaviors)

    def get_status(self) -> dict:

        return {
            "registered_behaviors": self.total_behaviors,
            "machines": list(self.behaviors.keys()),
        }

    def __str__(self) -> str:

        return (
            f"BehaviorEngine("
            f"behaviors={self.total_behaviors})"
        )