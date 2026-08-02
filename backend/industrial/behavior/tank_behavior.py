"""
tank_behavior.py

Behavior model for an industrial storage tank.
"""

from __future__ import annotations

from backend.industrial.behavior.base_behavior import BaseBehavior
from backend.industrial.behavior.state_models import BehaviorState


class TankBehavior(BaseBehavior):
    """
    Controls the operating behavior of an industrial storage tank.
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

            self.machine.inflow_rate = self.approach(
                self.machine.inflow_rate,
                0,
                5,
                dt,
            )

            self.machine.outflow_rate = self.approach(
                self.machine.outflow_rate,
                0,
                5,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                25,
                0.2,
                dt,
            )

        # ==================================================
        # STARTING
        # ==================================================

        elif self.state == BehaviorState.STARTING:

            self.machine.inflow_rate = self.approach(
                self.machine.inflow_rate,
                15,
                3,
                dt,
            )

            self.machine.outflow_rate = self.approach(
                self.machine.outflow_rate,
                10,
                2,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                27,
                0.2,
                dt,
            )

            if self.time_in_state >= 5:

                self.set_state(
                    BehaviorState.NORMAL
                )

        # ==================================================
        # NORMAL
        # ==================================================

        elif self.state == BehaviorState.NORMAL:

            self.machine.inflow_rate = self.approach(
                self.machine.inflow_rate,
                25,
                2,
                dt,
            )

            self.machine.outflow_rate = self.approach(
                self.machine.outflow_rate,
                20,
                2,
                dt,
            )

            self.machine.current_level += (
                self.machine.inflow_rate
                - self.machine.outflow_rate
            ) * dt

            self.machine.current_level = max(
                0,
                min(
                    self.machine.capacity,
                    self.machine.current_level,
                ),
            )

            self.machine.level_percentage = round(
                (
                    self.machine.current_level
                    / self.machine.capacity
                )
                * 100,
                2,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                30,
                0.2,
                dt,
            )

        # ==================================================
        # HIGH LOAD
        # ==================================================

        elif self.state == BehaviorState.HIGH_LOAD:

            self.machine.inflow_rate = self.approach(
                self.machine.inflow_rate,
                60,
                3,
                dt,
            )

            self.machine.outflow_rate = self.approach(
                self.machine.outflow_rate,
                50,
                3,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                40,
                0.5,
                dt,
            )

        # ==================================================
        # FAULT
        # ==================================================

        elif self.state == BehaviorState.FAULT:

            self.machine.inflow_rate = self.approach(
                self.machine.inflow_rate,
                0,
                5,
                dt,
            )

            self.machine.outflow_rate = self.approach(
                self.machine.outflow_rate,
                0,
                5,
                dt,
            )