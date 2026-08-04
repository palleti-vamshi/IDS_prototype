"""
network_scenarios.py

Network attack scenarios for LightX-IDS.
"""

from __future__ import annotations

from backend.attacks.scenarios.scenario import (
    AttackScenario,
)


class NetworkScenario(AttackScenario):
    """
    Standard network attack scenario.
    """

    def __init__(
        self,
        dos_attack,
        replay_attack,
        packet_delay_attack,
        packet_drop_attack,
        mqtt_hijack_attack,
    ) -> None:

        super().__init__(
            "network"
        )

        self.dos_attack = dos_attack
        self.replay_attack = replay_attack
        self.packet_delay_attack = packet_delay_attack
        self.packet_drop_attack = packet_drop_attack
        self.mqtt_hijack_attack = mqtt_hijack_attack

    # ==========================================
    # Build Scenario
    # ==========================================

    def build(self) -> None:

        self.events.clear()

        self.add_attack(
            self.dos_attack,
            10.0,
        )

        self.add_attack(
            self.replay_attack,
            40.0,
        )

        self.add_attack(
            self.packet_delay_attack,
            70.0,
        )

        self.add_attack(
            self.packet_drop_attack,
            100.0,
        )

        self.add_attack(
            self.mqtt_hijack_attack,
            130.0,
        )