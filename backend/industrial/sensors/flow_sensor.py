"""
Flow Sensor Module

Purpose:
    Industrial flow sensor.
"""

import random

from backend.industrial.common import SensorType
from backend.industrial.config.mqtt_config import (
    FLOW_TOPIC,
    FLOW_SENSOR_CLIENT,
)
from backend.industrial.sensors.base_sensor import BaseSensor


class FlowSensor(BaseSensor):
    """Industrial Flow Sensor."""

    def __init__(
        self,
        sensor_code: str = "FLW-001",
        device_id: str = "flow_sensor_01",
    ):

        super().__init__(
            sensor_code=sensor_code,
            device_id=device_id,
            sensor_type=SensorType.FLOW.value,
            unit="L/min",
            topic=FLOW_TOPIC,
            client_id=FLOW_SENSOR_CLIENT,
            interval=2,
        )

    def generate_value(self) -> float:

        if (
            self.attached_machine is not None
            and hasattr(self.attached_machine, "flow_rate")
        ):
            return self.attached_machine.flow_rate

        return random.uniform(40.0, 90.0)