"""
spoof_engine.py

Generates realistic spoofed sensor values.
"""

from __future__ import annotations

import random


class SpoofEngine:
    """
    Produces believable spoofed values
    by gradually drifting from the real value.
    """

    def __init__(self) -> None:

        self.offset = 0.0

        self.max_offset = 15.0

        self.noise = 0.25

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

        self.offset = round(
            progress * self.max_offset,
            2,
        )

    # ==========================================
    # Spoof
    # ==========================================

    def generate(
        self,
        real_value: float,
    ) -> float:

        value = (

            real_value

            + self.offset

            + random.uniform(
                -self.noise,
                self.noise,
            )

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

        self.offset = 0.0

    def get_status(
        self,
    ) -> dict:

        return {

            "offset": self.offset,

            "max_offset": self.max_offset,

            "noise": self.noise,
        }