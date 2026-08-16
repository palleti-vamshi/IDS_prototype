"""
sensor_freeze_attack.py

Advanced Sensor Freeze Attack
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
    Freezes sensor readings at the last observed
    value while maintaining attack state.
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

        return round(
            self.frozen_value,
            2,
        )

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        self.update_engines()

        for sensor_code in self.engine.sensor_states:

            self.engine.update_state(

                sensor_code,

                freeze=True,

                attack_name=self.attack_name,

            )

        # Compatibility Layer (temporary)
        SensorState.freeze = True

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "frozen_value":
                    self.frozen_value,
            }

        )

        return status

    # ==========================================
    # Stop
    # ==========================================

    def stop(
        self,
    ) -> None:

        self.frozen_value = None

        SensorState.freeze = False

        super().stop()