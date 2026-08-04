"""
process_attack.py

Base class for industrial process attacks.
"""

from __future__ import annotations

from abc import ABC

from backend.attacks.base_attack import BaseAttack
from backend.attacks.attack_target import AttackTarget
from backend.attacks.attack_type import AttackType


class ProcessAttack(BaseAttack, ABC):
    """
    Base class for industrial process attacks.
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
            attack_type=AttackType.PROCESS,
            attack_target=AttackTarget.PROCESS,
            duration=duration,
        )