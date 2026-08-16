"""
sensor_noise_injection_attack.py

Advanced Sensor Noise Injection Attack
"""

from __future__ import annotations

from backend.attacks.sensor.sensor_attack import (
    SensorAttack,
)

from backend.attacks.sensor.sensor_state import (
    SensorState,
)


class SensorNoiseInjectionAttack(SensorAttack):
    """
    Injects realistic measurement noise into
    sensor readings.
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

        # ==========================================
        # Noise Parameters
        # ==========================================

        self.noise_level = 2.5

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if not self.is_running:

            return value

        return self.noise_engine.generate(
            value
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

                noise=self.noise_level,

                attack_name=self.attack_name,

            )

        # ==========================================
        # Compatibility Layer
        # ==========================================

        SensorState.noise = self.noise_level

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "noise_level": self.noise_level,
            }

        )

        return status

    # ==========================================
    # Stop
    # ==========================================

    def stop(
        self,
    ) -> None:

        self.noise_level = 0.0

        self.noise_engine.reset()

        SensorState.noise = 0.0

        super().stop()