"""
valve_stuck_attack.py

Valve Stuck Attack
"""

from __future__ import annotations

from backend.attacks.process.process_attack import (
    ProcessAttack,
)

from backend.attacks.process.process_state import (
    ProcessState,
)


class ValveStuckAttack(ProcessAttack):
    """
    Simulates a valve becoming stuck
    in one position.
    """

    def __init__(
        self,
        attack_id: str = "PRC_002",
        duration: float = 30.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Valve Stuck Attack",
            duration=duration,
        )

        self.stuck_position = None

    # ==========================================
    # Modify Position
    # ==========================================

    def modify_position(
        self,
        position: float,
    ) -> float:

        if not self.is_running:
            return position

        if self.stuck_position is None:

            self.stuck_position = position

        return self.stuck_position

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        ProcessState.valve_stuck = True

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        ProcessState.valve_stuck = False

        self.stuck_position = None

        super().stop()