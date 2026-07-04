"""
PLC Controller Module

Purpose:
    Receives sensor data, updates factory state,
    and evaluates industrial rules.
"""

from backend.core.logger import setup_logger
from backend.industrial.config.mqtt_config import (
    PLC_CLIENT,
    TEMPERATURE_TOPIC,
    PRESSURE_TOPIC,
)
from backend.industrial.mqtt.subscriber import MQTTSubscriber
from backend.industrial.plc.rules import PLCRules
from backend.industrial.plc.state import PLCState


class PLCController:
    """Virtual PLC Controller."""

    def __init__(self):
        self.logger = setup_logger("PLC Controller")
        self.state = PLCState()

        self.subscriber = MQTTSubscriber(
            client_id=PLC_CLIENT,
            message_handler=self.process_message,
        )

    def process_message(self, topic: str, payload: dict):
        """Process incoming sensor messages."""

        sensor_type = payload.get("sensor_type")
        value = payload.get("value")

        if sensor_type == "temperature":
            self.state.update_temperature(value)

        elif sensor_type == "pressure":
            self.state.update_pressure(value)

        status = PLCRules.evaluate(
            self.state.temperature,
            self.state.pressure,
        )

        self.state.update_status(status)

        self.logger.info(
            f"Factory State: {self.state.get_state()}"
        )

    def start(self):
        """Start the PLC."""

        self.subscriber.subscribe(TEMPERATURE_TOPIC)
        self.subscriber.subscribe(PRESSURE_TOPIC)

        self.logger.info("PLC Controller started.")

    def stop(self):
        """Stop the PLC."""

        self.subscriber.disconnect()

        self.logger.info("PLC Controller stopped.")


if __name__ == "__main__":
    plc = PLCController()

    try:
        plc.start()

        while True:
            pass

    except KeyboardInterrupt:
        plc.stop()