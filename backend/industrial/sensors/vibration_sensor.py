"""
Vibration Sensor Module

Purpose:
    Industrial vibration sensor.
"""

import random

from backend.industrial.common import SensorType
from backend.industrial.config.mqtt_config import (
    VIBRATION_TOPIC,
    VIBRATION_SENSOR_CLIENT,
)
from backend.industrial.sensors.base_sensor import BaseSensor


class VibrationSensor(BaseSensor):
    """Industrial Vibration Sensor."""

    def __init__(
        self,
        sensor_code: str = "VIB-001",
        device_id: str = "vibration_sensor_01",
    ):

        super().__init__(
            sensor_code=sensor_code,
            device_id=device_id,
            sensor_type=SensorType.VIBRATION.value,
            unit="g",
            topic=VIBRATION_TOPIC,
            client_id=VIBRATION_SENSOR_CLIENT,
            interval=2,
        )

    def generate_value(self) -> float:

        if (
            self.attached_machine is not None
            and hasattr(self.attached_machine, "vibration")
        ):
            return self.attached_machine.vibration

        return random.uniform(0.1, 1.5)