"""
CSV Dataset Exporter for LightX-IDS.

Exports labeled records with clean, standardized column names.
"""

import csv
import os
from dataclasses import asdict

from backend.preprocessing.schemas import LabeledRecord


class CSVExporter:
    """Exports labeled records to a clean CSV dataset."""

    FIELDNAMES = [
        "timestamp",
        "topic",
        "device_id",
        "sensor_type",
        "value",
        "unit",
        "status",
        "attack_type",
        "label",
        "source",
        "sequence_number",
    ]

    def export(
        self,
        records: list[LabeledRecord],
        output_file: str,
    ) -> None:
        """
        Export labeled records to CSV.

        Guarantees:
        - Standardized column names
        - No accidental whitespace in headers
        - UTF-8 encoding
        - Consistent column order
        """

        if not records:
            print("⚠️ No records to export.")
            return

        # Create parent directory if required
        directory = os.path.dirname(output_file)

        if directory:
            os.makedirs(
                directory,
                exist_ok=True,
            )

        with open(
            output_file,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=self.FIELDNAMES,
                extrasaction="ignore",
            )

            writer.writeheader()

            for record in records:

                data = asdict(record)

                # Ensure every exported row follows
                # the exact dataset schema.
                writer.writerow(
                    {
                        field: data.get(field)
                        for field in self.FIELDNAMES
                    }
                )

        print(
            f"✅ Dataset exported successfully: "
            f"{output_file}"
        )

        print(
            f"📊 Records exported: {len(records)}"
        )