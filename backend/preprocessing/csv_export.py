"""
Exports labeled records to a CSV file.
"""

import csv
from dataclasses import asdict

from backend.preprocessing.schemas import LabeledRecord


class CSVExporter:
    """Exports labeled records to CSV."""

    def export(self, records: list[LabeledRecord], output_file: str) -> None:
        """
        Export records to a CSV file.
        """

        if not records:
            print("No records to export.")
            return

        with open(output_file, "w", newline="", encoding="utf-8") as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=asdict(records[0]).keys(),
            )

            writer.writeheader()

            for record in records:
                writer.writerow(asdict(record))

        print(f"Dataset exported successfully to {output_file}")