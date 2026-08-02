"""
Pressure Sensor Module

Purpose:
    Industrial pressure sensor.
"""

import random

from backend.industrial.common import SensorType
from backend.industrial.config.mqtt_config import (
    PRESSURE_TOPIC,
    PRESSURE_SENSOR_CLIENT,
)
from backend.industrial.sensors.base_sensor import BaseSensor


class PressureSensor(BaseSensor):
    """Industrial Pressure Sensor."""

    def __init__(
        self,
        sensor_code: str = "PRS-001",
        device_id: str = "pressure_sensor_01",
    ):

        super().__init__(
            sensor_code=sensor_code,
            device_id=device_id,
            sensor_type=SensorType.PRESSURE.value,
            unit="kPa",
            topic=PRESSURE_TOPIC,
            client_id=PRESSURE_SENSOR_CLIENT,
            interval=2,
        )

    def generate_value(self) -> float:
        """
        Generate pressure reading.

        Prototype Mode:
            Returns simulated value.

        Digital Twin Mode:
            Reads machine pressure.
        """

        if (
            self.attached_machine is not None
            and hasattr(self.attached_machine, "pressure")
        ):
            return self.attached_machine.pressure

        return random.uniform(100.5, 102.5)


if __name__ == "__main__":

    sensor = PressureSensor()

    try:
        sensor.start()

    except KeyboardInterrupt:
        sensor.stop()