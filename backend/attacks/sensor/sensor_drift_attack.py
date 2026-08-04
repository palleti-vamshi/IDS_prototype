"""
sensor_drift_attack.py

Sensor Drift Attack
"""

from __future__ import annotations

from backend.attacks.sensor.sensor_attack import (
    SensorAttack,
)

from backend.attacks.sensor.sensor_state import (
    SensorState,
)


class SensorDriftAttack(SensorAttack):
    """
    Gradually shifts sensor values over time.
    """

    def __init__(
        self,
        attack_id: str = "SNS_003",
        duration: float = 30.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Sensor Drift Attack",
            duration=duration,
        )

        self.max_drift = 20.0

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if self.is_running:

            progress = min(
                self.elapsed_time / self.duration,
                1.0,
            )

            drift = progress * self.max_drift

            return round(
                value + drift,
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

        progress = min(
            self.elapsed_time / self.duration,
            1.0,
        )

        SensorState.drift = (
            progress * self.max_drift
        )

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        SensorState.drift = 0.0

        super().stop()