"""
sensor_noise_injection_attack.py

Sensor Noise Injection Attack
"""

from __future__ import annotations

import random

from backend.attacks.sensor.sensor_attack import (
    SensorAttack,
)

from backend.attacks.sensor.sensor_state import (
    SensorState,
)


class SensorNoiseInjectionAttack(SensorAttack):
    """
    Injects random noise into sensor readings.
    """

    def __init__(
        self,
        attack_id: str = "SNS_005",
        duration: float = 20.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Sensor Noise Injection Attack",
            duration=duration,
        )

        self.noise_level = 5.0

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if self.is_running:

            noise = random.uniform(
                -self.noise_level,
                self.noise_level,
            )

            return round(
                value + noise,
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

        SensorState.noise = self.noise_level

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        SensorState.noise = 0.0

        super().stop()