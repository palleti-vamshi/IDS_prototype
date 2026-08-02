"""
motor_behavior.py

Behavior model for an industrial electric motor.
"""

from __future__ import annotations

from backend.industrial.behavior.base_behavior import BaseBehavior
from backend.industrial.behavior.state_models import BehaviorState


class MotorBehavior(BaseBehavior):
    """
    Controls the operating behavior of an industrial motor.
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

            self.machine.rpm = self.approach(
                self.machine.rpm,
                0,
                350,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                0,
                4,
                dt,
            )

            self.machine.power = self.approach(
                self.machine.power,
                0,
                2,
                dt,
            )

            self.machine.load = self.approach(
                self.machine.load,
                0,
                20,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                25,
                0.5,
                dt,
            )

            self.machine.vibration = self.approach(
                self.machine.vibration,
                0.05,
                0.05,
                dt,
            )

        # ==================================================
        # STARTING
        # ==================================================

        elif self.state == BehaviorState.STARTING:

            self.machine.rpm = self.approach(
                self.machine.rpm,
                900,
                250,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                8,
                2,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                30,
                0.4,
                dt,
            )

            self.machine.vibration = self.approach(
                self.machine.vibration,
                0.15,
                0.03,
                dt,
            )

            if self.time_in_state >= 5:

                self.set_state(
                    BehaviorState.WARMUP
                )

        # ==================================================
        # WARMUP
        # ==================================================

        elif self.state == BehaviorState.WARMUP:

            self.machine.rpm = self.approach(
                self.machine.rpm,
                1450,
                120,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                10,
                1,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                38,
                0.3,
                dt,
            )

            self.machine.power = self.approach(
                self.machine.power,
                3.0,
                0.4,
                dt,
            )

            self.machine.vibration = self.approach(
                self.machine.vibration,
                0.20,
                0.02,
                dt,
            )

            if self.time_in_state >= 10:

                self.set_state(
                    BehaviorState.NORMAL
                )

        # ==================================================
        # NORMAL
        # ==================================================

        elif self.state == BehaviorState.NORMAL:

            self.machine.load = self.approach(
                self.machine.load,
                50,
                5,
                dt,
            )

            self.machine.rpm = self.approach(
                self.machine.rpm,
                1450,
                50,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                10.5,
                0.5,
                dt,
            )

            self.machine.power = self.approach(
                self.machine.power,
                3.8,
                0.3,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                42,
                0.2,
                dt,
            )

            self.machine.vibration = self.approach(
                self.machine.vibration,
                0.25,
                0.02,
                dt,
            )

        # ==================================================
        # HIGH LOAD
        # ==================================================

        elif self.state == BehaviorState.HIGH_LOAD:

            self.machine.load = self.approach(
                self.machine.load,
                85,
                8,
                dt,
            )

            self.machine.rpm = self.approach(
                self.machine.rpm,
                1700,
                80,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                16,
                1,
                dt,
            )

            self.machine.power = self.approach(
                self.machine.power,
                5.5,
                0.5,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                60,
                0.5,
                dt,
            )

            self.machine.vibration = self.approach(
                self.machine.vibration,
                0.45,
                0.03,
                dt,
            )

        # ==================================================
        # OVERLOADED
        # ==================================================

        elif self.state == BehaviorState.OVERLOADED:

            self.machine.load = self.approach(
                self.machine.load,
                100,
                10,
                dt,
            )

            self.machine.rpm = self.approach(
                self.machine.rpm,
                1825,
                60,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                22,
                1,
                dt,
            )

            self.machine.power = self.approach(
                self.machine.power,
                7.2,
                0.6,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                80,
                0.7,
                dt,
            )

            self.machine.vibration = self.approach(
                self.machine.vibration,
                0.80,
                0.04,
                dt,
            )

        # ==================================================
        # FAULT
        # ==================================================

        elif self.state == BehaviorState.FAULT:

            self.machine.rpm = self.approach(
                self.machine.rpm,
                0,
                400,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                0,
                3,
                dt,
            )

            self.machine.power = self.approach(
                self.machine.power,
                0,
                1,
                dt,
            )

            self.machine.load = self.approach(
                self.machine.load,
                0,
                10,
                dt,
            )

            self.machine.vibration = self.approach(
                self.machine.vibration,
                0.05,
                0.05,
                dt,
            )