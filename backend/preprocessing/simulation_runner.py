"""
Simulation Runner

Starts the factory simulator in a background thread.
"""

import threading

from backend.industrial.simulator.factory_simulator import FactorySimulator


class SimulationRunner:
    """Runs the factory simulator."""

    def __init__(self):
        self.simulator = FactorySimulator()
        self.thread = None

    def start(self):
        """Start simulator."""

        self.thread = threading.Thread(
            target=self.simulator.start,
            daemon=True,
        )

        self.thread.start()

        print("🏭 Factory Simulator Started")

    def stop(self):
        """Stop simulator."""

        self.simulator.stop()

        print("🛑 Factory Simulator Stopped")