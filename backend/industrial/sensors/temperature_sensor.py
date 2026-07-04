"""
Temperature Sensor Module

Purpose:
    Simulates a virtual industrial temperature sensor.
"""

import random

from backend.industrial.config.mqtt_config import (
    TEMPERATURE_TOPIC,
    TEMP_SENSOR_CLIENT,
)

from backend.industrial.sensors.base_sensor import BaseSensor


class TemperatureSensor(BaseSensor):
    """Virtual Temperature Sensor."""

    def __init__(self):
        super().__init__(
            device_id="temperature_sensor_01",
            sensor_type="temperature",
            unit="°C",
            topic=TEMPERATURE_TOPIC,
            client_id=TEMP_SENSOR_CLIENT,
            interval=2,
        )

    def generate_value(self) -> float:
        """
        Generate a realistic temperature value.
        """
        return round(random.uniform(27.0, 30.0), 1)


if __name__ == "__main__":
    sensor = TemperatureSensor()

    try:
        sensor.start()
    except KeyboardInterrupt:
        sensor.stop()