"""
intermittent_attack.py

Intermittent Attack
"""

from __future__ import annotations

import random

from backend.attacks.stealth.stealth_attack import (
    StealthAttack,
)

from backend.attacks.stealth.stealth_state import (
    StealthState,
)


class IntermittentAttack(StealthAttack):
    """
    Activates malicious behavior only
    during random intervals.
    """

    def __init__(
        self,
        attack_id: str = "STL_002",
        duration: float = 60.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Intermittent Attack",
            duration=duration,
        )

        self.attack_probability = 0.3

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if (
            self.is_running
            and random.random()
            < self.attack_probability
        ):

            return round(
                value * 1.25,
                2,
            )

        return value

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        StealthState.intermittent = True

        StealthState.attack_probability = (
            self.attack_probability
        )

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        StealthState.intermittent = False

        StealthState.attack_probability = 0.0

        super().stop()