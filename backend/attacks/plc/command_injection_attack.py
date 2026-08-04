"""
plc_command_injection_attack.py

PLC Command Injection Attack
"""

from __future__ import annotations

from backend.attacks.plc.plc_attack import (
    PLCAttack,
)

from backend.attacks.plc.plc_state import (
    PLCState,
)


class PLCCommandInjectionAttack(PLCAttack):
    """
    Injects malicious commands into a PLC.
    """

    def __init__(
        self,
        attack_id: str = "PLC_001",
        duration: float = 20.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="PLC Command Injection",
            duration=duration,
        )

        self.injected_command = "FORCE_STOP"

    # ==========================================
    # Modify Command
    # ==========================================

    def modify_command(
        self,
        command: str,
    ) -> str:

        if self.is_running:
            return self.injected_command

        return command

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        PLCState.command_injection = True

        PLCState.injected_command = (
            self.injected_command
        )

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        PLCState.command_injection = False

        PLCState.injected_command = None

        super().stop()