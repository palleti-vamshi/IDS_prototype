"""
Tests locality-aware attack labeling in LightX-IDS preprocessing.
"""

import json
import unittest

from backend.preprocessing.schemas import (
    ParsedSensorRecord,
    RawMQTTMessage,
)
from backend.preprocessing.labeler import (
    Labeler,
    SENSOR_CODE_TO_DEVICE_ID,
    GLOBAL_NETWORK_ATTACKS,
    BROAD_SENSOR_ATTACKS,
    PLC_CONTROL_PLANE_ATTACKS,
    MACHINE_TARGETED_ATTACKS,
    DEFAULT_SENSOR_TARGETS,
)
from backend.preprocessing.dataset_manager import DatasetManager
from backend.industrial.config.mqtt_config import ATTACK_STATE_TOPIC


class TestLocalityAwareLabeling(unittest.TestCase):
    """Verifies that only records belonging to affected targets receive attack labels."""

    def setUp(self):
        self.labeler = Labeler()

        # Build records for all 19 physical sensors
        self.all_19_records: dict[str, ParsedSensorRecord] = {}
        for code, dev_id in SENSOR_CODE_TO_DEVICE_ID.items():
            self.all_19_records[code] = ParsedSensorRecord(
                timestamp="2026-09-24T02:00:00",
                topic=f"factory/test/{code}",
                device_id=dev_id,
                sensor_code=code,
                sensor_type="test",
                value=45.2,
                unit="unit",
                status="NORMAL",
            )

        self.record_target = self.all_19_records["MTR-001-TMP"]
        self.record_unrelated = self.all_19_records["MTR-001-CUR"]
        self.record_tank = self.all_19_records["TNK-001-HUM"]

    def test_targeted_attack_matching_sensor_code(self):
        """1. Targeted attack + matching sensor_code -> label 1."""
        labeled = self.labeler.label(
            record=self.record_target,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensor="MTR-001-TMP",
        )

        self.assertEqual(labeled.label, 1)
        self.assertEqual(labeled.attack_type, "Sensor Spoofing Attack")
        self.assertEqual(labeled.sensor_code, "MTR-001-TMP")

    def test_targeted_attack_unrelated_sensor_code(self):
        """2. Targeted attack + unrelated sensor_code -> label 0."""
        labeled_cur = self.labeler.label(
            record=self.record_unrelated,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensor="MTR-001-TMP",
        )

        self.assertEqual(labeled_cur.label, 0)
        self.assertIsNone(labeled_cur.attack_type)
        self.assertEqual(labeled_cur.sensor_code, "MTR-001-CUR")

        labeled_tank = self.labeler.label(
            record=self.record_tank,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensor="MTR-001-TMP",
        )

        self.assertEqual(labeled_tank.label, 0)
        self.assertIsNone(labeled_tank.attack_type)

    def test_attack_type_only_on_affected_record(self):
        """3. Targeted attack -> attack_type only on affected record, None on unaffected."""
        labeled_target = self.labeler.label(
            record=self.record_target,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensor="MTR-001-TMP",
        )
        labeled_other = self.labeler.label(
            record=self.record_unrelated,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensor="MTR-001-TMP",
        )

        self.assertEqual(labeled_target.attack_type, "Sensor Spoofing Attack")
        self.assertIsNone(labeled_other.attack_type)

    def test_multiple_targeted_sensors(self):
        """4. Multiple targeted sensors -> all explicitly targeted sensors labeled correctly."""
        record_rpm = ParsedSensorRecord(
            timestamp="2026-09-24T02:00:00",
            topic="factory/line1/rpm",
            device_id="mtr_001_rpm_sensor",
            sensor_code="MTR-001-RPM",
            sensor_type="rpm",
            value=1750.0,
            unit="RPM",
            status="NORMAL",
        )

        targets = ["MTR-001-TMP", "MTR-001-CUR"]

        # Target 1
        l1 = self.labeler.label(
            record=self.record_target,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensors=targets,
        )
        self.assertEqual(l1.label, 1)
        self.assertEqual(l1.attack_type, "Sensor Spoofing Attack")

        # Target 2
        l2 = self.labeler.label(
            record=self.record_unrelated,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensors=targets,
        )
        self.assertEqual(l2.label, 1)
        self.assertEqual(l2.attack_type, "Sensor Spoofing Attack")

        # Non-target sensor
        l3 = self.labeler.label(
            record=record_rpm,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensors=targets,
        )
        self.assertEqual(l3.label, 0)
        self.assertIsNone(l3.attack_type)

    def test_attack_stopped_records_return_to_normal(self):
        """5. Attack stopped -> records return to normal."""
        labeled = self.labeler.label(
            record=self.record_target,
            attack_active=False,
            attack_type=None,
            target_sensor="MTR-001-TMP",
        )

        self.assertEqual(labeled.label, 0)
        self.assertIsNone(labeled.attack_type)

    def test_legacy_record_without_sensor_code(self):
        """6. Legacy record without sensor_code -> no crash, resolves by device_id."""
        legacy_target = ParsedSensorRecord(
            timestamp="2026-09-24T02:00:00",
            topic="factory/line1/temperature",
            device_id="mtr_001_temperature_sensor",
            sensor_code=None,
            sensor_type="temperature",
            value=28.3,
            unit="°C",
            status="NORMAL",
        )
        legacy_other = ParsedSensorRecord(
            timestamp="2026-09-24T02:00:00",
            topic="factory/line1/pressure",
            device_id="pmp_001_pressure_sensor",
            sensor_code=None,
            sensor_type="pressure",
            value=101.3,
            unit="kPa",
            status="NORMAL",
        )

        # Legacy target matching device_id
        l_target = self.labeler.label(
            record=legacy_target,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensor="MTR-001-TMP",
        )
        self.assertEqual(l_target.label, 1)
        self.assertEqual(l_target.attack_type, "Sensor Spoofing Attack")

        # Legacy non-target
        l_other = self.labeler.label(
            record=legacy_other,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensor="MTR-001-TMP",
        )
        self.assertEqual(l_other.label, 0)
        self.assertIsNone(l_other.attack_type)

    def test_global_network_attacks_affect_all_traffic(self):
        """7. Global / network attacks affect all traffic across the network."""
        for attack_name in [
            "DoS Attack",
            "Replay Attack",
            "Packet Delay Attack",
            "Packet Drop Attack",
            "MQTT Topic Hijacking",
        ]:
            l_target = self.labeler.label(
                record=self.record_target,
                attack_active=True,
                attack_type=attack_name,
            )
            l_unrelated = self.labeler.label(
                record=self.record_unrelated,
                attack_active=True,
                attack_type=attack_name,
            )
            l_tank = self.labeler.label(
                record=self.record_tank,
                attack_active=True,
                attack_type=attack_name,
            )

            self.assertEqual(l_target.label, 1)
            self.assertEqual(l_target.attack_type, attack_name)
            self.assertEqual(l_unrelated.label, 1)
            self.assertEqual(l_unrelated.attack_type, attack_name)
            self.assertEqual(l_tank.label, 1)
            self.assertEqual(l_tank.attack_type, attack_name)

    def test_machine_targeted_attacks(self):
        """8. Machine-targeted attacks affect only sensors attached to the targeted machine."""
        # Motor Overload Attack
        l_motor_tmp = self.labeler.label(
            record=self.record_target,
            attack_active=True,
            attack_type="Motor Overload Attack",
        )
        l_motor_cur = self.labeler.label(
            record=self.record_unrelated,
            attack_active=True,
            attack_type="Motor Overload Attack",
        )
        l_tank = self.labeler.label(
            record=self.record_tank,
            attack_active=True,
            attack_type="Motor Overload Attack",
        )

        self.assertEqual(l_motor_tmp.label, 1)
        self.assertEqual(l_motor_tmp.attack_type, "Motor Overload Attack")
        self.assertEqual(l_motor_cur.label, 1)
        self.assertEqual(l_motor_cur.attack_type, "Motor Overload Attack")
        self.assertEqual(l_tank.label, 0)
        self.assertIsNone(l_tank.attack_type)

        # Valve Stuck Attack
        record_valve = ParsedSensorRecord(
            timestamp="2026-09-24T02:00:00",
            topic="factory/line1/pressure",
            device_id="vlv_001_pressure_sensor",
            sensor_code="VLV-001-PRS",
            sensor_type="pressure",
            value=81.0,
            unit="kPa",
            status="NORMAL",
        )
        l_valve = self.labeler.label(
            record=record_valve,
            attack_active=True,
            attack_type="Valve Stuck Attack",
        )
        l_motor = self.labeler.label(
            record=self.record_target,
            attack_active=True,
            attack_type="Valve Stuck Attack",
        )
        self.assertEqual(l_valve.label, 1)
        self.assertEqual(l_valve.attack_type, "Valve Stuck Attack")
        self.assertEqual(l_motor.label, 0)
        self.assertIsNone(l_motor.attack_type)

    def test_dataset_manager_integration(self):
        """9. DatasetManager processes attack events and applies locality labeling."""
        manager = DatasetManager()

        # Start event with target_sensor MTR-001-TMP
        start_event = RawMQTTMessage(
            timestamp="2026-09-24T02:00:00",
            topic=ATTACK_STATE_TOPIC,
            payload=json.dumps({
                "event": "start",
                "attack": "Sensor Spoofing Attack",
                "target_sensor": "MTR-001-TMP",
                "target_sensors": ["MTR-001-TMP"],
            }),
            qos=0,
            retain=False,
        )
        manager.process_message(start_event)
        self.assertTrue(manager.attack_active)
        self.assertEqual(manager.attack_targets, ["MTR-001-TMP"])

        # Sensor message for target sensor
        raw_target = RawMQTTMessage(
            timestamp="2026-09-24T02:00:01",
            topic="factory/line1/temperature",
            payload=json.dumps({
                "sensor_code": "MTR-001-TMP",
                "device_id": "mtr_001_temperature_sensor",
                "sensor_type": "temperature",
                "value": 45.0,
                "unit": "°C",
                "status": "NORMAL",
                "timestamp": "2026-09-24T02:00:01",
            }),
            qos=0,
            retain=False,
        )
        manager.process_message(raw_target)

        # Sensor message for untargeted sensor
        raw_unrelated = RawMQTTMessage(
            timestamp="2026-09-24T02:00:02",
            topic="factory/line1/current",
            payload=json.dumps({
                "sensor_code": "MTR-001-CUR",
                "device_id": "mtr_001_current_sensor",
                "sensor_type": "current",
                "value": 12.0,
                "unit": "A",
                "status": "NORMAL",
                "timestamp": "2026-09-24T02:00:02",
            }),
            qos=0,
            retain=False,
        )
        manager.process_message(raw_unrelated)

        records = manager.writer.get_records()
        self.assertEqual(len(records), 2)

        # Target record must be attack
        rec1 = records[0]
        self.assertEqual(rec1.sensor_code, "MTR-001-TMP")
        self.assertEqual(rec1.label, 1)
        self.assertEqual(rec1.attack_type, "Sensor Spoofing Attack")

        # Unrelated record must be normal
        rec2 = records[1]
        self.assertEqual(rec2.sensor_code, "MTR-001-CUR")
        self.assertEqual(rec2.label, 0)
        self.assertIsNone(rec2.attack_type)


    def test_all_5_global_network_attacks_label_appropriate_telemetry(self):
        """1. Proves all 5 GLOBAL_NETWORK_ATTACKS label sensor telemetry as attack."""
        expected_network_attacks = {
            "DoS Attack",
            "Replay Attack",
            "Packet Delay Attack",
            "Packet Drop Attack",
            "MQTT Topic Hijacking",
        }
        self.assertEqual(GLOBAL_NETWORK_ATTACKS, expected_network_attacks)

        for attack_name in GLOBAL_NETWORK_ATTACKS:
            for code, record in self.all_19_records.items():
                labeled = self.labeler.label(
                    record=record,
                    attack_active=True,
                    attack_type=attack_name,
                )
                self.assertEqual(
                    labeled.label,
                    1,
                    f"Global network attack '{attack_name}' should label sensor '{code}' as 1",
                )
                self.assertEqual(labeled.attack_type, attack_name)
                self.assertEqual(labeled.sensor_code, code)

    def test_all_6_broad_sensor_attacks_label_all_19_sensors(self):
        """2. Proves all 6 BROAD_SENSOR_ATTACKS label all 19 sensor records under Phase 2 semantics."""
        expected_broad_attacks = {
            "False Data Injection Attack",
            "Sensor Drift Attack",
            "Sensor Freeze Attack",
            "Sensor Noise Injection Attack",
            "Intermittent Attack",
            "Slow Drift Attack",
        }
        self.assertEqual(BROAD_SENSOR_ATTACKS, expected_broad_attacks)

        for attack_name in BROAD_SENSOR_ATTACKS:
            for code, record in self.all_19_records.items():
                labeled = self.labeler.label(
                    record=record,
                    attack_active=True,
                    attack_type=attack_name,
                    target_sensors=None,
                )
                self.assertEqual(
                    labeled.label,
                    1,
                    f"Broad sensor attack '{attack_name}' must label '{code}' as attack under Phase 2 semantics",
                )
                self.assertEqual(labeled.attack_type, attack_name)
                self.assertEqual(labeled.sensor_code, code)

    def test_motor_overload_labels_only_5_motor_sensors(self):
        """3. Proves Motor Overload Attack labels only the 5 motor sensors across all 19 sensors."""
        motor_sensor_codes = {
            "MTR-001-TMP",
            "MTR-001-CUR",
            "MTR-001-RPM",
            "MTR-001-VIB",
            "MTR-001-VLT",
        }
        self.assertEqual(MACHINE_TARGETED_ATTACKS["Motor Overload Attack"], motor_sensor_codes)

        for code, record in self.all_19_records.items():
            labeled = self.labeler.label(
                record=record,
                attack_active=True,
                attack_type="Motor Overload Attack",
            )
            if code in motor_sensor_codes:
                self.assertEqual(
                    labeled.label,
                    1,
                    f"Motor sensor {code} should have label=1 under Motor Overload Attack",
                )
                self.assertEqual(labeled.attack_type, "Motor Overload Attack")
            else:
                self.assertEqual(
                    labeled.label,
                    0,
                    f"Non-motor sensor {code} should have label=0 under Motor Overload Attack",
                )
                self.assertIsNone(labeled.attack_type)
            self.assertEqual(labeled.sensor_code, code)

    def test_valve_stuck_labels_only_vlv_001_prs(self):
        """4. Proves Valve Stuck Attack labels only VLV-001-PRS across all 19 sensors."""
        valve_sensor_codes = {"VLV-001-PRS"}
        self.assertEqual(MACHINE_TARGETED_ATTACKS["Valve Stuck Attack"], valve_sensor_codes)

        for code, record in self.all_19_records.items():
            labeled = self.labeler.label(
                record=record,
                attack_active=True,
                attack_type="Valve Stuck Attack",
            )
            if code in valve_sensor_codes:
                self.assertEqual(
                    labeled.label,
                    1,
                    f"Valve sensor {code} should have label=1 under Valve Stuck Attack",
                )
                self.assertEqual(labeled.attack_type, "Valve Stuck Attack")
            else:
                self.assertEqual(
                    labeled.label,
                    0,
                    f"Non-valve sensor {code} should have label=0 under Valve Stuck Attack",
                )
                self.assertIsNone(labeled.attack_type)
            self.assertEqual(labeled.sensor_code, code)

    def test_sensor_spoofing_labels_only_mtr_001_tmp_by_default(self):
        """5. Proves Sensor Spoofing Attack labels only MTR-001-TMP by default across all 19 sensors."""
        self.assertEqual(DEFAULT_SENSOR_TARGETS["Sensor Spoofing Attack"], ["MTR-001-TMP"])

        for code, record in self.all_19_records.items():
            labeled = self.labeler.label(
                record=record,
                attack_active=True,
                attack_type="Sensor Spoofing Attack",
            )
            if code == "MTR-001-TMP":
                self.assertEqual(labeled.label, 1)
                self.assertEqual(labeled.attack_type, "Sensor Spoofing Attack")
            else:
                self.assertEqual(
                    labeled.label,
                    0,
                    f"Sensor {code} should have label=0 by default under Sensor Spoofing Attack",
                )
                self.assertIsNone(labeled.attack_type)
            self.assertEqual(labeled.sensor_code, code)

    def test_explicit_target_sensors_behavior(self):
        """6. Proves explicit target_sensor and target_sensors behavior remains strictly enforced."""
        record_pump = self.all_19_records["PMP-001-PRS"]

        # Explicit single target
        l_single = self.labeler.label(
            record=record_pump,
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensor="PMP-001-PRS",
        )
        self.assertEqual(l_single.label, 1)
        self.assertEqual(l_single.attack_type, "Sensor Spoofing Attack")

        l_single_unrelated = self.labeler.label(
            record=self.all_19_records["MTR-001-TMP"],
            attack_active=True,
            attack_type="Sensor Spoofing Attack",
            target_sensor="PMP-001-PRS",
        )
        self.assertEqual(l_single_unrelated.label, 0)
        self.assertIsNone(l_single_unrelated.attack_type)

        # Explicit multiple targets
        explicit_targets = ["PMP-001-PRS", "CNV-001-RPM"]
        for code, record in self.all_19_records.items():
            labeled = self.labeler.label(
                record=record,
                attack_active=True,
                attack_type="Sensor Spoofing Attack",
                target_sensors=explicit_targets,
            )
            if code in explicit_targets:
                self.assertEqual(labeled.label, 1, f"Explicit target {code} should be 1")
                self.assertEqual(labeled.attack_type, "Sensor Spoofing Attack")
            else:
                self.assertEqual(labeled.label, 0, f"Non-target {code} should be 0")
                self.assertIsNone(labeled.attack_type)

        # Dynamic explicit target on broad attack restricts it to that target
        l_broad_targeted = self.labeler.label(
            record=record_pump,
            attack_active=True,
            attack_type="False Data Injection Attack",
            target_sensors=["PMP-001-PRS"],
        )
        self.assertEqual(l_broad_targeted.label, 1)

        l_broad_untargeted = self.labeler.label(
            record=self.all_19_records["MTR-001-TMP"],
            attack_active=True,
            attack_type="False Data Injection Attack",
            target_sensors=["PMP-001-PRS"],
        )
        self.assertEqual(l_broad_untargeted.label, 0)
        self.assertIsNone(l_broad_untargeted.attack_type)

    def test_plc_command_injection_never_labels_sensor_telemetry(self):
        """7. Proves PLC Command Injection does NOT label normal sensor MQTT telemetry as attack."""
        for code, record in self.all_19_records.items():
            labeled = self.labeler.label(
                record=record,
                attack_active=True,
                attack_type="PLC Command Injection",
            )
            self.assertEqual(
                labeled.label,
                0,
                f"PLC Command Injection must not label sensor '{code}' as attack!",
            )
            self.assertIsNone(labeled.attack_type)
            self.assertEqual(labeled.sensor_code, code)

        # Also test with explicit target — still rejected as control plane
        l_target = self.labeler.label(
            record=self.all_19_records["MTR-001-TMP"],
            attack_active=True,
            attack_type="PLC Command Injection",
            target_sensor="MTR-001-TMP",
        )
        self.assertEqual(l_target.label, 0)
        self.assertIsNone(l_target.attack_type)

    def test_unauthorized_command_never_labels_sensor_telemetry(self):
        """8. Proves Unauthorized Command does NOT label normal sensor MQTT telemetry as attack."""
        for code, record in self.all_19_records.items():
            labeled = self.labeler.label(
                record=record,
                attack_active=True,
                attack_type="Unauthorized Command Attack",
            )
            self.assertEqual(
                labeled.label,
                0,
                f"Unauthorized Command must not label sensor '{code}' as attack!",
            )
            self.assertIsNone(labeled.attack_type)
            self.assertEqual(labeled.sensor_code, code)

    def test_setpoint_manipulation_never_labels_sensor_telemetry(self):
        """9. Proves Setpoint Manipulation does NOT label normal sensor MQTT telemetry as attack."""
        for code, record in self.all_19_records.items():
            labeled = self.labeler.label(
                record=record,
                attack_active=True,
                attack_type="Setpoint Manipulation Attack",
            )
            self.assertEqual(
                labeled.label,
                0,
                f"Setpoint Manipulation must not label sensor '{code}' as attack!",
            )
            self.assertIsNone(labeled.attack_type)
            self.assertEqual(labeled.sensor_code, code)

    def test_unknown_or_missing_target_information_safely_remains_normal(self):
        """10. Proves unknown attack or missing target information safely remains normal."""
        unknown_attacks = [
            "Unknown Novel Attack",
            "Unregistered Zero-Day Attack",
            "Arbitrary Attack",
        ]
        for attack_name in unknown_attacks:
            for code, record in self.all_19_records.items():
                labeled = self.labeler.label(
                    record=record,
                    attack_active=True,
                    attack_type=attack_name,
                    target_sensors=None,
                )
                self.assertEqual(
                    labeled.label,
                    0,
                    f"Unknown attack '{attack_name}' should safely have label=0 on {code}",
                )
                self.assertIsNone(labeled.attack_type)

    def test_sensor_code_preservation(self):
        """11. Proves sensor_code is preserved on all labeled records (attack and normal)."""
        for code, record in self.all_19_records.items():
            # Normal record
            l_norm = self.labeler.label(record=record, attack_active=False)
            self.assertEqual(l_norm.sensor_code, code)

            # Attack record (network)
            l_net = self.labeler.label(record=record, attack_active=True, attack_type="DoS Attack")
            self.assertEqual(l_net.sensor_code, code)

            # Attack record (broad sensor)
            l_broad = self.labeler.label(
                record=record, attack_active=True, attack_type="False Data Injection Attack"
            )
            self.assertEqual(l_broad.sensor_code, code)

            # Attack record (PLC)
            l_plc = self.labeler.label(
                record=record, attack_active=True, attack_type="PLC Command Injection"
            )
            self.assertEqual(l_plc.sensor_code, code)

    def test_dataset_manager_plc_and_broad_attack_integration(self):
        """12. Proves DatasetManager processes broad and PLC attacks according to Change 3.1."""
        manager = DatasetManager()

        # 1. PLC Command Injection start event
        plc_event = RawMQTTMessage(
            timestamp="2026-09-24T02:00:00",
            topic=ATTACK_STATE_TOPIC,
            payload=json.dumps({
                "event": "start",
                "attack": "PLC Command Injection",
            }),
            qos=0,
            retain=False,
        )
        manager.process_message(plc_event)
        self.assertTrue(manager.attack_active)
        self.assertEqual(manager.attack_type, "PLC Command Injection")

        # Sensor message arrives during PLC attack
        sensor_msg = RawMQTTMessage(
            timestamp="2026-09-24T02:00:01",
            topic="factory/line1/temperature",
            payload=json.dumps({
                "sensor_code": "MTR-001-TMP",
                "device_id": "mtr_001_temperature_sensor",
                "sensor_type": "temperature",
                "value": 45.0,
                "unit": "°C",
                "status": "NORMAL",
                "timestamp": "2026-09-24T02:00:01",
            }),
            qos=0,
            retain=False,
        )
        manager.process_message(sensor_msg)

        records = manager.writer.get_records()
        self.assertEqual(len(records), 1)
        # PLC attack must NOT label physical sensor record as attack
        self.assertEqual(records[0].label, 0)
        self.assertIsNone(records[0].attack_type)
        self.assertEqual(records[0].sensor_code, "MTR-001-TMP")

        # 2. Broad attack start event (False Data Injection Attack)
        fdi_event = RawMQTTMessage(
            timestamp="2026-09-24T02:00:02",
            topic=ATTACK_STATE_TOPIC,
            payload=json.dumps({
                "event": "start",
                "attack": "False Data Injection Attack",
            }),
            qos=0,
            retain=False,
        )
        manager.process_message(fdi_event)
        self.assertEqual(manager.attack_type, "False Data Injection Attack")

        # Sensor message arrives during FDI
        manager.process_message(sensor_msg)
        records = manager.writer.get_records()
        self.assertEqual(len(records), 2)
        # FDI must label sensor record as attack under Phase 2 semantics
        self.assertEqual(records[1].label, 1)
        self.assertEqual(records[1].attack_type, "False Data Injection Attack")
        self.assertEqual(records[1].sensor_code, "MTR-001-TMP")

        # 3. Unknown attack start event with missing target
        unknown_event = RawMQTTMessage(
            timestamp="2026-09-24T02:00:03",
            topic=ATTACK_STATE_TOPIC,
            payload=json.dumps({
                "event": "start",
                "attack": "Unknown Zero-Day Attack",
            }),
            qos=0,
            retain=False,
        )
        manager.process_message(unknown_event)
        manager.process_message(sensor_msg)
        records = manager.writer.get_records()
        self.assertEqual(len(records), 3)
        # Unknown attack must safely remain normal
        self.assertEqual(records[2].label, 0)
        self.assertIsNone(records[2].attack_type)


if __name__ == "__main__":
    unittest.main()
