"""
Coordinates the preprocessing pipeline.

Phase 3:
    • Tracks total records
    • Tracks normal records
    • Tracks per-attack records
    • Enforces per-class quotas
    • Enforces per-class sensor distribution
    • Provides class distribution statistics
"""

import json

from backend.industrial.config.mqtt_config import ATTACK_STATE_TOPIC

from backend.preprocessing.parser import MessageParser
from backend.preprocessing.labeler import Labeler
from backend.preprocessing.dataset_writer import DatasetWriter
from backend.preprocessing.csv_export import CSVExporter

from backend.preprocessing.schemas import RawMQTTMessage

from backend.preprocessing.generation_config import (
    RECORDS_PER_CLASS,
    NORMAL_CLASS,
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
        #
        # Example:
        #
        # {
        #     "Normal": {
        #         "temperature": 1,
        #         "pressure": 1,
        #         ...
        #     },
        #
        #     "DoS Attack": {
        #         "temperature": 1,
        #         "pressure": 1,
        #         ...
        #     }
        # }
        # ==================================================

        self.class_sensor_counts = {}

        # ==================================================
        # Quota Statistics
        # ==================================================

        self.quota_rejected_records = 0

        self.sensor_quota_rejected_records = 0

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
        # Initialize Class
        # ==================================================

        if class_name not in self.class_sensor_counts:

            self.class_sensor_counts[
                class_name
            ] = {}

        # ==================================================
        # Current Sensor Count
        # ==================================================

        current_sensor_count = (
            self.class_sensor_counts[
                class_name
            ].get(
                sensor_type,
                0,
            )
        )

        # ==================================================
        # SENSOR BALANCE
        #
        # For the initial 10-record validation:
        #
        # 10 sensor types
        # 1 record per sensor type
        #
        # Therefore:
        #
        # temperature -> 1
        # pressure    -> 1
        # current     -> 1
        # ...
        #
        # This prevents "current" from becoming 37
        # while "humidity" becomes 1.
        # ==================================================

        sensor_quota = self._sensor_quota()

        if current_sensor_count >= sensor_quota:

            self.sensor_quota_rejected_records += 1

            return

        # ==================================================
        # HARD CLASS QUOTA
        # ==================================================

        if self.class_count(
            class_name
        ) >= RECORDS_PER_CLASS:

            self.quota_rejected_records += 1

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
    # Calculate Sensor Quota
    # ==================================================

    def _sensor_quota(
        self,
    ) -> int:
        """
        Determine maximum number of records allowed
        for one sensor type within a class.

        For the current validation dataset:

            RECORDS_PER_CLASS = 10
            Sensor types = 10

            10 / 10 = 1

        For larger datasets this becomes scalable.
        """

        # Sensor types currently produced by the
        # industrial simulator.

        sensor_types = {
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
        }

        sensor_type_count = len(
            sensor_types
        )

        if sensor_type_count == 0:

            return RECORDS_PER_CLASS

        quota = (
            RECORDS_PER_CLASS
            // sensor_type_count
        )

        return max(
            1,
            quota,
        )

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
            >= RECORDS_PER_CLASS
        )

    # ==================================================
    # Sensor Quota Status
    # ==================================================

    def sensor_quota_reached(
        self,
        class_name: str,
        sensor_type: str,
    ) -> bool:

        return (
            self.class_sensor_count(
                class_name,
                sensor_type,
            )
            >= self._sensor_quota()
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