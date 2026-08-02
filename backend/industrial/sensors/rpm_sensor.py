"""
RPM Sensor Module

Purpose:
    Industrial RPM sensor.
"""

import random

from backend.industrial.common import SensorType
from backend.industrial.config.mqtt_config import (
    RPM_TOPIC,
    RPM_SENSOR_CLIENT,
)
from backend.industrial.sensors.base_sensor import BaseSensor


class RPMSensor(BaseSensor):
    """Industrial RPM Sensor."""

    def __init__(
        self,
        sensor_code: str = "RPM-001",
        device_id: str = "rpm_sensor_01",
    ):

        super().__init__(
            sensor_code=sensor_code,
            device_id=device_id,
            sensor_type=SensorType.RPM.value,
            unit="RPM",
            topic=RPM_TOPIC,
            client_id=RPM_SENSOR_CLIENT,
            interval=2,
        )

    def generate_value(self) -> float:

        if (
            self.attached_machine is not None
            and hasattr(self.attached_machine, "rpm")
        ):
            return self.attached_machine.rpm

        return random.uniform(1400.0, 1800.0)