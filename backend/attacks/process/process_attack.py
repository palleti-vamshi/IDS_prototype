"""
process_attack.py

Base class for industrial process attacks.
"""

from __future__ import annotations

from abc import ABC

from backend.attacks.base_attack import BaseAttack
from backend.attacks.attack_target import AttackTarget
from backend.attacks.attack_type import AttackType

from backend.attacks.process.process_attack_engine import (
    ProcessAttackEngine,
)


class ProcessAttack(BaseAttack, ABC):
    """
    Base class for industrial process attacks.

    Every process attack shares one attack engine.
    """

    # ==========================================
    # Shared Process Engine
    # ==========================================

    attack_engine = ProcessAttackEngine()

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

        self.engine = ProcessAttack.attack_engine

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "process_engine":
                    self.engine.get_state(),
            }

        )

        return status