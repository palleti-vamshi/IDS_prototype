"""
factory_simulator.py

Central orchestrator for the LightX-IDS
Industrial Digital Twin.
"""

from __future__ import annotations

from backend.core.logger import setup_logger

from backend.industrial.factory.factory_builder import (
    FactoryBuilder,
)

from backend.industrial.behavior.behavior_engine import (
    BehaviorEngine,
)

from backend.industrial.simulator.simulation_clock import (
    SimulationClock,
)


class FactorySimulator:
    """
    Central orchestrator of the Industrial Digital Twin.

    Responsibilities
    ----------------
    • Build factory
    • Register behaviors
    • Collect sensors
    • Execute simulation
    • Publish MQTT
    """

    def __init__(self) -> None:

        self.logger = setup_logger(
            "FactorySimulator"
        )

        # =====================================
        # Core Components
        # =====================================

        self.clock = SimulationClock()

        self.builder = FactoryBuilder()

        self.behavior_engine = BehaviorEngine()

        # =====================================
        # Industrial Assets
        # =====================================

        self.factory = None

        self.production_line = None

        self.machines = []

        self.sensors = []

        # =====================================
        # Runtime
        # =====================================

        self.running = False

    # ==========================================
    # Initialization
    # ==========================================

    def initialize(self) -> None:
        """
        Build the complete digital twin.
        """

        self.logger.info(
            "Initializing Factory Simulator..."
        )

        self.build_factory()

        self.register_behaviors()

        self.collect_sensors()

        self.logger.info(
            "Initialization completed."
        )

    # ==========================================
    # Factory Construction
    # ==========================================

    def build_factory(self) -> None:
        """
        Construct the factory hierarchy.
        """

        self.factory = self.builder.assemble()

        self.production_line = (
            self.builder.get_production_line()
        )

        self.machines = (
            self.builder.get_machines()
        )

        self.logger.info(
            "Factory constructed."
        )

        self.logger.info(
            "Machines : %d",
            len(self.machines),
        )

    # ==========================================
    # Behavior Registration
    # ==========================================

    def register_behaviors(self) -> None:
        """
        Register every machine with
        the Behavior Engine.
        """

        for machine in self.machines:

            self.behavior_engine.register_machine(
                machine
            )

        self.logger.info(
            "%d behaviors registered.",
            self.behavior_engine.total_behaviors,
        )

    # ==========================================
    # Sensor Collection
    # ==========================================

    def collect_sensors(self) -> None:
        """
        Collect all attached sensors.
        """

        self.sensors.clear()

        for machine in self.machines:

            self.sensors.extend(
                machine.get_sensors()
            )

        self.logger.info(
            "%d sensors discovered.",
            len(self.sensors),
        )

    # ==========================================
    # Simulation Step
    # ==========================================

    def simulation_step(self) -> None:
        """
        Execute one synchronized simulation cycle.
        """

        # Advance simulation clock
        self.clock.step()

        # Update machine behaviors
        self.behavior_engine.update(
            self.clock.tick_rate
        )

        # Read all sensors
        for sensor in self.sensors:
            sensor.read()

    # ==========================================
    # MQTT Publishing
    # ==========================================

    def publish_cycle(self) -> None:
        """
        Publish all sensor packets.
        """

        for sensor in self.sensors:

            success = sensor.publish()

            if not success:

                self.logger.warning(
                    "Failed to publish sensor %s",
                    sensor.sensor_code,
                )

    # ==========================================
    # Main Simulation Loop
    # ==========================================

    def run(self) -> None:
        """
        Run the complete factory continuously.
        """

        self.initialize()
        self.behavior_engine.start_all()
        # Start all machines
        for machine in self.machines:
            machine.start()

        # Start factory hierarchy
        self.factory.start()

        # Activate sensors
        for sensor in self.sensors:
            sensor.start()

        self.clock.start()

        self.running = True

        self.logger.info(
            "========================================"
        )
        self.logger.info(
            "LightX-IDS Factory Simulator Started"
        )
        self.logger.info(
            "Press Ctrl+C to stop."
        )
        self.logger.info(
            "========================================"
        )

        try:

            while self.running:

                self.simulation_step()

                self.publish_cycle()

                self.logger.info(
                    "Tick=%d | Machines=%d | Sensors=%d",
                    self.clock.tick,
                    len(self.machines),
                    len(self.sensors),
                )

        except KeyboardInterrupt:

            self.logger.info(
                "Stopping simulator..."
            )

            self.stop()

    # ==========================================
    # Shutdown
    # ==========================================

    def stop(self) -> None:
        """
        Stop the complete simulator.
        """

        self.running = False

        if self.factory:
            self.factory.stop()

        for sensor in self.sensors:
            sensor.stop()

        self.clock.stop()

        self.logger.info(
            "Factory Simulator Stopped."
        )

    # ==========================================
    # Status
    # ==========================================

    def get_status(self) -> dict:
        """
        Return simulator status.
        """

        return {

            "running": self.running,

            "clock": self.clock.get_status(),

            "machines": len(self.machines),

            "sensors": len(self.sensors),

            "behaviors": (
                self.behavior_engine.total_behaviors
            ),
        }

    # ==========================================

    def __str__(self) -> str:

        return (
            f"FactorySimulator("
            f"Machines={len(self.machines)}, "
            f"Sensors={len(self.sensors)})"
        )


if __name__ == "__main__":

    simulator = FactorySimulator()

    simulator.run()