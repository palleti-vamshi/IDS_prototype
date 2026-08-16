"""
pump_behavior.py

Behavior model for an industrial pump.
"""

from __future__ import annotations

from backend.industrial.behavior.base_behavior import BaseBehavior
from backend.industrial.behavior.state_models import BehaviorState


class PumpBehavior(BaseBehavior):
    """
    Controls the operating behavior of an industrial pump.
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

            self.machine.flow_rate = self.approach(
                self.machine.flow_rate,
                0.0,
                20,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                0.0,
                5,
                dt,
            )

        # ==========================================
        # STARTING
        # ==========================================

        elif self.state == BehaviorState.STARTING:

            self.machine.flow_rate = self.approach(
                self.machine.flow_rate,
                40,
                15,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                6,
                2,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                120,
                5,
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

            self.machine.flow_rate = self.approach(
                self.machine.flow_rate,
                75,
                5,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                10,
                1,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                150,
                3,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                42,
                0.5,
                dt,
            )

            self.machine.load = 50

            self.machine.power = 3.5

            # ==========================================
            # Machine Health
            # ==========================================

            self.machine.health = max(
                0.0,
                self.machine.health - (0.002 * dt),
            )

        # ==========================================
        # HIGH LOAD
        # ==========================================

        elif self.state == BehaviorState.HIGH_LOAD:

            self.machine.flow_rate = self.approach(
                self.machine.flow_rate,
                100,
                3,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                16,
                1,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                190,
                2,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                60,
                0.5,
                dt,
            )

            self.machine.load = 90

            self.machine.power = 5.2

            # ==========================================
            # Accelerated Wear
            # ==========================================

            self.machine.health = max(
                0.0,
                self.machine.health - (0.01 * dt),
            )

        # ==========================================
        # FAULT
        # ==========================================

        elif self.state == BehaviorState.FAULT:

            self.machine.flow_rate = self.approach(
                self.machine.flow_rate,
                0.0,
                20,
                dt,
            )

            self.machine.current = self.approach(
                self.machine.current,
                0.0,
                5,
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
                30,
                0.5,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                0,
                5,
                dt,
            )

        # ==========================================
        # Automatic Fault Detection
        # ==========================================

        if (
            self.machine.temperature >= 90
            or self.machine.pressure >= 220
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

        self.machine.flow_rate = min(
            self.machine.flow_rate,
            120,
        )

        self.machine.pressure = min(
            self.machine.pressure,
            250,
        )

        self.machine.current = min(
            self.machine.current,
            35,
        )

        self.machine.temperature = min(
            self.machine.temperature,
            120,
        )