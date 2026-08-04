"""
sensor_scenarios.py

Sensor attack scenarios for LightX-IDS.
"""

from __future__ import annotations

from backend.attacks.scenarios.scenario import (
    AttackScenario,
)


class SensorScenario(AttackScenario):
    """
    Standard sensor attack scenario.
    """

    def __init__(
        self,
        spoof_attack,
        false_data_attack,
        drift_attack,
        freeze_attack,
        noise_attack,
    ) -> None:

        super().__init__(
            "sensor"
        )

        self.spoof_attack = spoof_attack
        self.false_data_attack = false_data_attack
        self.drift_attack = drift_attack
        self.freeze_attack = freeze_attack
        self.noise_attack = noise_attack

    # ==========================================
    # Build Scenario
    # ==========================================

    def build(self) -> None:

        self.events.clear()

        self.add_attack(
            self.spoof_attack,
            10.0,
        )

        self.add_attack(
            self.false_data_attack,
            40.0,
        )

        self.add_attack(
            self.drift_attack,
            70.0,
        )

        self.add_attack(
            self.freeze_attack,
            100.0,
        )

        self.add_attack(
            self.noise_attack,
            130.0,
        )