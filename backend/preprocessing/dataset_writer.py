"""
Stores labeled records in memory.
"""

from backend.preprocessing.schemas import LabeledRecord


class DatasetWriter:
    """Stores labeled records before export."""

    def __init__(self):
        self.records: list[LabeledRecord] = []

    def add_record(self, record: LabeledRecord) -> None:
        """Add a record to the dataset."""
        self.records.append(record)

    def get_records(self) -> list[LabeledRecord]:
        """Return all stored records."""
        return self.records

    def clear(self) -> None:
        """Clear all stored records."""
        self.records.clear()

    def record_count(self) -> int:
        """Return total number of records."""
        return len(self.records)