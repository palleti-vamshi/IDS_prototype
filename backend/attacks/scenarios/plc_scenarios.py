"""
plc_scenarios.py

PLC attack scenarios for LightX-IDS.
"""

from __future__ import annotations

from backend.attacks.scenarios.scenario import (
    AttackScenario,
)


class PLCScenario(AttackScenario):
    """
    Standard PLC attack scenario.
    """

    def __init__(
        self,
        command_injection_attack,
        unauthorized_command_attack,
        setpoint_manipulation_attack,
    ) -> None:

        super().__init__(
            "plc"
        )

        self.command_injection_attack = (
            command_injection_attack
        )

        self.unauthorized_command_attack = (
            unauthorized_command_attack
        )

        self.setpoint_manipulation_attack = (
            setpoint_manipulation_attack
        )

    # ==========================================
    # Build Scenario
    # ==========================================

    def build(self) -> None:

        self.events.clear()

        self.add_attack(
            self.command_injection_attack,
            10.0,
        )

        self.add_attack(
            self.unauthorized_command_attack,
            40.0,
        )

        self.add_attack(
            self.setpoint_manipulation_attack,
            70.0,
        )