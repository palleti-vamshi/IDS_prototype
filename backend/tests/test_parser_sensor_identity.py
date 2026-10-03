"""
Tests physical sensor identity preservation across parser, schema, and CSV exporter.
"""

import csv
import json
import os
import tempfile
import unittest

from backend.preprocessing.schemas import (
    RawMQTTMessage,
    ParsedSensorRecord,
    LabeledRecord,
)
from backend.preprocessing.parser import MessageParser
from backend.preprocessing.csv_export import CSVExporter
from backend.industrial.sensors import TemperatureSensor, CurrentSensor


class TestParserSensorIdentity(unittest.TestCase):
    """Verifies that sensor_code is preserved and not confused with device_id or sensor_type."""

    def test_parse_temperature_sensor_identity(self):
        """Verify parsing of temperature sensor preserves sensor_code."""
        payload = {
            "sensor_code": "MTR-001-TMP",
            "device_id": "mtr_001_temperature_sensor",
            "sensor_type": "temperature",
            "value": 42.5,
            "unit": "°C",
            "status": "NORMAL",
            "timestamp": "2026-09-24T01:00:00",
        }
        raw_msg = RawMQTTMessage(
            timestamp="2026-09-24T01:00:00",
            topic="factory/line1/temperature",
            payload=json.dumps(payload),
            qos=0,
            retain=False,
        )

        record = MessageParser.parse(raw_msg)

        self.assertIsNotNone(record)
        self.assertIsInstance(record, ParsedSensorRecord)
        self.assertEqual(record.sensor_code, "MTR-001-TMP")
        self.assertEqual(record.device_id, "mtr_001_temperature_sensor")
        self.assertEqual(record.sensor_type, "temperature")
        self.assertEqual(record.value, 42.5)
        self.assertEqual(record.unit, "°C")
        self.assertEqual(record.status, "NORMAL")

        # Distinctness checks
        self.assertNotEqual(record.sensor_code, record.device_id)
        self.assertNotEqual(record.sensor_code, record.sensor_type)
        self.assertNotEqual(record.device_id, record.sensor_type)

    def test_parse_current_sensor_identity(self):
        """Verify parsing of an additional physical sensor (current) preserves sensor_code."""
        payload = {
            "sensor_code": "MTR-001-CUR",
            "device_id": "mtr_001_current_sensor",
            "sensor_type": "current",
            "value": 14.8,
            "unit": "A",
            "status": "NORMAL",
            "timestamp": "2026-09-24T01:00:01",
        }
        raw_msg = RawMQTTMessage(
            timestamp="2026-09-24T01:00:01",
            topic="factory/line1/current",
            payload=json.dumps(payload),
            qos=0,
            retain=False,
        )

        record = MessageParser.parse(raw_msg)

        self.assertIsNotNone(record)
        self.assertEqual(record.sensor_code, "MTR-001-CUR")
        self.assertEqual(record.device_id, "mtr_001_current_sensor")
        self.assertEqual(record.sensor_type, "current")

        # Distinctness checks
        self.assertNotEqual(record.sensor_code, record.device_id)
        self.assertNotEqual(record.sensor_code, record.sensor_type)

    def test_live_physical_sensor_packet_propagation(self):
        """Verify real sensor instances emit packets with sensor_code parsed correctly."""
        temp_sensor = TemperatureSensor(
            sensor_code="MTR-001-TMP",
            device_id="mtr_001_temperature_sensor",
        )
        temp_sensor.read()
        packet = temp_sensor.create_packet()

        self.assertIn("sensor_code", packet)
        self.assertEqual(packet["sensor_code"], "MTR-001-TMP")

        raw_msg = RawMQTTMessage(
            timestamp="2026-09-24T01:00:02",
            topic="factory/line1/temperature",
            payload=json.dumps(packet),
            qos=0,
            retain=False,
        )

        record = MessageParser.parse(raw_msg)
        self.assertIsNotNone(record)
        self.assertEqual(record.sensor_code, "MTR-001-TMP")
        self.assertEqual(record.device_id, "mtr_001_temperature_sensor")

    def test_backward_compatibility_legacy_packet_without_sensor_code(self):
        """Verify legacy packets without sensor_code parse safely with sensor_code=None."""
        legacy_payload = {
            "device_id": "legacy_sensor_01",
            "sensor_type": "temperature",
            "value": 28.3,
            "unit": "°C",
            "status": "NORMAL",
            "timestamp": "2026-07-06T17:43:22",
        }
        raw_msg = RawMQTTMessage(
            timestamp="2026-07-06T17:43:22",
            topic="factory/line1/temperature",
            payload=json.dumps(legacy_payload),
            qos=0,
            retain=False,
        )

        record = MessageParser.parse(raw_msg)

        self.assertIsNotNone(record)
        self.assertIsNone(record.sensor_code)
        self.assertEqual(record.device_id, "legacy_sensor_01")
        self.assertEqual(record.value, 28.3)

    def test_schema_and_csv_export_preservation(self):
        """Verify sensor_code is preserved in LabeledRecord and exported properly in CSV."""
        record = LabeledRecord(
            timestamp="2026-09-24T01:00:00",
            topic="factory/line1/temperature",
            device_id="mtr_001_temperature_sensor",
            sensor_type="temperature",
            value=42.5,
            unit="°C",
            status="NORMAL",
            attack_type=None,
            label=0,
            source="simulator",
            sequence_number=1,
            sensor_code="MTR-001-TMP",
        )

        self.assertEqual(record.sensor_code, "MTR-001-TMP")

        exporter = CSVExporter()
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test_export.csv")
            exporter.export([record], csv_path)

            self.assertTrue(os.path.exists(csv_path))

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames

                # sensor_code must be in headers, right after device_id
                self.assertIn("sensor_code", headers)
                device_idx = headers.index("device_id")
                sensor_code_idx = headers.index("sensor_code")
                self.assertEqual(sensor_code_idx, device_idx + 1)

                rows = list(reader)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["sensor_code"], "MTR-001-TMP")
                self.assertEqual(rows[0]["device_id"], "mtr_001_temperature_sensor")


if __name__ == "__main__":
    unittest.main()
