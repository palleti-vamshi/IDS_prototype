"""
run_validation_campaign.py

Executes a small validation dataset campaign (1,000 records) and performs
comprehensive Phase 3.3, Phase 3.4, and Phase 3.5 audits.
"""

from __future__ import annotations

import json
from pathlib import Path
import time
import pandas as pd
import numpy as np

from backend.preprocessing.dataset_manager import DatasetManager
from backend.preprocessing.pipeline import DatasetPipeline
from backend.preprocessing.simulation_runner import SimulationRunner
from backend.preprocessing.attack_runner import AttackRunner
from backend.preprocessing.generation_config import SIMULATION_TICK_RATE
from backend.preprocessing.labeler import (
    SENSOR_CODE_TO_DEVICE_ID,
    GLOBAL_NETWORK_ATTACKS,
    BROAD_SENSOR_ATTACKS,
    MACHINE_TARGETED_ATTACKS,
    DEFAULT_SENSOR_TARGETS,
    PLC_CONTROL_PLANE_ATTACKS,
)

EXPECTED_COLUMNS = [
    "record_id",
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
    "sensor_code",
]


def generate_validation_dataset(output_path: str, target_size: int = 1000):
    print("=" * 72)
    print(f"🚀 GENERATING VALIDATION DATASET ({target_size} records)")
    print(f"Output: {output_path}")
    print("=" * 72)

    manager = DatasetManager(target_dataset_size=target_size)
    pipeline = DatasetPipeline(manager=manager)
    simulator = SimulationRunner(tick_rate=SIMULATION_TICK_RATE)

    try:
        simulator.start()
        time.sleep(1.0)

        pipeline.start()
        time.sleep(1.0)

        runner = AttackRunner(manager, simulator)
        runner.run()

    finally:
        print(f"\n💾 Exporting to {output_path}...")
        manager.export_dataset(output_path)
        pipeline.stop()
        simulator.stop()
        print("✅ Pipeline and Simulator stopped.")


def audit_validation_dataset(file_path: str, expected_size: int = 1000) -> dict:
    print("\n" + "=" * 72)
    print(f"🔍 AUDITING DATASET: {file_path}")
    print("=" * 72)

    df = pd.read_csv(file_path)
    # Strip any whitespace from string columns
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": None, "": None})

    results = {}

    # 1. Structure Audit
    print("\n--- 1. Structure Audit ---")
    row_count = len(df)
    results["row_count"] = row_count
    print(f"Row count: {row_count} (Expected: {expected_size})")
    assert row_count == expected_size, f"Expected {expected_size} rows, got {row_count}"

    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    assert not missing_cols, f"Missing columns: {missing_cols}"
    print(f"Columns: {list(df.columns)} (All {len(EXPECTED_COLUMNS)} expected columns present)")

    # 2. Null Audit
    print("\n--- 2. Null / Missing Value Audit ---")
    null_counts = df.isnull().sum()
    print("Null counts per column:")
    for col, count in null_counts.items():
        if col == "attack_type":
            print(f"  {col}: {count} (normal records have no attack_type - expected)")
        else:
            print(f"  {col}: {count}")
            assert count == 0, f"Unexpected null values in column {col}: {count}"

    # 3. Identity Audit
    print("\n--- 3. Sensor Identity Audit ---")
    unique_sensor_codes = set(df["sensor_code"].dropna().unique())
    print(f"Unique sensor codes count: {len(unique_sensor_codes)}")
    assert len(unique_sensor_codes) == 19, f"Expected 19 sensor codes, got {len(unique_sensor_codes)}"
    assert unique_sensor_codes == set(SENSOR_CODE_TO_DEVICE_ID.keys()), "Sensor codes mismatch!"
    print("✅ All 19 physical sensors present!")

    # Verify 1:1 sensor_code to device_id mapping
    mapping_violations = 0
    for code, group in df.groupby("sensor_code"):
        expected_device = SENSOR_CODE_TO_DEVICE_ID[code]
        actual_devices = set(group["device_id"].unique())
        if actual_devices != {expected_device}:
            mapping_violations += 1
            print(f"❌ Mapping violation for {code}: expected {expected_device}, got {actual_devices}")
    assert mapping_violations == 0, f"Found {mapping_violations} sensor_code to device_id violations"
    print("✅ 100% 1:1 sensor_code to device_id mapping verified!")

    # 4. Label Consistency Audit
    print("\n--- 4. Label Consistency Audit ---")
    label_0_with_attack = df[(df["label"] == 0) & (df["attack_type"].notnull()) & (df["attack_type"] != "")]
    assert len(label_0_with_attack) == 0, f"Found {len(label_0_with_attack)} records with label=0 and attack_type set!"

    label_1_without_attack = df[(df["label"] == 1) & (df["attack_type"].isnull())]
    assert len(label_1_without_attack) == 0, f"Found {len(label_1_without_attack)} records with label=1 and attack_type null!"
    print("✅ label=0 <-> attack_type=None and label=1 <-> attack_type!=None strictly verified!")

    # 5. Locality Audit
    print("\n--- 5. Locality Audit ---")
    # Motor Overload
    motor_records = df[df["attack_type"] == "Motor Overload Attack"]
    if len(motor_records) > 0:
        allowed_motor_sensors = MACHINE_TARGETED_ATTACKS["Motor Overload Attack"]
        unrelated_motor = motor_records[~motor_records["sensor_code"].isin(allowed_motor_sensors)]
        assert len(unrelated_motor) == 0, f"Motor Overload leaked to: {unrelated_motor['sensor_code'].unique()}"
        print(f"✅ Motor Overload correctly restricted to motor sensors ({len(motor_records)} records)")

    # Valve Stuck
    valve_records = df[df["attack_type"] == "Valve Stuck Attack"]
    if len(valve_records) > 0:
        unrelated_valve = valve_records[valve_records["sensor_code"] != "VLV-001-PRS"]
        assert len(unrelated_valve) == 0, f"Valve Stuck leaked to: {unrelated_valve['sensor_code'].unique()}"
        print(f"✅ Valve Stuck correctly restricted to VLV-001-PRS ({len(valve_records)} records)")

    # Sensor Spoofing
    spoof_records = df[df["attack_type"] == "Sensor Spoofing Attack"]
    if len(spoof_records) > 0:
        unrelated_spoof = spoof_records[spoof_records["sensor_code"] != "MTR-001-TMP"]
        assert len(unrelated_spoof) == 0, f"Sensor Spoofing leaked to: {unrelated_spoof['sensor_code'].unique()}"
        print(f"✅ Sensor Spoofing correctly restricted to MTR-001-TMP ({len(spoof_records)} records)")

    # PLC attacks
    for plc_attack in PLC_CONTROL_PLANE_ATTACKS:
        plc_records = df[df["attack_type"] == plc_attack]
        assert len(plc_records) == 0, f"PLC attack {plc_attack} unexpectedly labeled sensor telemetry as attack!"
    print("✅ PLC Control-Plane attacks produce 0 sensor attack labels (verified!)")

    # 6. Temporal Audit
    print("\n--- 6. Temporal Audit ---")
    parsed_timestamps = pd.to_datetime(df["timestamp"], format="ISO8601")
    assert not parsed_timestamps.isnull().any(), "Found unparseable ISO-8601 timestamps!"
    print(f"Time range: {parsed_timestamps.min()} to {parsed_timestamps.max()}")

    # 7. Duplicate Audit
    print("\n--- 7. Duplicate Audit ---")
    exact_duplicates = df.duplicated().sum()
    print(f"Exact full-row duplicates: {exact_duplicates}")
    assert exact_duplicates == 0, f"Found {exact_duplicates} exact duplicate rows!"

    # Sequence numbers
    seq_unique = df["sequence_number"].nunique()
    assert seq_unique == row_count, f"Duplicate sequence numbers found: {row_count - seq_unique}"
    print("✅ sequence_numbers strictly monotonically unique!")

    # Distribution summary
    label_counts = df["label"].value_counts().to_dict()
    normal_count = label_counts.get(0, 0)
    attack_count = label_counts.get(1, 0)
    print("\n--- Summary ---")
    print(f"Normal: {normal_count} ({normal_count / row_count * 100:.2f}%)")
    print(f"Attack: {attack_count} ({attack_count / row_count * 100:.2f}%)")
    print("Attack breakdown:")
    for att, count in df[df["label"] == 1]["attack_type"].value_counts().items():
        print(f"  {att:35}: {count:>5} records")

    print("\n🎉 ALL VALIDATION CHECKS PASSED!")
    return {
        "total": row_count,
        "normal": normal_count,
        "attack": attack_count,
    }


if __name__ == "__main__":
    validation_path = "dataset/lightx_ids_validation_1k.csv"
    generate_validation_dataset(validation_path, target_size=1000)
    audit_validation_dataset(validation_path, expected_size=1000)
