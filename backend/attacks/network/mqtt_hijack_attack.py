"""
mqtt_topic_hijacking.py

MQTT Topic Hijacking Attack
"""

from __future__ import annotations

from backend.attacks.network.network_attack import NetworkAttack
from backend.attacks.network.network_state import NetworkState


class MQTTTopicHijackingAttack(NetworkAttack):
    """
    Redirects MQTT packets to a fake topic.
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

    # ==========================================
    # Packet Modification
    # ==========================================

    def modify_topic(
        self,
        topic: str,
    ) -> str:

        if self.is_running:
            return self.fake_topic

        return topic

    # ==========================================
    # Runtime
    # ==========================================

    def apply(
    self,
    dt: float,
) -> None:

        NetworkState.hijacked_topic = self.fake_topic

    # ==========================================
    # Stop
    # ==========================================

    def stop(self) -> None:

        NetworkState.hijacked_topic = None

        super().stop()