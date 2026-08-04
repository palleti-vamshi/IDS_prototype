"""
sensor_freeze_attack.py

Sensor Freeze Attack
"""

from __future__ import annotations

from backend.attacks.sensor.sensor_attack import (
    SensorAttack,
)

from backend.attacks.sensor.sensor_state import (
    SensorState,
)


class SensorFreezeAttack(SensorAttack):
    """
    Freezes a sensor at its last observed value.
    """

    def __init__(
        self,
        attack_id: str = "SNS_004",
        duration: float = 20.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Sensor Freeze Attack",
            duration=duration,
        )

        self.frozen_value = None

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if not self.is_running:
            return value

        if self.frozen_value is None:
            self.frozen_value = value

        return self.frozen_value

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        SensorState.freeze = True

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        SensorState.freeze = False

        self.frozen_value = None

        super().stop()