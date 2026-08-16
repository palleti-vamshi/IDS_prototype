"""
slow_drift_attack.py

Slow Drift Attack
"""

from __future__ import annotations

from backend.attacks.stealth.stealth_attack import (
    StealthAttack,
)

from backend.attacks.stealth.stealth_state import (
    StealthState,
)


class SlowDriftAttack(StealthAttack):
    """
    Slowly changes process values to
    avoid immediate detection.
    """

    def __init__(
        self,
        attack_id: str = "STL_001",
        duration: float = 60.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="Slow Drift Attack",
            duration=duration,
        )

        self.max_drift = 10.0

    # ==========================================
    # Modify Value
    # ==========================================

    def modify_value(
        self,
        value: float,
    ) -> float:

        if self.is_running:

            progress = min(
                self.elapsed_time / self.duration,
                1.0,
            )

            return round(
                value + progress * self.max_drift,
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

        progress = min(
            self.elapsed_time / self.duration,
            1.0,
        )

        drift = progress * self.max_drift

        # Shared Stealth Engine
        self.engine.update(

            slow_drift=True,

            drift_rate=drift,

            attack_name=self.attack_name,

        )

        # Compatibility Layer
        StealthState.slow_drift = True

        StealthState.drift_rate = drift

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        StealthState.slow_drift = False

        StealthState.drift_rate = 0.0

        super().stop()