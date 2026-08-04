"""
false_data_injection_attack.py

False Data Injection Attack
"""

from __future__ import annotations

import random

from backend.attacks.sensor.sensor_attack import (
    SensorAttack,
)

from backend.attacks.sensor.sensor_state import (
    SensorState,
)


class FalseDataInjectionAttack(SensorAttack):
    """
    Injects malicious offsets into legitimate
    sensor readings.
    """

    def __init__(
        self,
        attack_id: str = "SNS_002",
        duration: float = 20.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="False Data Injection Attack",
            duration=duration,
        )

        self.max_offset = 50.0

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if self.is_running:

            offset = random.uniform(
                -self.max_offset,
                self.max_offset,
            )

            return round(
                value + offset,
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

        SensorState.false_data = True

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        SensorState.false_data = False

        super().stop()