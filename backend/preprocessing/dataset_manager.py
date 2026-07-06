"""
Coordinates the preprocessing pipeline.
"""

import json

from backend.industrial.config.mqtt_config import ATTACK_STATE_TOPIC
from backend.preprocessing.parser import MessageParser
from backend.preprocessing.labeler import Labeler
from backend.preprocessing.dataset_writer import DatasetWriter
from backend.preprocessing.csv_export import CSVExporter
from backend.preprocessing.schemas import RawMQTTMessage


class DatasetManager:
    """Coordinates dataset generation."""

    def __init__(self):
        self.parser = MessageParser()
        self.labeler = Labeler()
        self.writer = DatasetWriter()
        self.exporter = CSVExporter()

        # Current attack state
        self.attack_active = False
        self.attack_type = None

    def process_message(
        self,
        message: RawMQTTMessage,
    ) -> None:
        """
        Process a raw MQTT message through the preprocessing pipeline.
        """

        # ==========================================
        # Handle attack state events
        # ==========================================
        if message.topic == ATTACK_STATE_TOPIC:

            try:
                event = json.loads(message.payload)

                if event.get("event") == "start":

                    self.attack_active = True
                    self.attack_type = event.get("attack")

                    print(
                        f"\n🚨 Attack Started -> {self.attack_type}\n"
                    )

                elif event.get("event") == "stop":

                    print(
                        f"\n✅ Attack Ended -> {self.attack_type}\n"
                    )

                    self.attack_active = False
                    self.attack_type = None

            except json.JSONDecodeError:
                print("❌ Invalid attack event received.")

            return

        # ==========================================
        # Handle sensor messages
        # ==========================================

        parsed = self.parser.parse(message)

        if parsed is None:
            return

        labeled = self.labeler.label(
            record=parsed,
            attack_active=self.attack_active,
            attack_type=self.attack_type,
        )

        self.writer.add_record(labeled)

        print(
            f"[Pipeline] Record #{self.writer.record_count()} | "
            f"{labeled.device_id} | "
            f"{labeled.sensor_type} | "
            f"Attack={labeled.attack_type} | "
            f"Label={labeled.label}"
        )

    def export_dataset(self, output_file: str) -> None:
        """Export the collected dataset."""

        self.exporter.export(
            self.writer.get_records(),
            output_file,
        )