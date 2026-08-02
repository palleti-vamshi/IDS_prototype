"""
Supported industrial sensor types.
"""

from enum import Enum


class SensorType(Enum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    CURRENT = "current"
    VOLTAGE = "voltage"
    FLOW = "flow"
    RPM = "rpm"
    VIBRATION = "vibration"
    HUMIDITY = "humidity"
    LEVEL = "level"
    PROXIMITY = "proximity"