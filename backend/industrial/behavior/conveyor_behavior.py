"""
conveyor_behavior.py

Behavior model for an industrial conveyor.
"""

from __future__ import annotations

from backend.industrial.behavior.base_behavior import BaseBehavior
from backend.industrial.behavior.state_models import BehaviorState


class ConveyorBehavior(BaseBehavior):
    """
    Controls the operating behavior of an industrial conveyor.
    """

    def __init__(self, machine) -> None:
        super().__init__(machine)

    def update(
        self,
        dt: float,
    ) -> None:

        self.update_time(dt)

        # ==========================================
        # STOPPED
        # ==========================================

        if self.state == BehaviorState.STOPPED:

            self.machine.belt_speed = self.approach(
                self.machine.belt_speed,
                0.0,
                1.5,
                dt,
            )

            self.machine.rpm = self.approach(
                self.machine.rpm,
                0.0,
                250,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                0.0,
                2,
                dt,
            )

            self.machine.load = 0.0

        # ==========================================
        # STARTING
        # ==========================================

        elif self.state == BehaviorState.STARTING:

            self.machine.belt_speed = self.approach(
                self.machine.belt_speed,
                1.5,
                0.3,
                dt,
            )

            self.machine.rpm = self.approach(
                self.machine.rpm,
                900,
                200,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                6.0,
                1,
                dt,
            )

            if self.time_in_state >= 5:
                self.set_state(
                    BehaviorState.NORMAL
                )

        # ==========================================
        # NORMAL
        # ==========================================

        elif self.state == BehaviorState.NORMAL:

            self.machine.belt_speed = self.approach(
                self.machine.belt_speed,
                2.5,
                0.2,
                dt,
            )

            self.machine.rpm = self.approach(
                self.machine.rpm,
                1450,
                80,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                9.5,
                0.5,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                38.0,
                0.3,
                dt,
            )

            self.machine.load = 55.0
            self.machine.power = 3.2

        # ==========================================
        # HIGH LOAD
        # ==========================================

        elif self.state == BehaviorState.HIGH_LOAD:

            self.machine.belt_speed = self.approach(
                self.machine.belt_speed,
                3.5,
                0.2,
                dt,
            )

            self.machine.rpm = self.approach(
                self.machine.rpm,
                1700,
                50,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                15.0,
                0.8,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                55.0,
                0.5,
                dt,
            )

            self.machine.load = 90.0
            self.machine.power = 5.0

        # ==========================================
        # FAULT
        # ==========================================

        elif self.state == BehaviorState.FAULT:

            self.machine.belt_speed = self.approach(
                self.machine.belt_speed,
                0.0,
                1.5,
                dt,
            )

            self.machine.rpm = self.approach(
                self.machine.rpm,
                0.0,
                250,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                0.0,
                2,
                dt,
            )

            self.machine.power = self.approach(
                self.machine.power,
                0.0,
                2,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                25.0,
                0.4,
                dt,
            )

            self.machine.load = self.approach(
                self.machine.load,
                0.0,
                5,
                dt,
            )

        # ==========================================
        # Machine Health
        # ==========================================

        if self.state == BehaviorState.NORMAL:

            self.machine.health = max(
                0.0,
                self.machine.health - (0.002 * dt),
            )

        elif self.state == BehaviorState.HIGH_LOAD:

            self.machine.health = max(
                0.0,
                self.machine.health - (0.01 * dt),
            )

        # ==========================================
        # Automatic Fault Detection
        # ==========================================

        if (
            self.machine.temperature >= 90
            or self.machine.current >= 25
            or self.machine.health <= 15
        ):

            self.set_state(
                BehaviorState.FAULT
            )

        # ==========================================
        # Runtime
        # ==========================================

        self.machine.runtime_hours += (
            dt / 3600
        )

        # ==========================================
        # Safety Limits
        # ==========================================

        self.machine.belt_speed = min(
            self.machine.belt_speed,
            5.0,
        )

        self.machine.rpm = min(
            self.machine.rpm,
            2000,
        )

        self.machine.current = min(
            self.machine.current,
            30,
        )

        self.machine.temperature = min(
            self.machine.temperature,
            120,
        )

        self.machine.load = min(
            self.machine.load,
            100,
        )