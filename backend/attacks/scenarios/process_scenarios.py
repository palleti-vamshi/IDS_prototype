"""
process_scenarios.py

Process attack scenarios for LightX-IDS.
"""

from __future__ import annotations

from backend.attacks.scenarios.scenario import (
    AttackScenario,
)


class ProcessScenario(AttackScenario):
    """
    Standard process attack scenario.
    """

    def __init__(
        self,
        motor_overload_attack,
        valve_stuck_attack,
    ) -> None:

        super().__init__(
            "process"
        )

        self.motor_overload_attack = (
            motor_overload_attack
        )

        self.valve_stuck_attack = (
            valve_stuck_attack
        )

    # ==========================================
    # Build Scenario
    # ==========================================

    def build(self) -> None:

        self.events.clear()

        self.add_attack(
            self.motor_overload_attack,
            10.0,
        )

        self.add_attack(
            self.valve_stuck_attack,
            50.0,
        )