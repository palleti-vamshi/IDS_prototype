"""
Level Sensor Module

Purpose:
    Industrial tank level sensor.
"""

import random

from backend.industrial.common import SensorType
from backend.industrial.config.mqtt_config import (
    LEVEL_TOPIC,
    LEVEL_SENSOR_CLIENT,
)
from backend.industrial.sensors.base_sensor import BaseSensor


class LevelSensor(BaseSensor):
    """Industrial Level Sensor."""

    def __init__(
        self,
        sensor_code: str = "LVL-001",
        device_id: str = "level_sensor_01",
    ):

        super().__init__(
            sensor_code=sensor_code,
            device_id=device_id,
            sensor_type=SensorType.LEVEL.value,
            unit="%",
            topic=LEVEL_TOPIC,
            client_id=LEVEL_SENSOR_CLIENT,
            interval=2,
        )

    def generate_value(self) -> float:

        if (
            self.attached_machine is not None
            and hasattr(self.attached_machine, "current_level")
        ):
            return self.attached_machine.current_level

        return random.uniform(20.0, 90.0)