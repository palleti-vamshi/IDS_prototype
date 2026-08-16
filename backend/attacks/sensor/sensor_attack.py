"""
sensor_attack.py

Base class for all sensor-based cyber attacks.
"""

from __future__ import annotations

from abc import ABC

from backend.attacks.base_attack import BaseAttack
from backend.attacks.attack_target import AttackTarget
from backend.attacks.attack_type import AttackType

from backend.attacks.sensor.sensor_attack_engine import (
    SensorAttackEngine,
)

from backend.attacks.sensor.spoof_engine import (
    SpoofEngine,
)

from backend.attacks.sensor.drift_engine import (
    DriftEngine,
)

from backend.attacks.sensor.noise_engine import (
    NoiseEngine,
)


class SensorAttack(BaseAttack, ABC):
    """
    Base class for all sensor attacks.
    """

    # ==========================================
    # Shared Engine
    # ==========================================

    attack_engine = SensorAttackEngine()

    def __init__(
        self,
        attack_id: str,
        attack_name: str,
        duration: float = 30.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name=attack_name,
            attack_type=AttackType.SENSOR,
            attack_target=AttackTarget.SENSOR,
            duration=duration,
        )

        self.engine = SensorAttack.attack_engine

        self.spoof_engine = SpoofEngine()

        self.drift_engine = DriftEngine()

        self.noise_engine = NoiseEngine()

    # ==========================================
    # Registration
    # ==========================================

    def register_sensor(
        self,
        sensor_code: str,
    ) -> None:

        self.engine.register_sensor(
            sensor_code
        )

    # ==========================================
    # Runtime
    # ==========================================

    def update_engines(
        self,
    ) -> None:

        progress = min(
            self.elapsed_time / self.duration,
            1.0,
        )

        self.spoof_engine.update(
            progress
        )

        self.drift_engine.update(
            progress
        )

        self.noise_engine.update(
            progress
        )

    # ==========================================
    # Stop
    # ==========================================

    def stop(
        self,
    ) -> None:
        """
        Stop the sensor attack and clear all
        per-sensor attack states.

        This prevents completed sensor attacks
        from leaving stale spoof, drift, noise,
        freeze, or false-data states active.
        """

        # ------------------------------------------
        # Reset shared per-sensor attack state
        # ------------------------------------------

        self.engine.reset_all()

        # ------------------------------------------
        # Reset local attack engines
        # ------------------------------------------

        self.spoof_engine.reset()

        self.drift_engine.reset()

        self.noise_engine.reset()

        # ------------------------------------------
        # Complete BaseAttack lifecycle
        # ------------------------------------------

        super().stop()

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(
            {
                "registered_sensors":
                    self.engine.total_registered,

                "spoof_engine":
                    self.spoof_engine.get_status(),

                "drift_engine":
                    self.drift_engine.get_status(),

                "noise_engine":
                    self.noise_engine.get_status(),
            }
        )

        return status