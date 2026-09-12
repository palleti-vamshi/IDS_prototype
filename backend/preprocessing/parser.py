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
    """Parses raw MQTT messages into structured records."""

    @staticmethod
    def parse(
        message: RawMQTTMessage,
    ) -> ParsedSensorRecord | None:
        """
        Convert a RawMQTTMessage to ParsedSensorRecord.

        Non-sensor MQTT messages are ignored safely.
        """

        try:
            payload = json.loads(
                message.payload
            )

            # ==========================================
            # Ensure payload is a JSON object
            # ==========================================

            if not isinstance(payload, dict):

                logger.warning(
                    "Ignoring non-dictionary payload: %s",
                    payload,
                )

                return None

            # ==========================================
            # Required Sensor Fields
            # ==========================================

            device_id = payload.get(
                "device_id"
            )

            sensor_type = payload.get(
                "sensor_type"
            )

            value = payload.get(
                "value"
            )

            # ==========================================
            # Ignore Non-Sensor Messages
            # ==========================================

            if (
                device_id is None
                or sensor_type is None
                or value is None
            ):

                logger.debug(
                    "Ignoring non-sensor MQTT message "
                    "on topic: %s",
                    message.topic,
                )

                return None

            # ==========================================
            # Convert Sensor Value
            # ==========================================

            numeric_value = float(
                value
            )

            # ==========================================
            # Create Parsed Sensor Record
            # ==========================================

            return ParsedSensorRecord(

                timestamp=payload.get(
                    "timestamp"
                ),

                topic=message.topic,

                device_id=device_id,

                sensor_type=sensor_type,

                value=numeric_value,

                unit=payload.get(
                    "unit"
                ),

                status=payload.get(
                    "status"
                ),
            )

        except json.JSONDecodeError as e:

            logger.error(
                "Failed to decode MQTT JSON: %s",
                e,
            )

            return None

        except (
            TypeError,
            ValueError,
        ) as e:

            logger.error(
                "Failed to parse sensor value: %s",
                e,
            )

            return None