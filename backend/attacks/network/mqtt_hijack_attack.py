"""
mqtt_topic_hijacking.py

Advanced MQTT Topic Hijacking Attack
"""

from __future__ import annotations

from backend.attacks.network.network_attack import (
    NetworkAttack,
)
from backend.attacks.network.network_state import (
    NetworkState,
)


class MQTTTopicHijackingAttack(NetworkAttack):
    """
    Redirects MQTT packets to a malicious topic.
    """

    def __init__(
        self,
        attack_id: str = "NET_005",
        duration: float = 20.0,
    ) -> None:

        super().__init__(
            attack_id=attack_id,
            attack_name="MQTT Topic Hijacking",
            duration=duration,
        )

        self.fake_topic = "attacker/hijacked"

        self.hijacked_packets = 0

    # ==========================================
    # Modify Topic
    # ==========================================

    def modify_topic(
        self,
        topic: str,
    ) -> str:

        if not self.is_running:

            return topic

        self.hijacked_packets += 1

        if (
            self.communication is not None
            and self.communication.statistics
            is not None
        ):

            self.communication.statistics.packet_duplicated()

        return self.fake_topic

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
        self,
        dt: float,
    ) -> None:

        NetworkState.hijacked_topic = (
            self.fake_topic
        )

    # ==========================================
    # Status
    # ==========================================

    def get_status(
        self,
    ) -> dict:

        status = super().get_status()

        status.update(

            {
                "fake_topic":
                    self.fake_topic,

                "hijacked_packets":
                    self.hijacked_packets,
            }

        )

        return status

    # ==========================================
    # Stop
    # ==========================================

    def stop(
        self,
    ) -> None:

        self.hijacked_packets = 0

        NetworkState.hijacked_topic = None

        super().stop()