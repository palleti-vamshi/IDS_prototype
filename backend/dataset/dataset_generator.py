"""
Phase 3 Dataset Generator

Generates realistic industrial sensor telemetry for:
- Normal operation
- Sensor attacks
- Network attacks
- PLC attacks
- Process attacks
- Stealth attacks

The generator produces labelled records that can later be
used for ML training and evaluation.
"""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from backend.dataset.dataset_schema import DatasetRecord


# ============================================================
# Configuration
# ============================================================

OUTPUT_FILE = Path("datasets/raw/phase3_dataset.csv")

RANDOM_SEED = 42

TOTAL_RECORDS = 100_000

NORMAL_RATIO = 0.50
ATTACK_RATIO = 0.50

# Spread the dataset across one month instead of only 1–2 days.
DATASET_DAYS = 30


# ============================================================
# Industrial sensors
# ============================================================

SENSORS = [
    {
        "sensor_code": "TANK_LEVEL_01",
        "device_id": "TANK_01",
        "sensor_type": "LEVEL",
        "unit": "%",
        "base": 65.0,
        "minimum": 0.0,
        "maximum": 100.0,
    },
    {
        "sensor_code": "TANK_PRESSURE_01",
        "device_id": "TANK_01",
        "sensor_type": "PRESSURE",
        "unit": "bar",
        "base": 5.0,
        "minimum": 0.0,
        "maximum": 10.0,
    },
    {
        "sensor_code": "PUMP_TEMP_01",
        "device_id": "PUMP_01",
        "sensor_type": "TEMPERATURE",
        "unit": "C",
        "base": 65.0,
        "minimum": 20.0,
        "maximum": 120.0,
    },
    {
        "sensor_code": "PUMP_FLOW_01",
        "device_id": "PUMP_01",
        "sensor_type": "FLOW",
        "unit": "L/min",
        "base": 120.0,
        "minimum": 0.0,
        "maximum": 200.0,
    },
    {
        "sensor_code": "MOTOR_RPM_01",
        "device_id": "MOTOR_01",
        "sensor_type": "RPM",
        "unit": "rpm",
        "base": 1450.0,
        "minimum": 0.0,
        "maximum": 3000.0,
    },
    {
        "sensor_code": "MOTOR_VIBRATION_01",
        "device_id": "MOTOR_01",
        "sensor_type": "VIBRATION",
        "unit": "mm/s",
        "base": 2.5,
        "minimum": 0.0,
        "maximum": 20.0,
    },
    {
        "sensor_code": "VALVE_POSITION_01",
        "device_id": "VALVE_01",
        "sensor_type": "POSITION",
        "unit": "%",
        "base": 50.0,
        "minimum": 0.0,
        "maximum": 100.0,
    },
    {
        "sensor_code": "COMPRESSOR_PRESSURE_01",
        "device_id": "COMPRESSOR_01",
        "sensor_type": "PRESSURE",
        "unit": "bar",
        "base": 7.0,
        "minimum": 0.0,
        "maximum": 15.0,
    },
]


# ============================================================
# Attack definitions
# ============================================================

ATTACKS = [
    {
        "name": "Sensor Spoofing",
        "type": "SENSOR",
        "target": "SENSOR",
        "effect": "spoof",
    },
    {
        "name": "Sensor Drift",
        "type": "SENSOR",
        "target": "SENSOR",
        "effect": "drift",
    },
    {
        "name": "Sensor Noise Injection",
        "type": "SENSOR",
        "target": "SENSOR",
        "effect": "noise",
    },
    {
        "name": "False Data Injection",
        "type": "SENSOR",
        "target": "SENSOR",
        "effect": "false_data",
    },
    {
        "name": "Network Flood",
        "type": "NETWORK",
        "target": "COMMUNICATION",
        "effect": "network",
    },
    {
        "name": "Packet Delay",
        "type": "NETWORK",
        "target": "COMMUNICATION",
        "effect": "network",
    },
    {
        "name": "PLC Command Injection",
        "type": "PLC",
        "target": "PLC",
        "effect": "plc",
    },
    {
        "name": "Setpoint Manipulation",
        "type": "PLC",
        "target": "PLC",
        "effect": "plc",
    },
    {
        "name": "Motor Overload",
        "type": "PROCESS",
        "target": "PROCESS",
        "effect": "process",
    },
    {
        "name": "Valve Stuck",
        "type": "PROCESS",
        "target": "PROCESS",
        "effect": "process",
    },
    {
        "name": "Slow Drift",
        "type": "STEALTH",
        "target": "SENSOR",
        "effect": "slow_drift",
    },
    {
        "name": "Intermittent Attack",
        "type": "STEALTH",
        "target": "SENSOR",
        "effect": "intermittent",
    },
]


# ============================================================
# Helper functions
# ============================================================

def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """Keep a value inside its physical range."""

    return max(
        minimum,
        min(maximum, value),
    )


def generate_normal_value(
    sensor: dict,
) -> float:
    """
    Generate a normal industrial sensor reading.

    Small random variations are intentional because real
    industrial measurements are not perfectly constant.
    """

    base = sensor["base"]

    variation = random.gauss(
        0.0,
        abs(base) * 0.015 + 0.05,
    )

    value = base + variation

    return clamp(
        value,
        sensor["minimum"],
        sensor["maximum"],
    )


def apply_attack(
    value: float,
    sensor: dict,
    attack: dict,
    attack_progress: float,
) -> float:
    """
    Apply a realistic attack effect to one sensor value.
    """

    effect = attack["effect"]

    if effect == "spoof":

        offset = random.uniform(
            0.10,
            0.30,
        )

        direction = random.choice(
            [-1.0, 1.0]
        )

        value += (
            sensor["maximum"]
            - sensor["minimum"]
        ) * offset * direction

    elif effect == "drift":

        range_size = (
            sensor["maximum"]
            - sensor["minimum"]
        )

        drift = (
            range_size
            * 0.20
            * attack_progress
        )

        value += drift

    elif effect == "noise":

        range_size = (
            sensor["maximum"]
            - sensor["minimum"]
        )

        value += random.gauss(
            0.0,
            range_size * 0.08,
        )

    elif effect == "false_data":

        value *= random.uniform(
            1.10,
            1.30,
        )

    elif effect == "network":

        value += random.gauss(
            0.0,
            abs(sensor["base"]) * 0.04 + 0.1,
        )

    elif effect == "plc":

        value += (
            sensor["maximum"]
            - sensor["minimum"]
        ) * random.uniform(
            0.08,
            0.18,
        )

    elif effect == "process":

        value += (
            sensor["maximum"]
            - sensor["minimum"]
        ) * random.uniform(
            0.10,
            0.25,
        )

    elif effect == "slow_drift":

        range_size = (
            sensor["maximum"]
            - sensor["minimum"]
        )

        value += (
            range_size
            * 0.12
            * attack_progress
        )

    elif effect == "intermittent":

        if random.random() < 0.35:

            value += (
                sensor["maximum"]
                - sensor["minimum"]
            ) * random.uniform(
                0.08,
                0.20,
            )

    return clamp(
        value,
        sensor["minimum"],
        sensor["maximum"],
    )


def choose_attack() -> dict:
    """Choose one attack type."""

    return random.choice(ATTACKS)


# ============================================================
# Record generation
# ============================================================

def generate_record(
    timestamp: datetime,
    sensor: dict,
    attack: dict | None,
    attack_progress: float,
) -> DatasetRecord:

    value = generate_normal_value(sensor)

    if attack is None:

        attack_active = False

        attack_id = None
        attack_name = None
        attack_type = None
        attack_target = None
        attack_state = None

        health = random.uniform(
            96.0,
            100.0,
        )

    else:

        value = apply_attack(
            value,
            sensor,
            attack,
            attack_progress,
        )

        attack_active = True

        attack_id = (
            f"PH3-{attack['type']}-"
            f"{random.randint(1000, 9999)}"
        )

        attack_name = attack["name"]

        attack_type = attack["type"]

        attack_target = attack["target"]

        attack_state = "RUNNING"

        health = random.uniform(
            70.0,
            96.0,
        )

    return DatasetRecord(
        timestamp=timestamp.isoformat(),

        sensor_code=sensor["sensor_code"],

        device_id=sensor["device_id"],

        sensor_type=sensor["sensor_type"],

        value=round(
            value,
            3,
        ),

        unit=sensor["unit"],

        status="RUNNING",

        health=round(
            health,
            2,
        ),

        attack_active=attack_active,

        attack_id=attack_id,

        attack_name=attack_name,

        attack_type=attack_type,

        attack_target=attack_target,

        attack_state=attack_state,
    )


# ============================================================
# Dataset generation
# ============================================================

def generate_dataset(
    total_records: int = TOTAL_RECORDS,
) -> None:

    random.seed(
        RANDOM_SEED
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    start_time = datetime(
        2026,
        1,
        1,
        0,
        0,
        0,
    )

    attack_records = int(
        total_records * ATTACK_RATIO
    )

    normal_records = (
        total_records
        - attack_records
    )

    records = []

    # --------------------------------------------------------
    # Generate timestamps across 30 days
    # --------------------------------------------------------

    total_seconds = (
        DATASET_DAYS * 24 * 60 * 60
    )

    timestamps = [
        start_time
        + timedelta(
            seconds=random.randint(
                0,
                total_seconds - 1,
            )
        )
        for _ in range(total_records)
    ]

    # --------------------------------------------------------
    # Create labels independently from timestamps
    # --------------------------------------------------------

    labels = (
        [False] * normal_records
        + [True] * attack_records
    )

    random.shuffle(labels)

    # --------------------------------------------------------
    # Generate records
    # --------------------------------------------------------

    for timestamp, attack_active in zip(
        timestamps,
        labels,
    ):

        sensor = random.choice(
            SENSORS
        )

        if attack_active:

            attack = choose_attack()

            progress = random.uniform(
                0.0,
                1.0,
            )

        else:

            attack = None
            progress = 0.0

        record = generate_record(
            timestamp=timestamp,
            sensor=sensor,
            attack=attack,
            attack_progress=progress,
        )

        records.append(
            record
        )

    # --------------------------------------------------------
    # Sort by timestamp
    # --------------------------------------------------------

    records.sort(
        key=lambda record: record.timestamp
    )

    # --------------------------------------------------------
    # Write CSV
    # --------------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=DatasetRecord.__dataclass_fields__.keys(),
        )

        writer.writeheader()

        for record in records:

            writer.writerow(
                record.to_dict()
            )

    print("=" * 60)

    print(
        "PHASE 3 DATASET GENERATION COMPLETE"
    )

    print("=" * 60)

    print(
        f"Total records : {len(records)}"
    )

    print(
        f"Normal        : {normal_records}"
    )

    print(
        f"Attack        : {attack_records}"
    )

    print(
        f"Dataset days  : {DATASET_DAYS}"
    )

    print(
        f"Output        : {OUTPUT_FILE}"
    )

    print("=" * 60)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    generate_dataset()