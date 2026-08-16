"""
Voltage Sensor Module

Purpose:
    Industrial voltage sensor.
"""

import random

from backend.industrial.Common import SensorType
from backend.industrial.config.mqtt_config import (
    VOLTAGE_TOPIC,
    VOLTAGE_SENSOR_CLIENT,
)
from backend.industrial.sensors.base_sensor import BaseSensor


class VoltageSensor(BaseSensor):
    """Industrial Voltage Sensor."""

    def __init__(
        self,
        sensor_code: str = "VLT-001",
        device_id: str = "voltage_sensor_01",
    ):

        super().__init__(
            sensor_code=sensor_code,
            device_id=device_id,
            sensor_type=SensorType.VOLTAGE.value,
            unit="V",
            topic=VOLTAGE_TOPIC,
            client_id=VOLTAGE_SENSOR_CLIENT,
            interval=2,
        )

    def generate_value(self) -> float:

        if (
            self.attached_machine is not None
            and hasattr(self.attached_machine, "voltage")
        ):
            return self.attached_machine.voltage

        return random.uniform(220.0, 240.0)