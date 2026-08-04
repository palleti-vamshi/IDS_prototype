"""
sensor_attack.py

Base class for all sensor-based cyber attacks.
"""

from __future__ import annotations

from abc import ABC

from backend.attacks.base_attack import BaseAttack
from backend.attacks.attack_target import AttackTarget
from backend.attacks.attack_type import AttackType


class SensorAttack(BaseAttack, ABC):
    """
    Base class for sensor attacks.
    """

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