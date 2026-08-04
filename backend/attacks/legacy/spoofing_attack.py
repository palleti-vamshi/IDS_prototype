"""
Spoofing Attack

Purpose:
    Simulates a fake sensor impersonating a legitimate device.
"""

import random
from datetime import datetime

from backend.attacks.attack_config import (
    SPOOFING_ATTACK_CLIENT,
    SPOOFING_PACKET_INTERVAL,
    SPOOFING_ATTACK_DURATION,
)

from backend.attacks.attack_utils import choose_fake_sensor
from backend.attacks.base_attack import BaseAttack


class SpoofingAttack(BaseAttack):
    """MQTT Sensor Spoofing Attack."""

    def __init__(self):
        super().__init__(
            attack_name="Spoofing Attack",
            client_id=SPOOFING_ATTACK_CLIENT,
            interval=SPOOFING_PACKET_INTERVAL,
            duration=SPOOFING_ATTACK_DURATION,
        )

        self.packet_count = 0

    def execute(self):
        """Publish a spoofed sensor packet."""

        self.packet_count += 1

        sensor = choose_fake_sensor()

        # Spoofing uses realistic values, only identity is fake
        if sensor["sensor_type"] == "temperature":
            value = round(random.uniform(27.0, 30.0), 2)
        else:
            value = round(random.uniform(100.5, 102.5), 2)

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
            f"Spoofed Packet #{self.packet_count} | "
            f"{sensor['sensor_type']}={value} {sensor['unit']} "
            f"→ {sensor['topic']}"
        )


if __name__ == "__main__":
    attack = SpoofingAttack()

    try:
        attack.start()

    except KeyboardInterrupt:
        attack.stop()