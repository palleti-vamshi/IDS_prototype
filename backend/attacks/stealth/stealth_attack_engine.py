"""
stealth_attack_engine.py

Shared Stealth Attack Engine.
"""

from __future__ import annotations


class StealthAttackEngine:
    """
    Shared engine for stealth attacks.
    """

    def __init__(self) -> None:

        self.state = {

            "slow_drift": False,

            "drift_rate": 0.0,

            "intermittent": False,

            "attack_probability": 0.0,

            "attack_name": None,

        }

    # ==========================================
    # Update
    # ==========================================

    def update(
        self,
        **kwargs,
    ) -> None:

        self.state.update(kwargs)

    # ==========================================
    # Reset
    # ==========================================

    def reset(
        self,
    ) -> None:

        self.state = {

            "slow_drift": False,

            "drift_rate": 0.0,

            "intermittent": False,

            "attack_probability": 0.0,

            "attack_name": None,

        }

    # ==========================================
    # Access
    # ==========================================

    def get_state(
        self,
    ) -> dict:

        return self.state