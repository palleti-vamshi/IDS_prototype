"""
simulation_clock.py

Central simulation clock for the LightX-IDS
Industrial Digital Twin.
"""

from __future__ import annotations

import time


class SimulationClock:
    """
    Controls simulation time.

    Every subsystem in the simulator should
    use this clock instead of calling time.sleep()
    directly.
    """

    def __init__(
        self,
        tick_rate: float = 1.0,
    ) -> None:

        # Seconds per simulation tick
        self.tick_rate = tick_rate

        # Current simulation tick
        self.tick = 0

        # Total elapsed simulation time
        self.elapsed_time = 0.0

        # Running flag
        self.running = False

    # ==================================================
    # Lifecycle
    # ==================================================

    def start(self) -> None:

        self.running = True

        self.tick = 0

        self.elapsed_time = 0.0

    def stop(self) -> None:

        self.running = False

    # ==================================================
    # Tick
    # ==================================================

    def step(self) -> None:
        """
        Advance the simulation by one tick.
        """

        if not self.running:
            return

        time.sleep(self.tick_rate)

        self.tick += 1

        self.elapsed_time += self.tick_rate

    # ==================================================
    # Information
    # ==================================================

    def get_status(self) -> dict:

        return {
            "running": self.running,
            "tick": self.tick,
            "elapsed_time": round(
                self.elapsed_time,
                2,
            ),
            "tick_rate": self.tick_rate,
        }

    def __str__(self) -> str:

        return (
            f"SimulationClock("
            f"tick={self.tick}, "
            f"time={self.elapsed_time:.2f}s)"
        )