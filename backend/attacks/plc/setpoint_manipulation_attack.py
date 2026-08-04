"""
setpoint_manipulation_attack.py

Setpoint Manipulation Attack
"""

from __future__ import annotations

from backend.attacks.plc.plc_attack import (
    PLCAttack,
)

from backend.attacks.plc.plc_state import (
    PLCState,
)


class SetpointManipulationAttack(PLCAttack):
    """
    Manipulates PLC process setpoints.
    """

    def __init__(
        self,
        attack_id: str = "PLC_003",
        duration: float = 30.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Setpoint Manipulation Attack",
            duration=duration,
        )

        self.offset = 15.0

    # ==========================================
    # Modify Setpoint
    # ==========================================

    def modify_setpoint(
        self,
        value: float,
    ) -> float:

        if self.is_running:

            return value + self.offset

        return value

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        PLCState.manipulated_setpoint = (
            self.offset
        )

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        PLCState.manipulated_setpoint = None

        super().stop()