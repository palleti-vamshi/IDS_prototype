"""
Proximity Sensor Module

Purpose:
    Industrial proximity sensor.
"""

import random

from backend.industrial.common import SensorType
from backend.industrial.config.mqtt_config import (
    PROXIMITY_TOPIC,
    PROXIMITY_SENSOR_CLIENT,
)
from backend.industrial.sensors.base_sensor import BaseSensor


class ProximitySensor(BaseSensor):
    """Industrial Proximity Sensor."""

    def __init__(
        self,
        sensor_code: str = "PRX-001",
        device_id: str = "proximity_sensor_01",
    ):

        super().__init__(
            sensor_code=sensor_code,
            device_id=device_id,
            sensor_type=SensorType.PROXIMITY.value,
            unit="mm",
            topic=PROXIMITY_TOPIC,
            client_id=PROXIMITY_SENSOR_CLIENT,
            interval=2,
        )

    def generate_value(self) -> float:

        if (
            self.attached_machine is not None
            and hasattr(self.attached_machine, "distance")
        ):
            return self.attached_machine.distance

        return random.uniform(5.0, 500.0)