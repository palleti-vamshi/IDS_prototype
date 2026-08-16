"""
sensor_spoofing_attack.py

Advanced Sensor Spoofing Attack
"""

from __future__ import annotations

from backend.attacks.sensor.sensor_attack import (
    SensorAttack,
)

from backend.attacks.sensor.sensor_state import (
    SensorState,
)


class SensorSpoofingAttack(SensorAttack):
    """
    Generates realistic spoofed sensor values
    using the shared SpoofEngine.
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

        # ==========================================
        # Spoof Parameters
        # ==========================================

        self.max_offset = 20.0

        self.current_offset = 0.0

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if not self.is_running:

            return value

        return self.spoof_engine.generate(
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

                spoof=True,

                spoof_offset=self.current_offset,

                attack_name=self.attack_name,

            )

        # ==========================================
        # Compatibility Layer
        # ==========================================

        SensorState.spoofing = True

        SensorState.spoof_value = self.modify_value(
            0.0
        )

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "spoof_offset": self.current_offset,
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

        self.spoof_engine.reset()

        SensorState.spoofing = False

        SensorState.spoof_value = None

        super().stop()