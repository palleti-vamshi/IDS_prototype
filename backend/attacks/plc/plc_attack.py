"""
plc_attack.py

Base class for PLC cyber attacks.
"""

from __future__ import annotations

from abc import ABC

from backend.attacks.base_attack import BaseAttack
from backend.attacks.attack_target import AttackTarget
from backend.attacks.attack_type import AttackType

from backend.attacks.plc.plc_attack_engine import (
    PLCAttackEngine,
)


class PLCAttack(BaseAttack, ABC):
    """
    Base class for all PLC attacks.

    Every PLC attack shares one attack engine.
    """

    # ==========================================
    # Shared PLC Engine
    # ==========================================

    attack_engine = PLCAttackEngine()

    def __init__(
        self,
        attack_id: str,
        attack_name: str,
        duration: float = 30.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name=attack_name,
            attack_type=AttackType.PLC,
            attack_target=AttackTarget.PLC,
            duration=duration,
        )

        self.engine = PLCAttack.attack_engine

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "plc_engine":
                    self.engine.get_state(),
            }

        )

        return status