"""
schemas.py

Defines the data models used throughout the preprocessing pipeline.

These dataclasses act as data contracts between preprocessing modules,
ensuring a consistent and type-safe flow of information from raw MQTT
messages to machine learning-ready labeled records.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class RawMQTTMessage:
    """
    Represents a raw MQTT message received from the broker.

    This object is created by the Collector before any parsing or
    preprocessing is performed.
    """

    timestamp: str
    topic: str
    payload: str
    qos: int
    retain: bool


@dataclass(slots=True)
class ParsedSensorRecord:
    """
    Represents a parsed Industrial IoT sensor message.
    """

    timestamp: str
    topic: str

    device_id: str
    sensor_type: str

    value: float
    unit: str

    status: str


@dataclass(slots=True)
class LabeledRecord:
    """Final labeled dataset record."""

    timestamp: str
    topic: str

    device_id: str
    sensor_type: str

    value: float
    unit: str
    status: str

    attack_type: Optional[str]

    label: int

    source: str

    sequence_number: int