"""
drift_engine.py

Generates realistic sensor drift.
"""

from __future__ import annotations

import random


class DriftEngine:
    """
    Simulates gradual sensor drift.
    """

    def __init__(self) -> None:

        self.current_drift = 0.0

        self.max_drift = 8.0

        self.randomness = 0.15

    # ==========================================
    # Update
    # ==========================================

    def update(
        self,
        progress: float,
    ) -> None:

        progress = max(
            0.0,
            min(1.0, progress),
        )

        self.current_drift = round(
            progress * self.max_drift,
            2,
        )

    # ==========================================
    # Apply Drift
    # ==========================================

    def generate(
        self,
        value: float,
    ) -> float:

        drifted = (

            value

            + self.current_drift

            + random.uniform(
                -self.randomness,
                self.randomness,
            )

        )

        return round(
            drifted,
            2,
        )

    # ==========================================
    # Reset
    # ==========================================

    def reset(
        self,
    ) -> None:

        self.current_drift = 0.0

    def get_status(
        self,
    ) -> dict:

        return {

            "current_drift":
                self.current_drift,

            "max_drift":
                self.max_drift,
        }