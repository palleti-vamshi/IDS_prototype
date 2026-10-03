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
    using the shared SpoofEngine and targets
    specific industrial sensors.
    """

    DEFAULT_TARGET: str = "MTR-001-TMP"

    def __init__(
        self,
        attack_id: str = "SNS_001",
        duration: float = 20.0,
        target_sensor: str | None = None,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Sensor Spoofing Attack",
            duration=duration,
        )

        # ==========================================
        # Targets
        # ==========================================

        if target_sensor:
            self.add_target(target_sensor)

        # ==========================================
        # Spoof Parameters
        # ==========================================

        self.max_offset = 20.0

        self.current_offset = 0.0

    # ==========================================
    # Target Resolution
    # ==========================================

    @property
    def target_sensor(self) -> str:
        """
        Primary target sensor code.
        """
        return self.active_targets[0]

    @property
    def active_targets(self) -> list[str]:
        """
        Return the list of targeted sensor codes.
        If no targets were explicitly added, falls back
        to the single deterministic default target.
        """
        if self.targets:
            return list(self.targets)
        return [self.DEFAULT_TARGET]

    # ==========================================
    # Lifecycle
    # ==========================================

    def start(self) -> None:
        """
        Start attack. Ensures a deterministic target
        is registered if none was provided.
        """
        if not self.targets:
            self.add_target(self.DEFAULT_TARGET)

        super().start()

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
        # Update Sensor Attack Engine for TARGETS ONLY
        # ==========================================

        for sensor_code in self.active_targets:

            self.engine.update_state(
                sensor_code,
                spoof=True,
                spoof_offset=self.current_offset,
                attack_name=self.attack_name,
            )

        # ==========================================
        # Global Compatibility Layer
        # Ensure global spoofing flag is NEVER set,
        # preventing unintended side effects across
        # non-targeted sensors in the factory.
        # ==========================================

        SensorState.spoofing = False

        SensorState.spoof_value = None

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
                "target_sensor": self.target_sensor,
                "target_sensors": self.active_targets,
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

        # ==========================================
        # Reset targeted sensor state in attack engine
        # ==========================================

        for sensor_code in self.active_targets:
            self.engine.reset_sensor(sensor_code)

        # Ensure global spoofing state is inactive
        SensorState.spoofing = False

        SensorState.spoof_value = None

        super().stop()