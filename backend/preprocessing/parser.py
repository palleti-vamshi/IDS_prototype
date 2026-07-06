"""
Parses raw MQTT messages into structured sensor records.
"""

import json
import logging

from backend.preprocessing.schemas import (
    RawMQTTMessage,
    ParsedSensorRecord,
)

logger = logging.getLogger(__name__)


class MessageParser:
    """Parses MQTT messages into structured records."""

    @staticmethod
    def parse(message: RawMQTTMessage) -> ParsedSensorRecord | None:
        """
        Convert RawMQTTMessage to ParsedSensorRecord.
        """

        try:
            payload = json.loads(message.payload)

            # Ensure payload is a JSON object
            if not isinstance(payload, dict):
                logger.warning(
                    f"Ignoring non-dictionary payload: {payload}"
                )
                return None

            return ParsedSensorRecord(
                timestamp=payload.get("timestamp"),
                topic=message.topic,
                device_id=payload.get("device_id"),
                sensor_type=payload.get("sensor_type"),
                value=float(payload.get("value")),
                unit=payload.get("unit"),
                status=payload.get("status"),
            )

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            logger.error(f"Failed to parse message: {e}")
            return None