"""
compressor_behavior.py

Behavior model for an industrial air compressor.
"""

from __future__ import annotations

from backend.industrial.behavior.base_behavior import BaseBehavior
from backend.industrial.behavior.state_models import BehaviorState


class CompressorBehavior(BaseBehavior):
    """
    Controls the operating behavior of an industrial compressor.
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

            self.machine.current = self.approach(
                self.machine.current,
                0.0,
                3,
                dt,
            )

            self.machine.air_flow = self.approach(
                self.machine.air_flow,
                0.0,
                20,
                dt,
            )

            self.machine.load = 0.0

        # ==========================================
        # STARTING
        # ==========================================

        elif self.state == BehaviorState.STARTING:

            self.machine.current = self.approach(
                self.machine.current,
                8.0,
                2,
                dt,
            )

            self.machine.air_flow = self.approach(
                self.machine.air_flow,
                80.0,
                15,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                130.0,
                4,
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

            self.machine.current = self.approach(
                self.machine.current,
                12.0,
                1,
                dt,
            )

            self.machine.air_flow = self.approach(
                self.machine.air_flow,
                120.0,
                5,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                170.0,
                2,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                45.0,
                0.4,
                dt,
            )

            self.machine.power = 4.5
            self.machine.load = 55.0

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

            self.machine.current = self.approach(
                self.machine.current,
                18.0,
                1,
                dt,
            )

            self.machine.air_flow = self.approach(
                self.machine.air_flow,
                170.0,
                4,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                220.0,
                2,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                65.0,
                0.5,
                dt,
            )

            self.machine.power = 6.5
            self.machine.load = 90.0

            # ==========================================
            # Accelerated Wear
            # ==========================================

            self.machine.health = max(
                0.0,
                self.machine.health - (0.012 * dt),
            )

        # ==========================================
        # FAULT
        # ==========================================

        elif self.state == BehaviorState.FAULT:

            self.machine.current = self.approach(
                self.machine.current,
                0.0,
                3,
                dt,
            )

            self.machine.air_flow = self.approach(
                self.machine.air_flow,
                0.0,
                20,
                dt,
            )

            self.machine.power = self.approach(
                self.machine.power,
                0.0,
                2,
                dt,
            )

            self.machine.pressure = self.approach(
                self.machine.pressure,
                100.0,
                4,
                dt,
            )

            self.machine.temperature = self.approach(
                self.machine.temperature,
                30.0,
                0.5,
                dt,
            )

            self.machine.load = self.approach(
                self.machine.load,
                0.0,
                5,
                dt,
            )

        # ==========================================
        # Automatic Fault Detection
        # ==========================================

        if (

            self.machine.pressure >= 250

            or self.machine.temperature >= 95

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

        self.machine.air_flow = min(
            self.machine.air_flow,
            200,
        )

        self.machine.pressure = min(
            self.machine.pressure,
            280,
        )

        self.machine.current = min(
            self.machine.current,
            40,
        )

        self.machine.temperature = min(
            self.machine.temperature,
            120,
        )