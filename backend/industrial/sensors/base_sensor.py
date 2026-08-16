"""
Base Sensor Module

Purpose:
    Base class for all Industrial IoT sensors in LightX-IDS.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import uuid4

from backend.core.logger import setup_logger
from backend.industrial.Common import OperationalState
from backend.industrial.mqtt.publisher import MQTTPublisher
from backend.attacks.sensor.sensor_state import (
    SensorState,
)
from backend.attacks.stealth.stealth_state import (
    StealthState,
)


class BaseSensor(ABC):
    """
    Base class for every Industrial IoT sensor.

    Sensors DO NOT own the simulation loop.
    They simply measure machine telemetry and create MQTT packets.
    """

    def __init__(
        self,
        sensor_code: str,
        device_id: str,
        sensor_type: str,
        unit: str,
        topic: str,
        client_id: str,
        interval: int = 2,
    ) -> None:

        # ==================================================
        # Identity
        # ==================================================

        self.uuid = str(uuid4())

        self.sensor_code = sensor_code
        self.device_id = device_id

        self.sensor_type = sensor_type
        self.unit = unit

        # ==================================================
        # MQTT
        # ==================================================

        self.topic = topic
        self.publisher = MQTTPublisher(
            client_id=f"{client_id}_{sensor_code}"
        )

        # ==================================================
        # Sampling
        # ==================================================

        self.interval = interval
        self.last_timestamp: datetime | None = None

        # ==================================================
        # Operational State
        # ==================================================

        self.state = OperationalState.STOPPED

        # ==================================================
        # Sensor Health
        # ==================================================

        self.health = 100.0

        # ==================================================
        # Simulation Parameters
        # ==================================================

        self.noise_level = 0.0
        self.drift = 0.0
        self.calibration_offset = 0.0

        # ==================================================
        # Runtime
        # ==================================================

        self.current_value: float | None = None

        # ==================================================
        # Relationships
        # ==================================================

        self.attached_machine: Any = None

        # ==================================================
        # Logger
        # ==================================================

        self.logger = setup_logger(device_id)

        self.logger.info(
            "%s (%s) initialized.",
            self.sensor_type,
            self.sensor_code,
        )

    # ==================================================
    # Abstract Reading
    # ==================================================

    @abstractmethod
    def generate_value(self) -> float:
        """
        Read the current machine value.
        """
        raise NotImplementedError

    # ==================================================
    # Machine Association
    # ==================================================

    def attach_machine(
        self,
        machine: Any,
    ) -> None:

        self.attached_machine = machine

    def detach_machine(self) -> None:

        self.attached_machine = None

    # ==================================================
    # Configuration
    # ==================================================

    def calibrate(
        self,
        offset: float,
    ) -> None:

        self.calibration_offset = offset

    def set_noise(
        self,
        noise: float,
    ) -> None:

        self.noise_level = max(0.0, noise)

    def set_drift(
        self,
        drift: float,
    ) -> None:

        self.drift = drift

    def update_health(
        self,
        health: float,
    ) -> None:

        self.health = max(
            0.0,
            min(100.0, health),
        )

    def read(self) -> float:
        """
        Measure the current machine value.
        """

        value = self.generate_value()

        # ==========================================
        # Sensor Freeze Attack
        # ==========================================

        if (
            SensorState.freeze
            and self.current_value is not None
        ):

            value = self.current_value

        # ==========================================
        # Sensor Spoofing Attack
        # ==========================================

        elif (
            SensorState.spoofing
            and SensorState.spoof_value is not None
        ):

            value = SensorState.spoof_value

        # ==========================================
        # False Data Injection Attack
        # ==========================================

        elif SensorState.false_data:

            value = value * 1.35

        # ==========================================
        # Normal Sensor Processing
        # ==========================================

        value += self.calibration_offset

        # Physical Sensor Drift
        value += self.drift

        # Cyber Drift Attack
        value += SensorState.drift

        # ==========================================
        # Slow Drift Attack
        # ==========================================

        if StealthState.slow_drift:

            value += StealthState.drift_rate

        # ==========================================
        # Intermittent Attack
        # ==========================================

        if (
            StealthState.intermittent
            and random.random()
            < StealthState.attack_probability
        ):

            value *= 1.25

        # Physical Noise
        if self.noise_level > 0:

            value += random.uniform(
                -self.noise_level,
                self.noise_level,
            )

        # Cyber Noise Injection
        if SensorState.noise > 0:

            value += random.uniform(
                -SensorState.noise,
                SensorState.noise,
            )

        self.current_value = round(
            value,
            2,
        )

        self.last_timestamp = datetime.now()

        return self.current_value
    # ==================================================
    # MQTT Packet
    # ==================================================

    def create_packet(self) -> dict:
        """
        Create standardized MQTT packet.
        """

        return {

            "sensor_code": self.sensor_code,

            "device_id": self.device_id,

            "timestamp": (
                self.last_timestamp.isoformat()
                if self.last_timestamp
                else datetime.now().isoformat()
            ),

            "sensor_type": self.sensor_type,

            "value": self.current_value,

            "unit": self.unit,

            "status": self.state.value,

            "health": round(
                self.health,
                2,
            ),
        }

    # ==================================================
    # MQTT Publishing
    # ==================================================

    def publish(self) -> bool:
        """
        Publish the latest sensor packet.
        """

        packet = self.create_packet()

        success = self.publisher.publish(
            self.topic,
            packet,
        )

        if success:

            self.logger.info(
                "%s -> %.2f %s",
                self.sensor_code,
                packet["value"],
                self.unit,
            )

        return success

    # ==================================================
    # Lifecycle
    # ==================================================

    def start(self) -> None:
        """
        Mark sensor as active.
        """

        self.state = OperationalState.RUNNING

        self.logger.info(
            "%s started.",
            self.sensor_code,
        )

    def stop(self) -> None:
        """
        Mark sensor as stopped.
        """

        self.state = OperationalState.STOPPED

        self.publisher.disconnect()

        self.logger.info(
            "%s stopped.",
            self.sensor_code,
        )

    # ==================================================
    # Status
    # ==================================================

    def get_status(self) -> dict:

        return {

            "uuid": self.uuid,

            "sensor_code": self.sensor_code,

            "device_id": self.device_id,

            "sensor_type": self.sensor_type,

            "state": self.state.value,

            "health": self.health,

            "current_value": self.current_value,

            "noise_level": self.noise_level,

            "drift": self.drift,

            "calibration_offset": self.calibration_offset,

            "attached_machine": (
                self.attached_machine.machine_code
                if self.attached_machine
                else None
            ),
        }

    # ==================================================

    def __str__(self) -> str:

        return (
            f"{self.sensor_code}"
            f" ({self.sensor_type})"
        )