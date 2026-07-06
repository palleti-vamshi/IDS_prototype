"""
Labels parsed sensor records.
"""

from backend.preprocessing.schemas import (
    ParsedSensorRecord,
    LabeledRecord,
)


class Labeler:

    def __init__(self):
        self.sequence_number = 0

    def label(
        self,
        record: ParsedSensorRecord,
        attack_active: bool = False,
        attack_type: str | None = None,
    ) -> LabeledRecord:

        self.sequence_number += 1

        return LabeledRecord(
            timestamp=record.timestamp,
            topic=record.topic,
            device_id=record.device_id,
            sensor_type=record.sensor_type,
            value=record.value,
            unit=record.unit,
            status=record.status,
            attack_type=attack_type,
            label=1 if attack_active else 0,
            source="simulator",
            sequence_number=self.sequence_number,
        )