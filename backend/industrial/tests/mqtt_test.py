"""
MQTT Communication Test

Purpose:
    Verifies communication between the MQTT Publisher
    and MQTT Subscriber.
"""

import time

from backend.industrial.config.mqtt_config import (
    TEMP_SENSOR_CLIENT,
    PLC_CLIENT,
    TEMPERATURE_TOPIC,
)

from backend.industrial.mqtt.publisher import MQTTPublisher
from backend.industrial.mqtt.subscriber import MQTTSubscriber


def message_received(topic, payload):
    print("\n========== MESSAGE RECEIVED ==========")
    print(f"Topic   : {topic}")
    print(f"Payload : {payload}")
    print("======================================\n")


def main():
    subscriber = MQTTSubscriber(
        client_id=PLC_CLIENT,
        message_handler=message_received,
    )

    subscriber.subscribe(TEMPERATURE_TOPIC)

    publisher = MQTTPublisher(
        client_id=TEMP_SENSOR_CLIENT,
    )

    time.sleep(1)

    publisher.publish(
        TEMPERATURE_TOPIC,
        {
            "device_id": "temperature_sensor_01",
            "value": 28.5,
            "unit": "C",
            "status": "NORMAL",
        },
    )

    time.sleep(2)

    publisher.disconnect()
    subscriber.disconnect()


if __name__ == "__main__":
    main()