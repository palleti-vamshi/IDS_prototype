"""
Pressure Sensor Module

Purpose:
    Simulates a virtual industrial pressure sensor.
"""

import random

from backend.industrial.config.mqtt_config import (
    PRESSURE_TOPIC,
    PRESSURE_SENSOR_CLIENT,
)

from backend.industrial.sensors.base_sensor import BaseSensor


class PressureSensor(BaseSensor):
    """Virtual Pressure Sensor."""

    def __init__(self):
        super().__init__(
            device_id="pressure_sensor_01",
            sensor_type="pressure",
            unit="kPa",
            topic=PRESSURE_TOPIC,
            client_id=PRESSURE_SENSOR_CLIENT,
            interval=2,
        )

    def generate_value(self) -> float:
        """
        Generate a realistic pressure value.
        """
        return round(random.uniform(100.5, 102.5), 1)


if __name__ == "__main__":
    sensor = PressureSensor()

    try:
        sensor.start()
    except KeyboardInterrupt:
        sensor.stop()