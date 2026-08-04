"""
hybrid_scenarios.py

Hybrid attack scenarios for LightX-IDS.
"""

from __future__ import annotations

from backend.attacks.scenarios.scenario import (
    AttackScenario,
)


class HybridScenario(AttackScenario):
    """
    Hybrid cyber attack scenario.

    Combines attacks from multiple layers
    to simulate a coordinated intrusion.
    """

    def __init__(
        self,
        dos_attack,
        spoof_attack,
        command_injection_attack,
        motor_overload_attack,
        drift_attack,
    ) -> None:

        super().__init__(
            "hybrid"
        )

        self.dos_attack = dos_attack

        self.spoof_attack = spoof_attack

        self.command_injection_attack = (
            command_injection_attack
        )

        self.motor_overload_attack = (
            motor_overload_attack
        )

        self.drift_attack = drift_attack

    # ==========================================
    # Build Scenario
    # ==========================================

    def build(self) -> None:

        self.events.clear()

        self.add_attack(
            self.dos_attack,
            10.0,
        )

        self.add_attack(
            self.spoof_attack,
            30.0,
        )

        self.add_attack(
            self.command_injection_attack,
            60.0,
        )

        self.add_attack(
            self.motor_overload_attack,
            90.0,
        )

        self.add_attack(
            self.drift_attack,
            120.0,
        )