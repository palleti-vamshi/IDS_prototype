"""
factory_simulator.py

Central orchestrator for the LightX-IDS
Industrial Digital Twin.
"""

from __future__ import annotations

from backend.core.logger import setup_logger
import json

from backend.industrial.mqtt.publisher import (
    MQTTPublisher,
)

from backend.industrial.config.mqtt_config import (
    MACHINE_STATUS_TOPIC,
)

from backend.industrial.Factory.factory_builder import (
    FactoryBuilder,
)

from backend.industrial.behavior.behavior_engine import (
    BehaviorEngine,
)

from backend.industrial.simulator.simulation_clock import (
    SimulationClock,
)

from backend.attacks.attack_manager import (
    AttackManager,
)

from backend.attacks.attack_scheduler import (
    AttackScheduler,
)

from backend.attacks.scenarios.scenario_manager import (
    ScenarioManager,
)

from backend.attacks.attack_initializer import (
    AttackInitializer,
)


class FactorySimulator:
    """
    Central orchestrator of the Industrial Digital Twin.
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

        self.attack_manager = AttackManager()

        self.attack_scheduler = AttackScheduler()

        self.scenario_manager = ScenarioManager()

        self.attack_initializer = AttackInitializer(
            self.attack_manager,
            self.scenario_manager,
        )
        self.machine_status_publisher = MQTTPublisher(
            "factory_machine_status"
        )
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

        self.logger.info(
            "Initializing Factory Simulator..."
        )

        self.build_factory()

        self.register_behaviors()

        self.collect_sensors()

        self.attack_initializer.initialize()

        # =====================================
        # Automatic Attack Campaign
        # =====================================

        self.attack_scheduler.start_campaign(
            self.attack_initializer.get_campaign_attacks()
        )

        self.logger.info(
                    "Initialization completed."
        )

    # ==========================================
    # Factory
    # ==========================================

    def build_factory(self) -> None:

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

    # ==========================================
    # Behaviors
    # ==========================================

    def register_behaviors(self) -> None:

        for machine in self.machines:

            self.behavior_engine.register_machine(
                machine
            )

        self.logger.info(
            "%d behaviors registered.",
            self.behavior_engine.total_behaviors,
        )

    # ==========================================
    # Sensors
    # ==========================================

    def collect_sensors(self) -> None:

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
    # Simulation
    # ==========================================

    def simulation_step(self) -> None:

        self.clock.step()

        self.attack_scheduler.update(
            self.clock.tick_rate
        )

        self.attack_scheduler.print_progress()

        self.attack_manager.update(
            self.clock.tick_rate
        )

        self.behavior_engine.update(
            self.clock.tick_rate
        )

        for sensor in self.sensors:

            sensor.read()

    # ==========================================
    # MQTT
    # ==========================================

    def publish_cycle(self) -> None:

        for sensor in self.sensors:

            sensor.publish()
        self.publish_machine_status()

    # ==========================================
    # Run
    # ==========================================
    def publish_machine_status(self) -> None:
        """Publish the current status of all industrial machines."""

        machines = []

        for machine in self.machines:
            machines.append(
                machine.get_status()
            )

        payload = {
            "machines": machines
        }

        self.machine_status_publisher.publish(
            MACHINE_STATUS_TOPIC,
            payload,
        )  
    def run(self) -> None:

        self.initialize()

        self.behavior_engine.start_all()

        for machine in self.machines:

            machine.start()

        self.factory.start()

        for sensor in self.sensors:

            sensor.start()

        self.clock.start()

        self.running = True

        self.logger.info(
            "LightX-IDS Factory Simulator Started."
        )

        try:

            while self.running:

                self.simulation_step()

                self.publish_cycle()

                if (
                    self.attack_scheduler.campaign_finished()
                ):

                    print()

                    print("=" * 70)

                    print(
                        "🎉 ATTACK CAMPAIGN FINISHED"
                    )

                    print("=" * 70)

                    self.stop()

        except KeyboardInterrupt:

            self.stop()

    # ==========================================
    # Shutdown
    # ==========================================

    def stop(self) -> None:

        self.running = False

        self.attack_manager.stop_all()

        self.attack_scheduler.reset()

        if self.factory:

            self.factory.stop()

        for sensor in self.sensors:

            sensor.stop()

        self.clock.stop()

        self.logger.info(
            "Factory Simulator Stopped."
        )
        self.machine_status_publisher.disconnect()
    def __str__(self) -> str:

        return (
            f"FactorySimulator("
            f"Machines={len(self.machines)}, "
            f"Sensors={len(self.sensors)})"
        )


if __name__ == "__main__":

    simulator = FactorySimulator()

    simulator.run()