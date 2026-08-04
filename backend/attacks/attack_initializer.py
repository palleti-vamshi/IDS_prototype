"""
attack_initializer.py

Initializes and wires together all cyber attacks
and attack scenarios for the LightX-IDS platform.
"""

from __future__ import annotations

from backend.core.logger import setup_logger

# ==================================================
# Network Attacks
# ==================================================

from backend.attacks.network.dos_attack import (
    DoSAttack,
)

from backend.attacks.network.replay_attack import (
    ReplayAttack,
)

from backend.attacks.network.packet_delay_attack import (
    PacketDelayAttack,
)

from backend.attacks.network.packet_drop_attack import (
    PacketDropAttack,
)

from backend.attacks.network.mqtt_hijack_attack import (
    MQTTTopicHijackingAttack,
)

# ==================================================
# Sensor Attacks
# ==================================================

from backend.attacks.sensor.sensor_spoofing_attack import (
    SensorSpoofingAttack,
)

from backend.attacks.sensor.false_data_injection_attack import (
    FalseDataInjectionAttack,
)

from backend.attacks.sensor.sensor_drift_attack import (
    SensorDriftAttack,
)

from backend.attacks.sensor.sensor_freeze_attack import (
    SensorFreezeAttack,
)

from backend.attacks.sensor.noise_injection_attack import (
    SensorNoiseInjectionAttack,
)

# ==================================================
# PLC Attacks
# ==================================================

from backend.attacks.plc.command_injection_attack import (
    PLCCommandInjectionAttack,
)

from backend.attacks.plc.unauthorized_command_attack import (
    UnauthorizedCommandAttack,
)

from backend.attacks.plc.setpoint_manipulation_attack import (
    SetpointManipulationAttack,
)

# ==================================================
# Process Attacks
# ==================================================

from backend.attacks.process.motor_overload_attack import (
    MotorOverloadAttack,
)

from backend.attacks.process.valve_stuck_attack import (
    ValveStuckAttack,
)

# ==================================================
# Stealth Attacks
# ==================================================

from backend.attacks.stealth.intermittent_attack import (
    IntermittentAttack,
)

from backend.attacks.stealth.slow_drift_attack import (
    SlowDriftAttack,
)

# ==================================================
# Scenarios
# ==================================================

from backend.attacks.scenarios.network_scenarios import (
    NetworkScenario,
)

from backend.attacks.scenarios.sensor_scenarios import (
    SensorScenario,
)

from backend.attacks.scenarios.plc_scenarios import (
    PLCScenario,
)

from backend.attacks.scenarios.process_scenarios import (
    ProcessScenario,
)

from backend.attacks.scenarios.hybrid_scenarios import (
    HybridScenario,
)


class AttackInitializer:
    """
    Initializes the attack framework.

    Responsibilities
    ----------------
    • Create attack objects
    • Register attacks
    • Create scenarios
    • Register scenarios
    """

    def __init__(
        self,
        attack_manager,
        scenario_manager,
    ) -> None:

        self.logger = setup_logger(
            "AttackInitializer"
        )

        self.attack_manager = attack_manager

        self.scenario_manager = scenario_manager


    # ==================================================
    # Initialization
    # ==================================================

    def initialize(self) -> None:
        """
        Build the complete attack framework.
        """

        self.logger.info(
            "Initializing attack framework..."
        )

        self.create_attacks()

        self.register_attacks()

        self.create_scenarios()

        self.register_scenarios()

        self.logger.info(
            "Attack framework initialized."
        )

    # ==================================================
    # Attack Creation
    # ==================================================

    def create_attacks(self) -> None:
        """
        Create all attack objects.
        """

        self.attacks = {

            # ===========================
            # Network
            # ===========================

            "dos": DoSAttack(),

            "replay": ReplayAttack(),

            "packet_delay": PacketDelayAttack(),

            "packet_drop": PacketDropAttack(),

            "mqtt_hijack": MQTTTopicHijackingAttack(),

            # ===========================
            # Sensor
            # ===========================

            "spoof": SensorSpoofingAttack(),

            "false_data": FalseDataInjectionAttack(),

            "drift": SensorDriftAttack(),

            "freeze": SensorFreezeAttack(),

            "noise": SensorNoiseInjectionAttack(),

            # ===========================
            # PLC
            # ===========================

            "command_injection":
                PLCCommandInjectionAttack(),

            "unauthorized":
                UnauthorizedCommandAttack(),

            "setpoint":
                SetpointManipulationAttack(),

            # ===========================
            # Process
            # ===========================

            "motor":
                MotorOverloadAttack(),

            "valve":
                ValveStuckAttack(),

            # ===========================
            # Stealth
            # ===========================

            "intermittent":
                IntermittentAttack(),

            "slow_drift":
                SlowDriftAttack(),
        }

        self.logger.info(
            "%d attacks created.",
            len(self.attacks),
        )


    # ==================================================
    # Attack Registration
    # ==================================================

    def register_attacks(self) -> None:
        """
        Register every attack with AttackManager.
        """

        for attack in self.attacks.values():

            self.attack_manager.register_attack(
                attack
            )

        self.logger.info(
            "%d attacks registered.",
            len(self.attacks),
        )

    # ==================================================
    # Scenario Creation
    # ==================================================

    def create_scenarios(self) -> None:
        """
        Create all attack scenarios.
        """

        self.network_scenario = NetworkScenario(
            self.attacks["dos"],
            self.attacks["replay"],
            self.attacks["packet_delay"],
            self.attacks["packet_drop"],
            self.attacks["mqtt_hijack"],
        )

        self.sensor_scenario = SensorScenario(
            self.attacks["spoof"],
            self.attacks["false_data"],
            self.attacks["drift"],
            self.attacks["freeze"],
            self.attacks["noise"],
        )

        self.plc_scenario = PLCScenario(
            self.attacks["command_injection"],
            self.attacks["unauthorized"],
            self.attacks["setpoint"],
        )

        self.process_scenario = ProcessScenario(
            self.attacks["motor"],
            self.attacks["valve"],
        )

        self.hybrid_scenario = HybridScenario(
            self.attacks["dos"],
            self.attacks["spoof"],
            self.attacks["command_injection"],
            self.attacks["motor"],
            self.attacks["drift"],
        )

        self.logger.info(
            "All scenarios created."
        )


    # ==================================================
    # Scenario Registration
    # ==================================================

    def register_scenarios(self) -> None:
        """
        Register all scenarios with ScenarioManager.
        """

        self.scenario_manager.register(
            self.network_scenario
        )

        self.scenario_manager.register(
            self.sensor_scenario
        )

        self.scenario_manager.register(
            self.plc_scenario
        )

        self.scenario_manager.register(
            self.process_scenario
        )

        self.scenario_manager.register(
            self.hybrid_scenario
        )

        self.logger.info(
            "All scenarios registered."
        )

    # ==================================================
    # Campaign Order
    # ==================================================

    def get_campaign_attacks(self) -> list:

        return [

            # Network
            self.attacks["dos"],
            self.attacks["replay"],
            self.attacks["packet_delay"],
            self.attacks["packet_drop"],
            self.attacks["mqtt_hijack"],

            # Sensor
            self.attacks["spoof"],
            self.attacks["false_data"],
            self.attacks["drift"],
            self.attacks["freeze"],
            self.attacks["noise"],

            # PLC
            self.attacks["command_injection"],
            self.attacks["unauthorized"],
            self.attacks["setpoint"],

            # Process
            self.attacks["motor"],
            self.attacks["valve"],

            # Stealth
            self.attacks["intermittent"],
            self.attacks["slow_drift"],
        ]