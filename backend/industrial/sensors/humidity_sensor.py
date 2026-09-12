"""
Humidity Sensor Module

Purpose:
    Industrial humidity sensor.
"""

import random

from backend.industrial.Common import SensorType
from backend.industrial.communication.communication_controller import (
    CommunicationController,
)
from backend.industrial.config.mqtt_config import (
    HUMIDITY_TOPIC,
    HUMIDITY_SENSOR_CLIENT,
)
from backend.industrial.sensors.base_sensor import BaseSensor


class HumiditySensor(BaseSensor):
    """Industrial Humidity Sensor."""

    def __init__(
        self,
        sensor_code: str = "HUM-001",
        device_id: str = "humidity_sensor_01",
        communication: CommunicationController | None = None,
    ):

        super().__init__(
            sensor_code=sensor_code,
            device_id=device_id,
            sensor_type=SensorType.HUMIDITY.value,
            unit="%",
            topic=HUMIDITY_TOPIC,
            client_id=HUMIDITY_SENSOR_CLIENT,
            interval=2,
            communication=communication,
        )

    def generate_value(self) -> float:

        if (
            self.attached_machine is not None
            and hasattr(self.attached_machine, "humidity")
        ):
            return self.attached_machine.humidity

        return random.uniform(40.0, 70.0)