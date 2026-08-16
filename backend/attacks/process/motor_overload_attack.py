"""
motor_overload_attack.py

Motor Overload Attack
"""

from __future__ import annotations

from backend.attacks.process.process_attack import (
    ProcessAttack,
)

from backend.attacks.process.process_state import (
    ProcessState,
)


class MotorOverloadAttack(ProcessAttack):
    """
    Forces the motor to operate above
    its normal load.
    """

    def __init__(
        self,
        attack_id: str = "PRC_001",
        duration: float = 30.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Motor Overload Attack",
            duration=duration,
        )

        self.overload_factor = 1.5

    # ==========================================
    # Modify Load
    # ==========================================

    def modify_load(
        self,
        load: float,
    ) -> float:

        if self.is_running:

            return round(
                load * self.overload_factor,
                2,
            )

        return load

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        # Update shared Process Attack Engine
        self.engine.update(

            motor_overload=True,

            overload_factor=self.overload_factor,

            attack_name=self.attack_name,

        )

        # Compatibility Layer (temporary)
        ProcessState.motor_overload = True

        ProcessState.overload_factor = (
            self.overload_factor
        )

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        ProcessState.motor_overload = False

        ProcessState.overload_factor = 1.5

        super().stop()