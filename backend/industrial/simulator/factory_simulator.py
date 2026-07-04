"""
Factory Simulator

Purpose:
    Starts and manages the complete virtual industrial environment.
"""

import threading
import time

from backend.core.logger import setup_logger
from backend.industrial.plc.plc_controller import PLCController
from backend.industrial.sensors.pressure_sensor import PressureSensor
from backend.industrial.sensors.temperature_sensor import TemperatureSensor


class FactorySimulator:
    """Orchestrates the virtual industrial factory."""

    def __init__(self):
        self.logger = setup_logger("Factory Simulator")

        self.temperature_sensor = TemperatureSensor()
        self.pressure_sensor = PressureSensor()
        self.plc = PLCController()

        self.threads = []

    def start(self):
        """Start the virtual factory."""

        self.logger.info("Starting LightX-IDS Factory Simulator...")

        components = [
            self.temperature_sensor.start,
            self.pressure_sensor.start,
            self.plc.start,
        ]

        for component in components:
            thread = threading.Thread(
                target=component,
                daemon=True,
            )

            thread.start()
            self.threads.append(thread)

        self.logger.info("Factory started successfully.")

        try:
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the virtual factory."""

        self.logger.info("Stopping Factory Simulator...")

        self.temperature_sensor.stop()
        self.pressure_sensor.stop()
        self.plc.stop()

        self.logger.info("Factory stopped successfully.")


if __name__ == "__main__":
    simulator = FactorySimulator()
    simulator.start()