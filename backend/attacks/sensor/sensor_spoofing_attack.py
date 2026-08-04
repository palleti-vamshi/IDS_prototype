"""
sensor_spoofing_attack.py

Sensor Spoofing Attack
"""

from __future__ import annotations

import random

from backend.attacks.sensor.sensor_attack import (
    SensorAttack,
)

from backend.attacks.sensor.sensor_state import (
    SensorState,
)


class SensorSpoofingAttack(SensorAttack):
    """
    Replaces genuine sensor values with
    attacker-generated fake values.
    """

    def __init__(
        self,
        attack_id: str = "SNS_001",
        duration: float = 20.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Sensor Spoofing Attack",
            duration=duration,
        )

        self.min_value = 0.0

        self.max_value = 100.0

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if self.is_running:

            return round(
                random.uniform(
                    self.min_value,
                    self.max_value,
                ),
                2,
            )

        return value

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        SensorState.spoofing = True

        SensorState.spoof_value = round(
            random.uniform(
                self.min_value,
                self.max_value,
            ),
            2,
        )

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        SensorState.spoofing = False

        SensorState.spoof_value = None

        super().stop()