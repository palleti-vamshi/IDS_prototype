"""
plc_attack_engine.py

Shared PLC attack engine.
"""

from __future__ import annotations


class PLCAttackEngine:
    """
    Central engine maintaining PLC attack state.
    """

    def __init__(self) -> None:

        self.state = {

            "command_injection": False,

            "injected_command": None,

            "unauthorized_command": False,

            "unauthorized_value": None,

            "setpoint_offset": 0.0,

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

    def reset(self) -> None:

        self.state = {

            "command_injection": False,

            "injected_command": None,

            "unauthorized_command": False,

            "unauthorized_value": None,

            "setpoint_offset": 0.0,

            "attack_name": None,

        }

    # ==========================================
    # Access
    # ==========================================

    def get_state(self) -> dict:

        return self.state