"""
factory_simulator.py

Central orchestrator of the LightX-IDS
Industrial Digital Twin.

IMPORTANT
---------
The Phase 3 Dataset AttackRunner controls
attack execution.

FactorySimulator ONLY:
    - Runs the industrial simulation
    - Updates AttackManager
    - Publishes sensor data
    - Evaluates alarms

AttackScheduler is NOT executed here during
Phase 3 dataset generation.
"""

from __future__ import annotations

from backend.core.logger import setup_logger

from backend.industrial.mqtt.publisher import (
    MQTTPublisher,
)

from backend.industrial.config.mqtt_config import (
    MACHINE_STATUS_TOPIC,
)

from backend.industrial.factory.factory_builder import (
    FactoryBuilder,
)

from backend.industrial.behavior.behavior_engine import (
    BehaviorEngine,
)

from backend.industrial.physics.physics_engine import (
    PhysicsEngine,
)

from backend.industrial.dependencies.dependency_engine import (
    DependencyEngine,
)

from backend.industrial.simulator.simulation_clock import (
    SimulationClock,
)

# ==================================================
# Industrial Events / Alarms
# ==================================================

from backend.industrial.events.event_logger import (
    IndustrialEventLogger,
)

from backend.industrial.alarms.alarm_manager import (
    AlarmManager,
)

from backend.industrial.alarms.industrial_alarm_rules import (
    get_default_alarm_rules,
)

# ==================================================
# Cyber Attack Framework
# ==================================================

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

from backend.attacks.sensor.sensor_attack import (
    SensorAttack,
)


class FactorySimulator:
    """
    Central orchestrator of the Industrial Digital Twin.

    During Phase 3 dataset generation, attack execution
    is controlled by AttackRunner.

    FactorySimulator is responsible for continuously
    updating the AttackManager so that active attacks
    actually affect the industrial environment.
    """

    def __init__(self) -> None:

        self.logger = setup_logger(
            "FactorySimulator"
        )

        # ==========================================
        # Core Components
        # ==========================================

        self.clock = SimulationClock()

        self.builder = FactoryBuilder()

        self.behavior_engine = BehaviorEngine()

        self.physics_engine = PhysicsEngine()

        self.dependency_engine = DependencyEngine()

        # ==========================================
        # Industrial Event / Alarm System
        # ==========================================

        self.event_logger = IndustrialEventLogger()

        self.alarm_manager = AlarmManager(
            event_logger=self.event_logger
        )

        # ==========================================
        # Cyber Attack Components
        # ==========================================

        self.attack_manager = AttackManager()

        # ------------------------------------------
        # Kept for backward compatibility.
        #
        # IMPORTANT:
        # Phase 3 AttackRunner controls attacks.
        # The scheduler is NOT updated by the
        # simulator during Phase 3 generation.
        # ------------------------------------------

        self.attack_scheduler = AttackScheduler()

        self.scenario_manager = ScenarioManager()

        self.attack_initializer = AttackInitializer(
            self.attack_manager,
            self.scenario_manager,
        )

        # ==========================================
        # SCADA Machine Status Publisher
        # ==========================================

        self.machine_status_publisher = MQTTPublisher(
            "factory_machine_status"
        )

        # ==========================================
        # Industrial Assets
        # ==========================================

        self.factory = None

        self.production_line = None

        self.machines = []

        self.sensors = []

        # ==========================================
        # Runtime
        # ==========================================

        self.running = False

        self.initialized = False

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

        self.initialize_alarm_system()

        # ==========================================
        # Initialize Attack Framework
        # ==========================================

        self.attack_initializer.initialize()

        self.initialized = True

        self.logger.info(
            "Attack framework initialized. "
            "Attack execution delegated to Phase 3 "
            "AttackRunner."
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

            self.physics_engine.register_machine(
                machine
            )

            self.dependency_engine.register_machine(
                machine
            )

        self.logger.info(
            "%d behaviors registered.",
            self.behavior_engine.total_behaviors,
        )

        # ==========================================
        # Machine Dependencies
        # ==========================================

        self.dependency_engine.register_dependency(
            "TANK_001",
            "PUMP_001",
        )

        self.dependency_engine.register_dependency(
            "PUMP_001",
            "VALVE_001",
        )

        self.dependency_engine.register_dependency(
            "VALVE_001",
            "CONVEYOR_001",
        )

        self.dependency_engine.register_dependency(
            "MOTOR_001",
            "CONVEYOR_001",
        )

        self.dependency_engine.register_dependency(
            "COMPRESSOR_001",
            "VALVE_001",
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

        # ==========================================
        # Register Sensors with Shared Attack Engine
        # ==========================================

        for sensor in self.sensors:

            SensorAttack.attack_engine.register_sensor(
                sensor.sensor_code
            )

        self.logger.info(
            "%d sensors discovered.",
            len(self.sensors),
        )

        self.logger.info(
            "%d sensors registered with "
            "SensorAttackEngine.",
            SensorAttack.attack_engine.total_registered,
        )

    # ==========================================
    # Alarm System
    # ==========================================

    def initialize_alarm_system(self) -> None:
        """
        Register all default industrial alarm rules.
        """

        rules = get_default_alarm_rules()

        for rule in rules:

            self.alarm_manager.register_rule(
                rule
            )

        self.logger.info(
            "%d industrial alarm rules registered.",
            self.alarm_manager.total_rules,
        )

    # ==========================================
    # Alarm Source Mapping
    # ==========================================

    @staticmethod
    def get_alarm_source(
        sensor,
    ) -> str | None:
        """
        Convert a machine-specific sensor code into
        the canonical alarm-rule source.
        """

        sensor_code = getattr(
            sensor,
            "sensor_code",
            "",
        )

        if not sensor_code:
            return None

        suffix_map = {

            "TMP": "TMP-001",

            "PRS": "PRS-001",

            "FLW": "FLW-001",

            "CUR": "CUR-001",

            "LVL": "LVL-001",

            "RPM": "RPM-001",

            "VIB": "VIB-001",

            "PRX": "PRX-001",

            "VLT": "VLT-001",

            "HUM": "HUM-001",
        }

        parts = sensor_code.split("-")

        if not parts:
            return None

        suffix = parts[-1]

        return suffix_map.get(
            suffix
        )

    # ==========================================
    # Alarm Evaluation
    # ==========================================

    def evaluate_sensor_alarm(
        self,
        sensor,
        value: float,
    ) -> None:
        """
        Evaluate one sensor reading against the
        industrial alarm rules.
        """

        source = self.get_alarm_source(
            sensor
        )

        if source is None:
            return

        alarms = self.alarm_manager.evaluate(
            source,
            value,
        )

        for alarm in alarms:

            print(
                f"\n🚨 INDUSTRIAL ALARM | "
                f"{alarm.severity} | "
                f"{alarm.alarm_type} | "
                f"{alarm.source} | "
                f"{alarm.value} "
                f"{alarm.unit}\n"
            )

    # ==========================================
    # Simulation
    # ==========================================

    def simulation_step(self) -> None:

        self.clock.step()

        # ==========================================
        # ATTACK EXECUTION
        # ==========================================
        #
        # AttackRunner starts/stops the attack.
        #
        # AttackManager.update() is responsible for
        # actually executing the currently active
        # attack and applying its effects.
        #
        # This MUST remain here.
        # ==========================================

        self.attack_manager.update(
            self.clock.tick_rate
        )

        # ==========================================
        # IMPORTANT
        # ==========================================
        #
        # Do NOT call:
        #
        # self.attack_scheduler.update(...)
        #
        # during Phase 3.
        #
        # AttackRunner is the sole attack controller.
        # ==========================================

        # ==========================================
        # Industrial Simulation
        # ==========================================

        self.behavior_engine.update(
            self.clock.tick_rate
        )

        self.physics_engine.update(
            self.clock.tick_rate
        )

        self.dependency_engine.update(
            self.clock.tick_rate
        )

        # ==========================================
        # Sensors + Alarm Evaluation
        # ==========================================

        for sensor in self.sensors:

            value = sensor.read()

            if value is None:
                continue

            self.evaluate_sensor_alarm(
                sensor,
                value,
            )

    # ==========================================
    # MQTT
    # ==========================================

    def publish_cycle(self) -> None:

        for sensor in self.sensors:

            sensor.publish()

        self.publish_machine_status()

    # ==========================================
    # Machine Status
    # ==========================================

    def publish_machine_status(self) -> None:
        """
        Publish the current status of all
        industrial machines for SCADA monitoring.
        """

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

    # ==========================================
    # Run
    # ==========================================

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

        except KeyboardInterrupt:

            self.stop()

    # ==========================================
    # Shutdown
    # ==========================================

    def stop(self) -> None:

        if not self.running:

            return

        self.running = False

        # ==========================================
        # Stop Active Attacks
        # ==========================================

        self.attack_manager.stop_all()

        # ==========================================
        # Reset Scheduler
        # ==========================================
        #
        # Scheduler is retained for compatibility,
        # but it does NOT control Phase 3 attacks.
        # ==========================================

        self.attack_scheduler.reset()

        # ==========================================
        # Reset Alarms
        # ==========================================

        self.alarm_manager.reset()

        # ==========================================
        # Stop Factory
        # ==========================================

        if self.factory:

            self.factory.stop()

        # ==========================================
        # Stop Sensors
        # ==========================================

        for sensor in self.sensors:

            sensor.stop()

        # ==========================================
        # Stop Clock
        # ==========================================

        self.clock.stop()

        # ==========================================
        # SCADA Publisher Shutdown
        # ==========================================

        self.machine_status_publisher.disconnect()

        self.logger.info(
            "Factory Simulator Stopped."
        )

    # ==========================================
    # Status
    # ==========================================

    def get_status(self) -> dict:
        """
        Return complete simulator status.
        """

        return {

            "running":
                self.running,

            "initialized":
                self.initialized,

            "clock":
                self.clock.get_status(),

            "machines":
                len(self.machines),

            "sensors":
                len(self.sensors),

            "dependencies":
                self.dependency_engine.get_status(),

            "alarms":
                self.alarm_manager.get_status(),

            "events":
                self.event_logger.get_status(),

            "attacks":
                self.attack_manager.get_status(),
        }

    # ==========================================
    # String
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