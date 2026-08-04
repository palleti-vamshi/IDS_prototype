"""
valve_behavior.py

Behavior model for an industrial control valve.
"""

from __future__ import annotations

from backend.attacks.process.process_state import (
    ProcessState,
)

from backend.industrial.behavior.base_behavior import BaseBehavior
from backend.industrial.behavior.state_models import BehaviorState


class ValveBehavior(BaseBehavior):
    """
    Controls the operating behavior of an industrial valve.
    """

    def __init__(self, machine) -> None:
        super().__init__(machine)

    def update(
        self,
        dt: float,
    ) -> None:

        self.update_time(dt)

        # ==================================================
        # STOPPED
        # ==================================================

        if self.state == BehaviorState.STOPPED:

            self.machine.position = self.approach(
                self.machine.position,
                0,
                15,
                dt,
            )

            self.machine.flow_rate = self.approach(
                self.machine.flow_rate,
                0,
                8,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                101.3,
                2,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                25,
                0.2,
                dt,
            )

            self.machine.is_open = False

        # ==================================================
        # STARTING
        # ==================================================

        elif self.state == BehaviorState.STARTING:

            self.machine.position = self.approach(
                self.machine.position,
                35,
                5,
                dt,
            )

            self.machine.flow_rate = self.approach(
                self.machine.flow_rate,
                20,
                3,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                120,
                2,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                28,
                0.2,
                dt,
            )

            self.machine.is_open = (
                self.machine.position > 5
            )

            if self.time_in_state >= 5:

                self.set_state(
                    BehaviorState.NORMAL
                )

        # ==================================================
        # NORMAL
        # ==================================================

        elif self.state == BehaviorState.NORMAL:

            self.machine.position = self.approach(
                self.machine.position,
                60,
                3,
                dt,
            )

            self.machine.flow_rate = self.approach(
                self.machine.flow_rate,
                45,
                2,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                140,
                2,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                35,
                0.2,
                dt,
            )

            self.machine.is_open = (
                self.machine.position > 5
            )

        # ==================================================
        # HIGH LOAD
        # ==================================================

        elif self.state == BehaviorState.HIGH_LOAD:

            self.machine.position = self.approach(
                self.machine.position,
                100,
                4,
                dt,
            )

            self.machine.flow_rate = self.approach(
                self.machine.flow_rate,
                75,
                3,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                180,
                2,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                45,
                0.4,
                dt,
            )

            self.machine.is_open = True

        # ==================================================
        # FAULT
        # ==================================================

        elif self.state == BehaviorState.FAULT:

            self.machine.position = self.approach(
                self.machine.position,
                0,
                10,
                dt,
            )

            self.machine.flow_rate = self.approach(
                self.machine.flow_rate,
                0,
                5,
                dt,
            )

            self.machine.is_open = False

        # ==================================================
        # Process Attack
        # ==================================================

        if ProcessState.valve_stuck:

            # Freeze valve at current position
            self.machine.position = self.machine.position

            self.machine.is_open = (
                self.machine.position > 5
            )