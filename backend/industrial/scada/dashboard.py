"""
SCADA Dashboard Backend

Receives live industrial sensor telemetry, machine status,
SCADA alarms, and cyber-attack state events from MQTT.
"""

from __future__ import annotations

from typing import Any

from backend.core.logger import setup_logger

from backend.industrial.config.mqtt_config import (
    MQTT_TOPICS,
    SCADA_CLIENT,
    ALERT_TOPIC,
    ATTACK_STATE_TOPIC,
    MACHINE_STATUS_TOPIC,
)

from backend.industrial.mqtt.subscriber import (
    MQTTSubscriber,
)


class SCADADashboard:
    """Receives and stores live industrial SCADA information."""

    def __init__(self) -> None:

        self.logger = setup_logger(
            "SCADA Dashboard"
        )

        self.latest_data: dict[str, Any] = {}

        self.subscriber = MQTTSubscriber(
            client_id=SCADA_CLIENT,
            message_handler=self.process_message,
        )

    # ==================================================
    # MQTT Message Processing
    # ==================================================

    def process_message(
        self,
        topic: str,
        payload: dict[str, Any],
    ) -> None:
        """Process incoming MQTT messages."""

        # ==================================================
        # SCADA ALARM
        # ==================================================

        if topic == ALERT_TOPIC:

            self.latest_data["alarm"] = {
                **payload,
                "topic": topic,
            }

            self.logger.warning(
                "SCADA Alarm | %s | %s",
                payload.get("status"),
                payload.get("message"),
            )

            return

        # ==================================================
        # ATTACK STATE
        # ==================================================

        if topic == ATTACK_STATE_TOPIC:

            self.latest_data["attack"] = {
                **payload,
                "topic": topic,
            }

            self.logger.warning(
                "SCADA Attack | %s | %s",
                payload.get("event"),
                payload.get("attack_name"),
            )

            return

        # ==================================================
        # MACHINE STATUS
        # ==================================================

        if topic == MACHINE_STATUS_TOPIC:

            self.latest_data["machines"] = {
                **payload,
                "topic": topic,
            }

            self.logger.info(
                "SCADA machine status updated | %d machines",
                len(payload.get("machines", [])),
            )

            return

        # ==================================================
        # SENSOR TELEMETRY
        # ==================================================

        sensor_type = payload.get(
            "sensor_type"
        )

        if sensor_type:

            self.latest_data[sensor_type] = {
                **payload,
                "topic": topic,
            }

            self.logger.info(
                "SCADA updated | %s | %.2f %s",
                sensor_type,
                payload.get("value", 0),
                payload.get("unit", ""),
            )

    # ==================================================
    # Start
    # ==================================================

    def start(self) -> None:
        """Start receiving SCADA MQTT data."""

        # Sensor topics
        for topic in MQTT_TOPICS:

            self.subscriber.subscribe(
                topic
            )

        # Alarm
        self.subscriber.subscribe(
            ALERT_TOPIC
        )

        # Attack state
        self.subscriber.subscribe(
            ATTACK_STATE_TOPIC
        )

        # Machine status
        self.subscriber.subscribe(
            MACHINE_STATUS_TOPIC
        )

        self.logger.info(
            "SCADA Dashboard MQTT receiver started."
        )

    # ==================================================
    # Get Current State
    # ==================================================

    def get_latest_data(
        self,
    ) -> dict[str, Any]:
        """Return latest SCADA data."""

        return self.latest_data

    # ==================================================
    # Stop
    # ==================================================

    def stop(self) -> None:
        """Stop SCADA MQTT receiver."""

        self.subscriber.disconnect()

        self.logger.info(
            "SCADA Dashboard MQTT receiver stopped."
        )


if __name__ == "__main__":

    scada = SCADADashboard()

    try:

        scada.start()

        while True:
            pass

    except KeyboardInterrupt:

        scada.stop()