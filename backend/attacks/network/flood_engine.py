"""
flood_engine.py

Simulates network flooding during
DoS attacks.
"""

from __future__ import annotations


class FloodEngine:
    """
    Simulates increasing network load.
    """

    def __init__(
        self,
        max_rate: int = 5000,
    ) -> None:

        self.max_rate = max_rate

        self.current_rate = 0

        self.network_load = 0.0

        self.active = False

    # ==========================================
    # Lifecycle
    # ==========================================

    def start(self) -> None:

        self.active = True

        self.current_rate = 0

        self.network_load = 0.0

    def stop(self) -> None:

        self.active = False

        self.current_rate = 0

        self.network_load = 0.0

    # ==========================================
    # Update
    # ==========================================

    def update(
        self,
        progress: float,
    ) -> None:

        if not self.active:

            return

        progress = max(
            0.0,
            min(1.0, progress),
        )

        self.current_rate = int(
            self.max_rate * progress
        )

        self.network_load = round(
            progress * 100,
            2,
        )

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        return {

            "active": self.active,

            "packets_per_second":
                self.current_rate,

            "network_load":
                self.network_load,
        }

    def __str__(
        self,
    ) -> str:

        return (
            f"FloodEngine("
            f"{self.current_rate} pkt/s, "
            f"{self.network_load}% load)"
        )