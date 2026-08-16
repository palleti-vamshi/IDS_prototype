"""
noise_engine.py

Generates realistic sensor noise.
"""

from __future__ import annotations

import random


class NoiseEngine:
    """
    Simulates sensor measurement noise.
    """

    def __init__(self) -> None:

        self.noise_level = 0.0

        self.max_noise = 2.0

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

        self.noise_level = round(
            progress * self.max_noise,
            2,
        )

    # ==========================================
    # Apply Noise
    # ==========================================

    def generate(
        self,
        value: float,
    ) -> float:

        value += random.uniform(
            -self.noise_level,
            self.noise_level,
        )

        return round(
            value,
            2,
        )

    # ==========================================
    # Reset
    # ==========================================

    def reset(
        self,
    ) -> None:

        self.noise_level = 0.0

    def get_status(
        self,
    ) -> dict:

        return {

            "noise_level":
                self.noise_level,

            "max_noise":
                self.max_noise,
        }