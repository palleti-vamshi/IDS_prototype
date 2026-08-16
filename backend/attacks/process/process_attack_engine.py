"""
process_attack_engine.py

Shared Process Attack Engine.
"""

from __future__ import annotations


class ProcessAttackEngine:
    """
    Shared engine for all industrial
    process attacks.
    """

    def __init__(self) -> None:

        self.state = {

            "motor_overload": False,

            "overload_factor": 1.5,

            "valve_stuck": False,

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

            "motor_overload": False,

            "overload_factor": 1.5,

            "valve_stuck": False,

            "attack_name": None,

        }

    # ==========================================
    # Access
    # ==========================================

    def get_state(
        self,
    ) -> dict:

        return self.state