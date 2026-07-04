"""
Base Sensor Module

Purpose:
    Provides a reusable base class for all virtual industrial sensors.
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime

from backend.core.logger import setup_logger
from backend.industrial.mqtt.publisher import MQTTPublisher


class BaseSensor(ABC):
    """
    Abstract base class for all virtual sensors.
    """

    def __init__(
        self,
        device_id: str,
        sensor_type: str,
        unit: str,
        topic: str,
        client_id: str,
        interval: int = 2,
    ):
        self.device_id = device_id
        self.sensor_type = sensor_type
        self.unit = unit
        self.topic = topic
        self.interval = interval

        self.logger = setup_logger(device_id)
        self.publisher = MQTTPublisher(client_id)

        self.running = False

    @abstractmethod
    def generate_value(self) -> float:
        """
        Generate the current sensor value.
        """
        pass

    def create_packet(self) -> dict:
        """
        Create a standardized MQTT packet.
        """

        return {
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "sensor_type": self.sensor_type,
            "value": self.generate_value(),
            "unit": self.unit,
            "status": "NORMAL",
        }

    def start(self):
        """
        Start publishing sensor data.
        """

        self.running = True

        self.logger.info("Sensor started.")

        while self.running:

            packet = self.create_packet()

            self.logger.info(
                f"Generated {packet['value']} {self.unit} → Publishing to {self.topic}"
            )

            success = self.publisher.publish(
                self.topic,
                packet,
            )

            if not success:
                self.logger.error("Failed to publish sensor data.")

            time.sleep(self.interval)

    def stop(self):
        """
        Stop the sensor.
        """

        self.running = False

        self.publisher.disconnect()

        self.logger.info("Sensor stopped.")