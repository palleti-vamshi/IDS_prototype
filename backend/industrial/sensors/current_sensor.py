"""
Current Sensor Module

Purpose:
    Industrial current sensor.
"""

import random

from backend.industrial.Common import SensorType
from backend.industrial.config.mqtt_config import (
    CURRENT_TOPIC,
    CURRENT_SENSOR_CLIENT,
)
from backend.industrial.communication.communication_controller import (
    CommunicationController,
)
from backend.industrial.sensors.base_sensor import BaseSensor


class CurrentSensor(BaseSensor):
    """Industrial Current Sensor."""

    def __init__(
        self,
        sensor_code: str = "CUR-001",
        device_id: str = "current_sensor_01",
        communication: CommunicationController | None = None,
    ):

        super().__init__(
            sensor_code=sensor_code,
            device_id=device_id,
            sensor_type=SensorType.CURRENT.value,
            unit="A",
            topic=CURRENT_TOPIC,
            client_id=CURRENT_SENSOR_CLIENT,
            interval=2,
            communication=communication,
        )

    def generate_value(self) -> float:

        if (
            self.attached_machine is not None
            and hasattr(self.attached_machine, "current")
        ):
            return self.attached_machine.current

        return random.uniform(4.5, 15.0)