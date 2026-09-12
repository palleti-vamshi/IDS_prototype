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
    Injects realistic sensor-specific measurement noise.

    Noise is assigned independently to each registered sensor
    using the sensor-code suffix.

    The attack preserves the existing SensorAttackEngine
    architecture and stores noise in each sensor's state.
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
        # Base Noise Parameters
        # ==========================================

        # Maximum absolute noise used by each sensor
        # type during the attack.
        #
        # These are simulation parameters, not universal
        # real-world sensor specifications.
        self.noise_profile = {

            # Motor sensors
            "TMP": 0.75,
            "CUR": 0.30,
            "RPM": 3.00,
            "VIB": 0.08,
            "VLT": 1.50,

            # Pump / valve / compressor sensors
            "PRS": 1.50,
            "FLW": 1.00,

            # Tank sensors
            "LVL": 0.75,
            "HUM": 1.00,

            # Conveyor proximity sensor
            "PRX": 3.00,
        }

        # Backward-compatible public attribute.
        self.noise_level = 0.0

    # ==========================================
    # Sensor Noise Profile
    # ==========================================

    def get_sensor_noise(
        self,
        sensor_code: str,
    ) -> float:
        """
        Return the configured maximum noise magnitude
        for a sensor based on its sensor-code suffix.
        """

        suffix = sensor_code.rsplit(
            "-",
            1,
        )[-1].upper()

        return self.noise_profile.get(
            suffix,
            1.0,
        )

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

        progress = min(
            self.elapsed_time / self.duration,
            1.0,
        )

        for sensor_code in self.engine.sensor_states:

            maximum_noise = self.get_sensor_noise(
                sensor_code
            )

            # Gradually increase the attack strength
            # throughout the attack duration.
            current_noise = round(
                maximum_noise * progress,
                4,
            )

            self.engine.update_state(

                sensor_code,

                noise=current_noise,

                attack_name=self.attack_name,

            )

        # ==========================================
        # Compatibility Layer
        # ==========================================
        #
        # The active attack uses per-sensor state.
        # The global compatibility value remains
        # disabled so it cannot override the
        # sensor-specific profile.

        SensorState.noise = 0.0

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

                "noise_profile":
                    self.noise_profile.copy(),
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