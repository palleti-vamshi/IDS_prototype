"""
stealth_attack.py

Base class for stealth cyber attacks.
"""

from __future__ import annotations

from abc import ABC

from backend.attacks.base_attack import BaseAttack
from backend.attacks.attack_target import AttackTarget
from backend.attacks.attack_type import AttackType

from backend.attacks.stealth.stealth_attack_engine import (
    StealthAttackEngine,
)


class StealthAttack(BaseAttack, ABC):
    """
    Base class for stealth attacks.
    """

    attack_engine = StealthAttackEngine()

    def __init__(
        self,
        attack_id: str,
        attack_name: str,
        duration: float = 30.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name=attack_name,
            attack_type=AttackType.STEALTH,
            attack_target=AttackTarget.PROCESS,
            duration=duration,
        )

        self.engine = StealthAttack.attack_engine

    def get_status(self) -> dict:

        status = super().get_status()

        status.update(

            {
                "stealth_engine":
                    self.engine.get_state(),
            }

        )

        return status