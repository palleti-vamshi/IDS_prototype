"""
unauthorized_command_attack.py

Unauthorized Command Attack
"""

from __future__ import annotations

import random

from backend.attacks.plc.plc_attack import (
    PLCAttack,
)

from backend.attacks.plc.plc_state import (
    PLCState,
)


class UnauthorizedCommandAttack(PLCAttack):
    """
    Simulates execution of unauthorized PLC commands.
    """

    def __init__(
        self,
        attack_id: str = "PLC_002",
        duration: float = 20.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Unauthorized Command Attack",
            duration=duration,
        )

        self.commands = [
            "START",
            "STOP",
            "RESET",
            "EMERGENCY_STOP",
            "OVERRIDE",
        ]

    # ==========================================
    # Modify Command
    # ==========================================

    def modify_command(
        self,
        command: str,
    ) -> str:

        if self.is_running:

            return random.choice(
                self.commands
            )

        return command

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        PLCState.unauthorized_command = True

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        PLCState.unauthorized_command = False

        super().stop()