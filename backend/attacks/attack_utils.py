"""
Attack Utilities

Shared helper functions for attack modules.
"""

import random

from backend.attacks.attack_config import (
    TEMPERATURE_TOPIC,
    PRESSURE_TOPIC,
    TEMPERATURE_SENSOR,
    PRESSURE_SENSOR,
    FAKE_TEMPERATURE_SENSOR,
    FAKE_PRESSURE_SENSOR,
)


def choose_real_sensor():
    """Randomly choose a legitimate sensor."""

    if random.choice([True, False]):
        return {
            "topic": TEMPERATURE_TOPIC,
            "device_id": TEMPERATURE_SENSOR,
            "sensor_type": "temperature",
            "unit": "°C",
        }

    return {
        "topic": PRESSURE_TOPIC,
        "device_id": PRESSURE_SENSOR,
        "sensor_type": "pressure",
        "unit": "kPa",
    }


def choose_fake_sensor():
    """Randomly choose a spoofed sensor."""

    if random.choice([True, False]):
        return {
            "topic": TEMPERATURE_TOPIC,
            "device_id": FAKE_TEMPERATURE_SENSOR,
            "sensor_type": "temperature",
            "unit": "°C",
        }

    return {
        "topic": PRESSURE_TOPIC,
        "device_id": FAKE_PRESSURE_SENSOR,
        "sensor_type": "pressure",
        "unit": "kPa",
    }