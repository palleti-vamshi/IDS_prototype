"""
Simulation Runner

Starts the factory simulator in a background thread
and exposes the simulator's existing attack framework
to the Phase 3 dataset generator.
"""

import threading
import time

from backend.industrial.simulator.factory_simulator import (
    FactorySimulator,
)


class SimulationRunner:
    """Runs the factory simulator."""

    def __init__(self):

        self.simulator = FactorySimulator()

        self.thread = None

    # ==================================================
    # Start
    # ==================================================

    def start(self):
        """Start simulator in background."""

        if (
            self.thread
            and self.thread.is_alive()
        ):

            print(
                "⚠️ Factory Simulator is already running."
            )

            return

        self.thread = threading.Thread(
            target=self.simulator.run,
            daemon=True,
            name="FactorySimulatorThread",
        )

        self.thread.start()

        print(
            "🏭 Factory Simulator Starting..."
        )

        # ==========================================
        # Wait for initialization
        # ==========================================

        timeout = 10.0

        start_time = time.time()

        while (
            not self.simulator.initialized
            and (
                time.time()
                - start_time
            )
            < timeout
        ):

            # If simulator stopped before
            # initialization completed
            if (
                not self.thread.is_alive()
            ):

                raise RuntimeError(
                    "Factory Simulator stopped "
                    "before initialization completed."
                )

            time.sleep(0.1)

        # ==========================================
        # Initialization result
        # ==========================================

        if not self.simulator.initialized:

            raise RuntimeError(
                "Factory Simulator initialization "
                "timed out."
            )

        print(
            "✅ Factory Simulator Initialized"
        )

        print(
            "🏭 Factory Simulator Started"
        )

    # ==================================================
    # Attack Framework
    # ==================================================

    def get_attack_manager(self):
        """
        Return the AttackManager owned by the
        FactorySimulator.

        AttackRunner uses this existing manager.
        """

        if not self.simulator.initialized:

            raise RuntimeError(
                "Factory Simulator is not initialized."
            )

        return (
            self.simulator.attack_manager
        )

    # ==================================================
    # Attack Initializer
    # ==================================================

    def get_attack_initializer(self):
        """
        Return the AttackInitializer owned by the
        FactorySimulator.
        """

        if not self.simulator.initialized:

            raise RuntimeError(
                "Factory Simulator is not initialized."
            )

        return (
            self.simulator.attack_initializer
        )

    # ==================================================
    # Attacks
    # ==================================================

    def get_attacks(self):
        """
        Return the actual attack objects owned by
        the FactorySimulator.

        These are NOT newly created attack objects.
        """

        if not self.simulator.initialized:

            raise RuntimeError(
                "Factory Simulator is not initialized."
            )

        attacks = (
            self.simulator
            .attack_initializer
            .get_campaign_attacks()
        )

        if not attacks:

            raise RuntimeError(
                "Factory Simulator attack framework "
                "returned no attacks."
            )

        return attacks

    # ==================================================
    # Simulator Status
    # ==================================================

    def is_running(self) -> bool:
        """
        Return whether the factory simulator
        is currently running.
        """

        return self.simulator.running

    # ==================================================
    # Stop
    # ==================================================

    def stop(self):
        """Stop simulator."""

        self.simulator.stop()

        if (
            self.thread
            and self.thread.is_alive()
        ):

            self.thread.join(
                timeout=5
            )

        print(
            "🛑 Factory Simulator Stopped"
        )