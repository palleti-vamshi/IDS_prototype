from backend.preprocessing.csv_export import CSVExporter
from backend.preprocessing.dataset_writer import DatasetWriter
from backend.preprocessing.schemas import LabeledRecord

writer = DatasetWriter()

writer.add_record(
    LabeledRecord(
        timestamp="2026-07-06T17:43:22",
        topic="factory/line1/temperature",
        device_id="temperature_sensor_01",
        sensor_type="temperature",
        value=28.3,
        unit="°C",
        status="NORMAL",
        attack_type=None,
        label=0,
        source="simulator",
        sequence_number=1,
    )
)

exporter = CSVExporter()

exporter.export(
    writer.get_records(),
    "backend/datasets/lightx_dataset.csv",
)