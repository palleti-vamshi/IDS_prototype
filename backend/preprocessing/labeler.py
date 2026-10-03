"""
Labels parsed sensor records with locality awareness.
"""

from __future__ import annotations

from typing import Iterable

from backend.preprocessing.schemas import (
    ParsedSensorRecord,
    LabeledRecord,
)

# Authoritative 1:1 physical sensor mapping from Phase 1
SENSOR_CODE_TO_DEVICE_ID: dict[str, str] = {
    "MTR-001-TMP": "mtr_001_temperature_sensor",
    "MTR-001-CUR": "mtr_001_current_sensor",
    "MTR-001-RPM": "mtr_001_rpm_sensor",
    "MTR-001-VIB": "mtr_001_vibration_sensor",
    "MTR-001-VLT": "mtr_001_voltage_sensor",

    "PMP-001-PRS": "pmp_001_pressure_sensor",
    "PMP-001-FLW": "pmp_001_flow_sensor",
    "PMP-001-CUR": "pmp_001_current_sensor",

    "TNK-001-LVL": "tnk_001_level_sensor",
    "TNK-001-TMP": "tnk_001_temperature_sensor",
    "TNK-001-PRS": "tnk_001_pressure_sensor",
    "TNK-001-HUM": "tnk_001_humidity_sensor",

    "CNV-001-RPM": "cnv_001_rpm_sensor",
    "CNV-001-CUR": "cnv_001_current_sensor",
    "CNV-001-PRX": "cnv_001_proximity_sensor",

    "VLV-001-PRS": "vlv_001_pressure_sensor",

    "CMP-001-TMP": "cmp_001_temperature_sensor",
    "CMP-001-PRS": "cmp_001_pressure_sensor",
    "CMP-001-CUR": "cmp_001_current_sensor",
}

DEVICE_ID_TO_SENSOR_CODE: dict[str, str] = {
    v: k for k, v in SENSOR_CODE_TO_DEVICE_ID.items()
}

# Global Network attacks (Communication Layer)
# These attacks affect traffic globally across the entire communication bus.
GLOBAL_NETWORK_ATTACKS: set[str] = {
    "DoS Attack",
    "Replay Attack",
    "Packet Delay Attack",
    "Packet Drop Attack",
    "MQTT Topic Hijacking",
}

# Broad / Multi-Sensor physical attacks
# Under frozen Phase 2 simulation semantics, these attacks actively perturb
# or modify all 19 sensors across the factory.
BROAD_SENSOR_ATTACKS: set[str] = {
    "False Data Injection Attack",
    "Sensor Drift Attack",
    "Sensor Freeze Attack",
    "Sensor Noise Injection Attack",
    "Intermittent Attack",
    "Slow Drift Attack",
}

# Machine-targeted attacks
MACHINE_TARGETED_ATTACKS: dict[str, set[str]] = {
    "Motor Overload Attack": {
        "MTR-001-TMP",
        "MTR-001-CUR",
        "MTR-001-RPM",
        "MTR-001-VIB",
        "MTR-001-VLT",
    },
    "Valve Stuck Attack": {
        "VLV-001-PRS",
    },
}

# Default targets for sensor-targeted attacks when no dynamic target is provided
DEFAULT_SENSOR_TARGETS: dict[str, list[str]] = {
    "Sensor Spoofing Attack": ["MTR-001-TMP"],
}

# PLC Control-Plane attacks: These attacks manipulate controller logic or internal state.
# Physical sensor MQTT telemetry remains unperturbed, so they do NOT label normal
# sensor records as attack.
PLC_CONTROL_PLANE_ATTACKS: set[str] = {
    "PLC Command Injection",
    "PLC Command Injection Attack",
    "Unauthorized Command Attack",
    "Setpoint Manipulation Attack",
}


class Labeler:
    """
    Labels parsed sensor records with strict locality awareness.

    Ensures that only records originating from physical targets
    actually affected by an active attack receive label=1 and attack_type.
    Unrelated sensor telemetry remains labeled as normal (label=0, attack_type=None).
    """

    def __init__(self) -> None:
        self.sequence_number: int = 0

    def is_target_affected(
        self,
        record: ParsedSensorRecord,
        attack_type: str,
        target_sensors: Iterable[str] | str | None = None,
    ) -> bool:
        """
        Determine whether a sensor record belongs to an affected attack target.
        """
        # 0. PLC control-plane attacks affect controller state/commands, not sensor telemetry.
        # Sensor MQTT records remain normal and must NOT be labeled as attack.
        if attack_type in PLC_CONTROL_PLANE_ATTACKS:
            return False

        # 1. Normalize explicitly supplied targets if present
        explicit_targets: set[str] = set()
        if target_sensors is not None:
            if isinstance(target_sensors, str):
                explicit_targets.add(target_sensors)
            else:
                explicit_targets.update(target_sensors)

        if explicit_targets:
            # Check direct match against sensor_code
            if record.sensor_code is not None:
                if record.sensor_code in explicit_targets:
                    return True
                # Target might have been supplied as a device_id
                target_sensor_codes = {
                    DEVICE_ID_TO_SENSOR_CODE.get(t, t) for t in explicit_targets
                }
                if record.sensor_code in target_sensor_codes:
                    return True

            # Check match against device_id (for legacy packets or device-level targeting)
            if record.device_id in explicit_targets:
                return True
            target_device_ids = {
                SENSOR_CODE_TO_DEVICE_ID.get(t, t) for t in explicit_targets
            }
            if record.device_id in target_device_ids:
                return True

            # If explicit targets were specified and did not match, record is not affected
            return False

        # 2. Global network attacks affect all traffic across the communication layer
        if attack_type in GLOBAL_NETWORK_ATTACKS:
            return True

        # 3. Broad sensor attacks perturb all sensors across the factory under Phase 2 semantics
        if attack_type in BROAD_SENSOR_ATTACKS:
            return True

        # 4. Machine-targeted attacks
        if attack_type in MACHINE_TARGETED_ATTACKS:
            affected_codes = MACHINE_TARGETED_ATTACKS[attack_type]
            if record.sensor_code is not None:
                return record.sensor_code in affected_codes
            # Fallback for legacy records using device_id
            affected_devices = {
                SENSOR_CODE_TO_DEVICE_ID[code] for code in affected_codes
            }
            return record.device_id in affected_devices

        # 5. Sensor-targeted attacks with known default targets
        if attack_type in DEFAULT_SENSOR_TARGETS:
            default_codes = DEFAULT_SENSOR_TARGETS[attack_type]
            if record.sensor_code is not None:
                return record.sensor_code in default_codes
            default_devices = {
                SENSOR_CODE_TO_DEVICE_ID.get(c, c) for c in default_codes
            }
            return record.device_id in default_devices

        # 6. Default safe fallback for missing target information
        # Missing or unspecified target information must NEVER silently label
        # unrelated sensors as attacks.
        return False

    def label(
        self,
        record: ParsedSensorRecord,
        attack_active: bool = False,
        attack_type: str | None = None,
        target_sensor: str | None = None,
        target_sensors: Iterable[str] | str | None = None,
    ) -> LabeledRecord:
        """
        Label a parsed sensor record.

        Parameters
        ----------
        record : ParsedSensorRecord
            The parsed sensor telemetry record.
        attack_active : bool
            Whether an attack is currently running.
        attack_type : str | None
            Name of the active attack, or None if normal.
        target_sensor : str | None
            Optional single target sensor code.
        target_sensors : Iterable[str] | str | None
            Optional list or set of target sensor codes.
        """
        self.sequence_number += 1

        # Combine target_sensor and target_sensors into a single collection if provided
        combined_targets: list[str] | None = None
        if target_sensor or target_sensors is not None:
            combined_targets = []
            if target_sensor:
                combined_targets.append(target_sensor)
            if target_sensors is not None:
                if isinstance(target_sensors, str):
                    combined_targets.append(target_sensors)
                else:
                    combined_targets.extend(target_sensors)

        is_attack = False
        final_attack_type: str | None = None

        if attack_active and attack_type:
            if self.is_target_affected(record, attack_type, combined_targets):
                is_attack = True
                final_attack_type = attack_type

        return LabeledRecord(
            timestamp=record.timestamp,
            topic=record.topic,
            device_id=record.device_id,
            sensor_type=record.sensor_type,
            value=record.value,
            unit=record.unit,
            status=record.status,
            attack_type=final_attack_type,
            label=1 if is_attack else 0,
            source="simulator",
            sequence_number=self.sequence_number,
            sensor_code=record.sensor_code,
        )