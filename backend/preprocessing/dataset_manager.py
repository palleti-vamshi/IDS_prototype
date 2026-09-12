"""
Dataset Manager

Coordinates the preprocessing pipeline.

Phase 3:
    • Tracks total records
    • Tracks normal records
    • Tracks per-attack records
    • Enforces dynamic per-class quotas
    • Enforces balanced per-class sensor distribution
    • Provides class distribution statistics
"""

import json
import math

from backend.industrial.config.mqtt_config import ATTACK_STATE_TOPIC

from backend.preprocessing.parser import MessageParser
from backend.preprocessing.labeler import Labeler
from backend.preprocessing.dataset_writer import DatasetWriter
from backend.preprocessing.csv_export import CSVExporter

from backend.preprocessing.schemas import RawMQTTMessage

from backend.preprocessing.generation_config import (
    CLASS_QUOTAS,
    ALL_CLASSES,
    ATTACK_CLASSES,
    NORMAL_CLASS,
    TARGET_DATASET_SIZE,
)


class DatasetManager:
    """Coordinates dataset generation."""

    def __init__(self):

        self.parser = MessageParser()
        self.labeler = Labeler()
        self.writer = DatasetWriter()
        self.exporter = CSVExporter()

        # ==================================================
        # Current Attack State
        # ==================================================

        self.attack_active = False
        self.attack_type = None

        # ==================================================
        # Phase 3 Statistics
        # ==================================================

        self.normal_records = 0
        self.attack_records = 0

        self.attack_counts = {}

        # ==================================================
        # Class × Sensor Tracking
        # ==================================================

        self.class_sensor_counts = {}

        # ==================================================
        # Quota Statistics
        # ==================================================

        self.quota_rejected_records = 0

        self.sensor_quota_rejected_records = 0

    # ==================================================
    # Sensor Types
    # ==================================================

    @staticmethod
    def _sensor_types() -> tuple[str, ...]:
        """
        Sensor types currently produced by the
        industrial simulator.

        The order is fixed so remainder distribution
        stays deterministic.
        """

        return (
            "temperature",
            "pressure",
            "current",
            "rpm",
            "vibration",
            "voltage",
            "flow",
            "level",
            "humidity",
            "proximity",
        )

    # ==================================================
    # Process MQTT Message
    # ==================================================

    def process_message(
        self,
        message: RawMQTTMessage,
    ) -> None:

        # ==================================================
        # Attack State Events
        # ==================================================

        if message.topic == ATTACK_STATE_TOPIC:

            try:

                event = json.loads(
                    message.payload
                )

                event_type = event.get("event")

                if event_type == "start":

                    self.attack_active = True

                    self.attack_type = (
                        event.get("attack")
                    )

                    print(
                        f"\n🚨 Attack Started -> "
                        f"{self.attack_type}\n"
                    )

                elif event_type == "stop":

                    print(
                        f"\n✅ Attack Ended -> "
                        f"{self.attack_type}\n"
                    )

                    self.attack_active = False
                    self.attack_type = None

            except json.JSONDecodeError:

                print(
                    "❌ Invalid attack event received."
                )

            return

        # ==================================================
        # Parse Sensor Message
        # ==================================================

        parsed = self.parser.parse(message)

        if parsed is None:
            return

        # ==================================================
        # Label Record
        # ==================================================

        labeled = self.labeler.label(
            record=parsed,
            attack_active=self.attack_active,
            attack_type=self.attack_type,
        )

        # ==================================================
        # Determine Dataset Class
        # ==================================================

        if labeled.label == 0:

            class_name = NORMAL_CLASS

        else:

            class_name = (
                labeled.attack_type
                or "Unknown"
            )

        sensor_type = labeled.sensor_type

        # ==================================================
        # Unknown Class Protection
        # ==================================================

        if class_name not in ALL_CLASSES:

            self.quota_rejected_records += 1

            return

        # ==================================================
        # Initialize Class
        # ==================================================

        if class_name not in self.class_sensor_counts:

            self.class_sensor_counts[
                class_name
            ] = {}

        # ==================================================
        # HARD CLASS QUOTA
        # ==================================================

        class_quota = self.class_quota(
            class_name
        )

        if (
            self.class_count(class_name)
            >= class_quota
        ):

            self.quota_rejected_records += 1

            return

        # ==================================================
        # SENSOR BALANCE
        # ==================================================

        sensor_quota = self._sensor_quota(
            class_name
        )

        current_sensor_count = (
            self.class_sensor_counts[
                class_name
            ].get(
                sensor_type,
                0,
            )
        )

        # --------------------------------------------------
        # If this sensor already reached its base quota,
        # allow the remainder logic to decide whether it
        # can receive one additional record.
        # --------------------------------------------------

        if not self._sensor_can_accept_record(
            class_name,
            sensor_type,
        ):

            self.sensor_quota_rejected_records += 1

            return

        # ==================================================
        # Store Record
        # ==================================================

        self.writer.add_record(
            labeled
        )

        # ==================================================
        # Update Class × Sensor Statistics
        # ==================================================

        self.class_sensor_counts[
            class_name
        ][
            sensor_type
        ] = (
            current_sensor_count + 1
        )

        # ==================================================
        # Update General Statistics
        # ==================================================

        if labeled.label == 0:

            self.normal_records += 1

        else:

            self.attack_records += 1

            attack_name = (
                labeled.attack_type
                or "Unknown"
            )

            self.attack_counts[
                attack_name
            ] = (
                self.attack_counts.get(
                    attack_name,
                    0,
                )
                + 1
            )

        # ==================================================
        # Pipeline Log
        # ==================================================

        print(
            f"[Pipeline] Record #"
            f"{self.writer.record_count()} | "
            f"Class={class_name} | "
            f"Sensor={sensor_type} | "
            f"Device={labeled.device_id} | "
            f"Attack={labeled.attack_type} | "
            f"Label={labeled.label}"
        )

    # ==================================================
    # Class Quota
    # ==================================================

    def class_quota(
        self,
        class_name: str,
    ) -> int:
        """
        Return the configured quota for a class.
        """

        return CLASS_QUOTAS.get(
            class_name,
            0,
        )

    # ==================================================
    # Sensor Quota
    # ==================================================

    def _sensor_quota(
        self,
        class_name: str,
    ) -> int:
        """
        Return the base number of records allowed
        for each sensor type within a class.

        Example for 55 records and 10 sensors:

            55 // 10 = 5

        Five records are guaranteed for every sensor.
        The remaining five records are distributed
        deterministically across the first five sensors.

        Therefore:

            5, 5, 5, 5, 5, 6, 6, 6, 6, 6

        Total = 55.
        """

        class_quota = self.class_quota(
            class_name
        )

        sensor_count = len(
            self._sensor_types()
        )

        if sensor_count == 0:

            return class_quota

        return max(
            1,
            class_quota // sensor_count,
        )

    # ==================================================
    # Sensor Acceptance
    # ==================================================

    def _sensor_can_accept_record(
        self,
        class_name: str,
        sensor_type: str,
    ) -> bool:
        """
        Decide whether a sensor can accept another
        record while keeping the class balanced.

        The class quota is divided as evenly as possible
        among all ten sensor types.

        Example:

            Class quota = 55
            Sensors = 10

            5 sensors receive 6 records
            5 sensors receive 5 records
        """

        sensors = self._sensor_types()

        if sensor_type not in sensors:

            return False

        class_quota = self.class_quota(
            class_name
        )

        if class_quota <= 0:

            return False

        sensor_count = len(sensors)

        base_quota = (
            class_quota
            // sensor_count
        )

        remainder = (
            class_quota
            % sensor_count
        )

        sensor_index = sensors.index(
            sensor_type
        )

        # First `remainder` sensors receive
        # one additional record.

        allowed_quota = base_quota

        if sensor_index < remainder:

            allowed_quota += 1

        current_count = (
            self.class_sensor_counts
            .get(
                class_name,
                {},
            )
            .get(
                sensor_type,
                0,
            )
        )

        return current_count < allowed_quota

    # ==================================================
    # Record Count
    # ==================================================

    def record_count(
        self,
    ) -> int:

        return self.writer.record_count()

    # ==================================================
    # Normal Count
    # ==================================================

    def normal_count(
        self,
    ) -> int:

        return self.normal_records

    # ==================================================
    # Attack Count
    # ==================================================

    def attack_count(
        self,
        attack_name: str,
    ) -> int:

        return self.attack_counts.get(
            attack_name,
            0,
        )

    # ==================================================
    # Generic Class Count
    # ==================================================

    def class_count(
        self,
        class_name: str,
    ) -> int:

        if class_name == NORMAL_CLASS:

            return self.normal_records

        return self.attack_counts.get(
            class_name,
            0,
        )

    # ==================================================
    # Class × Sensor Count
    # ==================================================

    def class_sensor_count(
        self,
        class_name: str,
        sensor_type: str,
    ) -> int:
        """
        Return number of records collected for a
        specific class and sensor type.
        """

        return (
            self.class_sensor_counts
            .get(
                class_name,
                {},
            )
            .get(
                sensor_type,
                0,
            )
        )

    # ==================================================
    # Sensor Distribution
    # ==================================================

    def get_sensor_distribution(
        self,
    ) -> dict:
        """
        Return class × sensor distribution.
        """

        return {
            class_name: dict(
                sensor_counts
            )
            for class_name, sensor_counts
            in self.class_sensor_counts.items()
        }

    # ==================================================
    # Quota Status
    # ==================================================

    def class_quota_reached(
        self,
        class_name: str,
    ) -> bool:

        return (
            self.class_count(
                class_name
            )
            >= self.class_quota(
                class_name
            )
        )

    # ==================================================
    # Sensor Quota Status
    # ==================================================

    def sensor_quota_reached(
        self,
        class_name: str,
        sensor_type: str,
    ) -> bool:

        return not self._sensor_can_accept_record(
            class_name,
            sensor_type,
        )

    # ==================================================
    # Rejected Records
    # ==================================================

    def rejected_count(
        self,
    ) -> int:

        return self.quota_rejected_records

    # ==================================================
    # Sensor Rejected Records
    # ==================================================

    def sensor_rejected_count(
        self,
    ) -> int:

        return (
            self.sensor_quota_rejected_records
        )

    # ==================================================
    # Distribution
    # ==================================================

    def get_distribution(
        self,
    ) -> dict:

        return {

            "total":
                self.record_count(),

            "normal":
                self.normal_records,

            "attack":
                self.attack_records,

            "attacks":
                dict(
                    self.attack_counts
                ),

            "class_sensor_distribution":
                self.get_sensor_distribution(),

            "quota_rejected":
                self.quota_rejected_records,

            "sensor_quota_rejected":
                self.sensor_quota_rejected_records,

            "target":
                TARGET_DATASET_SIZE,

            "class_quotas":
                dict(CLASS_QUOTAS),
        }

    # ==================================================
    # Export
    # ==================================================

    def export_dataset(
        self,
        output_file: str,
    ) -> None:

        self.exporter.export(
            self.writer.get_records(),
            output_file,
        )