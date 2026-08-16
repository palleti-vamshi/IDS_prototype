"""
sensor_drift_attack.py

Advanced Sensor Drift Attack
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
    Simulates realistic gradual sensor drift.
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

        # ==========================================
        # Drift Parameters
        # ==========================================

        self.max_drift = 15.0

        self.current_drift = 0.0

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if not self.is_running:

            return value

        return self.drift_engine.generate(
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

        progress = min(
            self.elapsed_time / self.duration,
            1.0,
        )

        self.current_drift = round(
            progress * self.max_drift,
            2,
        )

        # ==========================================
        # Update Sensor Attack Engine
        # ==========================================

        for sensor_code in self.engine.sensor_states:

            self.engine.update_state(

                sensor_code,

                drift=self.current_drift,

                attack_name=self.attack_name,

            )

        # ==========================================
        # Compatibility Layer
        # ==========================================

        SensorState.drift = self.current_drift

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "current_drift": self.current_drift,
            }

        )

        return status

    # ==========================================
    # Stop
    # ==========================================

    def stop(
        self,
    ) -> None:

        self.current_drift = 0.0

        self.drift_engine.reset()

        SensorState.drift = 0.0

        super().stop()