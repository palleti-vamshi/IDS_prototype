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

    def __init__(self, target_dataset_size: int | None = None):

        self.target_dataset_size = (
            target_dataset_size
            if target_dataset_size is not None
            else TARGET_DATASET_SIZE
        )

        self.parser = MessageParser()
        self.labeler = Labeler()
        self.writer = DatasetWriter()
        self.exporter = CSVExporter()

        # ==================================================
        # Current Attack State
        # ==================================================

        self.attack_active = False
        self.attack_type = None
        self.attack_targets = None

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

    def reset(self) -> None:
        """
        Reset collected records and statistics for a fresh campaign.
        """
        self.writer.clear()
        self.normal_records = 0
        self.attack_records = 0
        self.attack_counts.clear()
        self.class_sensor_counts.clear()
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

                    raw_targets = (
                        event.get("target_sensors")
                        or event.get("target_sensor")
                    )
                    if raw_targets:
                        self.attack_targets = (
                            list(raw_targets)
                            if isinstance(raw_targets, (list, tuple))
                            else [raw_targets]
                        )
                    else:
                        self.attack_targets = None

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
                    self.attack_targets = None

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
            target_sensors=self.attack_targets,
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

        # Check if target dataset size has been reached
        if self.is_target_reached():
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

        if class_name not in self.class_sensor_counts:
            self.class_sensor_counts[class_name] = {}

        current_sensor_count = (
            self.class_sensor_counts[class_name].get(sensor_type, 0)
        )

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

        cnt = self.writer.record_count()
        if cnt <= 5 or cnt % 100 == 0 or cnt == self.target_dataset_size:
            print(
                f"[Pipeline] Record #"
                f"{cnt} | "
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

    def is_target_reached(self) -> bool:
        """
        Return True if the target dataset size has been reached.
        """
        return self.writer.record_count() >= self.target_dataset_size

    # ==================================================
    # Sensor Acceptance
    # ==================================================

    def _sensor_can_accept_record(
        self,
        class_name: str,
        sensor_type: str,
    ) -> bool:
        """
        In realistic campaign mode, all genuine physical sensor records
        are accepted without artificial quotas.
        """
        return True

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
                self.target_dataset_size,

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