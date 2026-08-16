"""
Temperature Sensor Module

Purpose:
    Industrial temperature sensor.
"""

import random

from backend.industrial.Common import SensorType
from backend.industrial.config.mqtt_config import (
    TEMPERATURE_TOPIC,
    TEMP_SENSOR_CLIENT,
)
from backend.industrial.sensors.base_sensor import BaseSensor


class TemperatureSensor(BaseSensor):
    """Industrial Temperature Sensor."""

    def __init__(
        self,
        sensor_code: str = "TMP-001",
        device_id: str = "temperature_sensor_01",
    ):

        super().__init__(
            sensor_code=sensor_code,
            device_id=device_id,
            sensor_type=SensorType.TEMPERATURE.value,
            unit="°C",
            topic=TEMPERATURE_TOPIC,
            client_id=TEMP_SENSOR_CLIENT,
            interval=2,
        )

    def generate_value(self) -> float:
        """
        Generate temperature reading.

        Prototype Mode:
            Returns simulated value.

        Digital Twin Mode:
            Reads machine temperature.
        """

        if (
            self.attached_machine is not None
            and hasattr(self.attached_machine, "temperature")
        ):
            return self.attached_machine.temperature

        return random.uniform(27.0, 30.0)


if __name__ == "__main__":

    sensor = TemperatureSensor()

    try:
        sensor.start()

    except KeyboardInterrupt:
        sensor.stop()