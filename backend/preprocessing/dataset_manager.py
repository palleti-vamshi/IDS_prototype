"""
Coordinates the preprocessing pipeline.
"""

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

    def process_message(
        self,
        message: RawMQTTMessage,
        attack_active: bool = False,
        attack_type: str | None = None,
    ) -> None:

        parsed = self.parser.parse(message)

        labeled = self.labeler.label(
            parsed,
            attack_active,
            attack_type,
        )

        self.writer.add_record(labeled)

        print(f"[Pipeline] Stored Record #{self.writer.record_count()} | "
                f"{labeled.device_id} | "
                f"{labeled.sensor_type} | "
                f"Label={labeled.label}")
    def export_dataset(self, output_file: str) -> None:
        self.exporter.export(
            self.writer.get_records(),
            output_file,
        )