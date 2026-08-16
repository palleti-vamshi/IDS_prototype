"""
false_data_injection_attack.py

Advanced False Data Injection Attack
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
    Injects gradually increasing false data into
    legitimate sensor readings.
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

        # ==========================================
        # False Data Parameters
        # ==========================================

        self.current_offset = 0.0

        self.max_offset = 30.0

        self.random_noise = 0.5

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if not self.is_running:

            return value

        modified = (

            value

            + self.current_offset

            + random.uniform(
                -self.random_noise,
                self.random_noise,
            )

        )

        return round(
            modified,
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

        progress = min(
            self.elapsed_time / self.duration,
            1.0,
        )

        self.current_offset = round(
            progress * self.max_offset,
            2,
        )

        # ==========================================
        # Update Sensor Attack Engine
        # ==========================================

        for sensor_code in self.engine.sensor_states:

            self.engine.update_state(

                sensor_code,

                false_data=True,

                attack_name=self.attack_name,

            )

        # ==========================================
        # Compatibility Layer
        # ==========================================

        SensorState.false_data = True

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "current_offset":
                    self.current_offset,
            }

        )

        return status

    # ==========================================
    # Stop
    # ==========================================

    def stop(
        self,
    ) -> None:

        self.current_offset = 0.0

        SensorState.false_data = False

        super().stop()