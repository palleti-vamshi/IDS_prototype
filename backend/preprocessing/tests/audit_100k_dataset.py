"""
LightX-IDS 100K Dataset Audit

Purpose:
    Perform a comprehensive quality audit of the generated 100K dataset
    before freezing it for Phase 4 Machine Learning.

Run from project root:

    python -m backend.preprocessing.tests.audit_100k_dataset
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

TARGET_SIZE = 100_000
EXPECTED_CLASS_COUNT = 18
EXPECTED_SENSOR_TYPES = {
    "temperature",
    "pressure",
    "current",
    "rpm",
    "vibration",
    "voltage",
    "flow",
    "level",
    "humidity",
    "proximity",
}

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
]

ATTACK_CLASSES = {
    "DoS Attack",
    "Replay Attack",
    "Packet Delay Attack",
    "Packet Drop Attack",
    "MQTT Topic Hijacking",
    "Sensor Spoofing Attack",
    "False Data Injection Attack",
    "Sensor Drift Attack",
    "Sensor Freeze Attack",
    "Sensor Noise Injection Attack",
    "PLC Command Injection",
    "Unauthorized Command Attack",
    "Setpoint Manipulation Attack",
    "Motor Overload Attack",
    "Valve Stuck Attack",
    "Intermittent Attack",
    "Slow Drift Attack",
}


# ============================================================
# PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = PROJECT_ROOT / "dataset" / "lightx_ids_dataset.csv"


# ============================================================
# HELPERS
# ============================================================

passed = 0
warnings = 0
failed = 0


def check(name, condition, success_message, failure_message=None):
    global passed, failed

    if condition:
        print(f"✅ {name}: {success_message}")
        passed += 1
    else:
        print(
            f"❌ {name}: "
            f"{failure_message if failure_message else 'FAILED'}"
        )
        failed += 1


def warning(name, message):
    global warnings
    print(f"⚠️ {name}: {message}")
    warnings += 1


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# LOAD DATASET
# ============================================================

section("1. DATASET LOADING")

print(f"Dataset path: {DATASET_PATH}")

if not DATASET_PATH.exists():
    print("❌ Dataset file was not found.")
    print()
    print("Expected:")
    print(DATASET_PATH)
    sys.exit(1)

try:
    df = pd.read_csv(DATASET_PATH)
except Exception as exc:
    print(f"❌ Failed to read dataset: {exc}")
    sys.exit(1)

print(f"Shape: {df.shape}")
print(f"File size: {DATASET_PATH.stat().st_size / (1024 * 1024):.2f} MB")


# ============================================================
# 2. ROW COUNT
# ============================================================

section("2. RECORD COUNT")

check(
    "Target size",
    len(df) == TARGET_SIZE,
    f"{len(df):,} records exactly",
    f"Expected {TARGET_SIZE:,}, found {len(df):,}",
)


# ============================================================
# 3. COLUMN CHECK
# ============================================================

section("3. COLUMN STRUCTURE")

actual_columns = list(df.columns)

missing_columns = [
    column for column in EXPECTED_COLUMNS
    if column not in actual_columns
]

extra_columns = [
    column for column in actual_columns
    if column not in EXPECTED_COLUMNS
]

check(
    "Required columns",
    len(missing_columns) == 0,
    "All required columns present",
    f"Missing columns: {missing_columns}",
)

if extra_columns:
    warning(
        "Extra columns",
        f"Dataset contains additional columns: {extra_columns}",
    )
else:
    print("✅ Extra columns: None")


# ============================================================
# 4. CLASS DISTRIBUTION
# ============================================================

section("4. CLASS DISTRIBUTION")

class_counts = df["label"].value_counts().sort_index()

print("\nLabel distribution:")
print(class_counts.to_string())

unique_classes = df["attack_type"].dropna().unique()

print("\nAttack classes:")
for class_name, count in (
    df["attack_type"]
    .fillna("Normal")
    .value_counts()
    .sort_index()
    .items()
):
    print(f"  {class_name:<35} {count:>7,}")

class_names = set(
    df["attack_type"].fillna("Normal").astype(str).unique()
)

check(
    "Class count",
    len(class_names) == EXPECTED_CLASS_COUNT,
    f"{len(class_names)} classes found",
    f"Expected {EXPECTED_CLASS_COUNT}, found {len(class_names)}",
)

unexpected_classes = class_names - (ATTACK_CLASSES | {"Normal"})

check(
    "Class names",
    len(unexpected_classes) == 0,
    "All class names are expected",
    f"Unexpected classes: {sorted(unexpected_classes)}",
)


# ============================================================
# 5. LABEL CONSISTENCY
# ============================================================

section("5. LABEL CONSISTENCY")

normal_mask = df["attack_type"].isna()
attack_mask = df["attack_type"].notna()

normal_wrong_label = (df.loc[normal_mask, "label"] != 0).sum()
attack_wrong_label = (df.loc[attack_mask, "label"] != 1).sum()

check(
    "Normal labels",
    normal_wrong_label == 0,
    "All Normal records have label 0",
    f"{normal_wrong_label} Normal records have incorrect labels",
)

check(
    "Attack labels",
    attack_wrong_label == 0,
    "All attack records have label 1",
    f"{attack_wrong_label} attack records have incorrect labels",
)

invalid_labels = set(df["label"].dropna().unique()) - {0, 1}

check(
    "Binary labels",
    len(invalid_labels) == 0,
    "Only labels 0 and 1 are present",
    f"Invalid labels: {invalid_labels}",
)


# ============================================================
# 6. SENSOR DISTRIBUTION
# ============================================================

section("6. SENSOR-TYPE DISTRIBUTION")

sensor_counts = df["sensor_type"].value_counts().sort_index()

print("\nSensor distribution:")
print(sensor_counts.to_string())

actual_sensor_types = set(
    df["sensor_type"].dropna().astype(str).unique()
)

missing_sensor_types = EXPECTED_SENSOR_TYPES - actual_sensor_types
unexpected_sensor_types = actual_sensor_types - EXPECTED_SENSOR_TYPES

check(
    "Sensor-type count",
    len(actual_sensor_types) == len(EXPECTED_SENSOR_TYPES),
    f"{len(actual_sensor_types)} sensor types found",
    f"Expected {len(EXPECTED_SENSOR_TYPES)}, found {len(actual_sensor_types)}",
)

check(
    "Required sensor types",
    len(missing_sensor_types) == 0,
    "All 10 expected sensor types present",
    f"Missing sensor types: {sorted(missing_sensor_types)}",
)

check(
    "Unexpected sensor types",
    len(unexpected_sensor_types) == 0,
    "No unexpected sensor types",
    f"Unexpected sensor types: {sorted(unexpected_sensor_types)}",
)


# ============================================================
# 7. ATTACK × SENSOR DISTRIBUTION
# ============================================================

section("7. ATTACK × SENSOR DISTRIBUTION")

cross = pd.crosstab(
    df["attack_type"].fillna("Normal"),
    df["sensor_type"],
)

print(cross.to_string())

missing_combinations = []

for attack_class in sorted(class_names):
    if attack_class not in cross.index:
        continue

    for sensor_type in sorted(EXPECTED_SENSOR_TYPES):
        count = cross.loc[attack_class].get(sensor_type, 0)

        if count == 0:
            missing_combinations.append(
                (attack_class, sensor_type)
            )

if missing_combinations:
    warning(
        "Attack × sensor coverage",
        f"{len(missing_combinations)} zero-count combinations found.",
    )

    for attack_class, sensor_type in missing_combinations[:20]:
        print(
            f"  Missing: {attack_class} × {sensor_type}"
        )

    if len(missing_combinations) > 20:
        print(
            f"  ... and {len(missing_combinations) - 20} more"
        )
else:
    print(
        "✅ Attack × sensor coverage: "
        "Every class has every expected sensor type."
    )


# ============================================================
# 8. NULL VALUES
# ============================================================

section("8. NULL / MISSING VALUES")

null_counts = df.isnull().sum()

print(null_counts.to_string())

# attack_type is intentionally NULL for Normal records.
allowed_attack_type_nulls = int(normal_mask.sum())

unexpected_nulls = {}

for column in EXPECTED_COLUMNS:
    count = int(null_counts[column])

    if column == "attack_type":
        if count != allowed_attack_type_nulls:
            unexpected_nulls[column] = count
    else:
        if count != 0:
            unexpected_nulls[column] = count

check(
    "Required telemetry fields",
    all(
        int(null_counts[column]) == 0
        for column in [
            "record_id",
            "timestamp",
            "topic",
            "device_id",
            "sensor_type",
            "value",
            "unit",
            "status",
            "label",
            "source",
            "sequence_number",
        ]
    ),
    "No unexpected nulls in required fields",
    f"Unexpected nulls: {unexpected_nulls}",
)

check(
    "Normal attack_type nulls",
    int(null_counts["attack_type"]) == allowed_attack_type_nulls,
    f"{allowed_attack_type_nulls:,} Normal records correctly use null attack_type",
    (
        f"Expected {allowed_attack_type_nulls:,} attack_type nulls, "
        f"found {int(null_counts['attack_type']):,}"
    ),
)


# ============================================================
# 9. DUPLICATES
# ============================================================

section("9. DUPLICATE CHECKS")

duplicate_rows = int(df.duplicated().sum())

duplicate_record_ids = int(
    df["record_id"].duplicated().sum()
)

duplicate_sequence_numbers = int(
    df["sequence_number"].duplicated().sum()
)

check(
    "Duplicate rows",
    duplicate_rows == 0,
    "0 duplicate rows",
    f"{duplicate_rows:,} duplicate rows",
)

check(
    "Duplicate record IDs",
    duplicate_record_ids == 0,
    "0 duplicate record IDs",
    f"{duplicate_record_ids:,} duplicate record IDs",
)

check(
    "Duplicate sequence numbers",
    duplicate_sequence_numbers == 0,
    "0 duplicate sequence numbers",
    f"{duplicate_sequence_numbers:,} duplicate sequence numbers",
)


# ============================================================
# 10. SEQUENCE NUMBER
# ============================================================

section("10. SEQUENCE NUMBER INTEGRITY")

sequence_numeric = pd.to_numeric(
    df["sequence_number"],
    errors="coerce",
)

sequence_nulls = int(sequence_numeric.isna().sum())

check(
    "Sequence numeric",
    sequence_nulls == 0,
    "All sequence numbers are numeric",
    f"{sequence_nulls:,} non-numeric sequence values",
)

if sequence_nulls == 0:
    seq_min = int(sequence_numeric.min())
    seq_max = int(sequence_numeric.max())
    seq_unique = int(sequence_numeric.nunique())

    print(f"Minimum sequence: {seq_min:,}")
    print(f"Maximum sequence: {seq_max:,}")
    print(f"Unique sequences: {seq_unique:,}")

    check(
        "Sequence uniqueness",
        seq_unique == len(df),
        "All sequence numbers are unique",
        f"Only {seq_unique:,} unique sequences",
    )

    check(
        "Sequence lower bound",
        seq_min >= 1,
        f"Minimum sequence is {seq_min}",
        f"Invalid minimum sequence: {seq_min}",
    )

    # IMPORTANT:
    # We do NOT require sequence numbers to be contiguous.
    # Quota-rejected/generated stream records can advance the sequence.
    if seq_max > len(df):
        warning(
            "Sequence gaps",
            (
                f"Maximum sequence is {seq_max:,}, greater than "
                f"record count {len(df):,}. This is allowed because "
                f"the sequence tracks the generated/processed stream, "
                f"not only accepted CSV records."
            ),
        )


# ============================================================
# 11. NUMERIC VALIDITY
# ============================================================

section("11. NUMERIC TELEMETRY VALIDITY")

values = pd.to_numeric(df["value"], errors="coerce")

non_numeric_values = int(values.isna().sum())
nan_values = int(values.isna().sum())
inf_values = int(np.isinf(values.to_numpy()).sum())

check(
    "Numeric values",
    non_numeric_values == 0,
    "All telemetry values are numeric",
    f"{non_numeric_values:,} non-numeric values",
)

check(
    "NaN values",
    nan_values == 0,
    "No NaN telemetry values",
    f"{nan_values:,} NaN values",
)

check(
    "Infinite values",
    inf_values == 0,
    "No infinite telemetry values",
    f"{inf_values:,} infinite values",
)

if non_numeric_values == 0:
    print(f"Minimum telemetry value: {values.min():.6f}")
    print(f"Maximum telemetry value: {values.max():.6f}")
    print(f"Mean telemetry value:    {values.mean():.6f}")
    print(f"Std telemetry value:     {values.std():.6f}")


# ============================================================
# 12. RECORD ID
# ============================================================

section("12. RECORD ID INTEGRITY")

record_id_nulls = int(df["record_id"].isna().sum())
record_id_unique = int(df["record_id"].nunique())

check(
    "Record ID nulls",
    record_id_nulls == 0,
    "No missing record IDs",
    f"{record_id_nulls:,} missing record IDs",
)

check(
    "Record ID uniqueness",
    record_id_unique == len(df),
    "All record IDs are unique",
    f"{record_id_unique:,} unique IDs for {len(df):,} records",
)


# ============================================================
# 13. TOPIC / SENSOR CONSISTENCY
# ============================================================

section("13. TOPIC CONSISTENCY")

topic_sensor_mismatches = 0

for _, row in df.iterrows():
    topic = str(row["topic"])
    sensor_type = str(row["sensor_type"])

    # MQTT hijacking can legitimately use attacker/hijacked.
    if topic == "attacker/hijacked":
        continue

    expected_fragment = f"/{sensor_type}"

    if expected_fragment not in topic:
        topic_sensor_mismatches += 1

check(
    "Topic ↔ sensor consistency",
    topic_sensor_mismatches == 0,
    "Sensor topics are consistent with sensor_type",
    f"{topic_sensor_mismatches:,} topic/sensor mismatches",
)


# ============================================================
# 14. ATTACK VARIABILITY
# ============================================================

section("14. ATTACK TELEMETRY VARIABILITY")

variability_targets = [
    "False Data Injection Attack",
    "Sensor Spoofing Attack",
    "Sensor Drift Attack",
    "Sensor Noise Injection Attack",
    "Slow Drift Attack",
    "Intermittent Attack",
    "Motor Overload Attack",
    "Valve Stuck Attack",
]

variability_results = []

for attack_class in variability_targets:
    attack_df = df[
        df["attack_type"] == attack_class
    ]

    if attack_df.empty:
        warning(
            attack_class,
            "Class not present in dataset.",
        )
        continue

    grouped = (
        attack_df
        .groupby("sensor_type")["value"]
        .agg(["count", "nunique", "min", "max", "std"])
    )

    variable_groups = int(
        (grouped["nunique"] > 1).sum()
    )

    fixed_groups = int(
        (grouped["nunique"] == 1).sum()
    )

    variability_results.append(
        (
            attack_class,
            len(attack_df),
            variable_groups,
            fixed_groups,
        )
    )

    print(
        f"{attack_class:<35} "
        f"records={len(attack_df):>6,} | "
        f"variable sensor groups={variable_groups:>2} | "
        f"fixed sensor groups={fixed_groups:>2}"
    )

# We intentionally do NOT require every attack/sensor pair to vary.
# Network/control attacks can legitimately leave telemetry unchanged.
print()
print(
    "ℹ️ Fixed telemetry groups are NOT automatically failures. "
    "Network/control attacks can legitimately preserve sensor values."
)


# ============================================================
# 15. FDI-SPECIFIC VARIABILITY
# ============================================================

section("15. FALSE DATA INJECTION VARIABILITY")

fdi_df = df[
    df["attack_type"] == "False Data Injection Attack"
]

if fdi_df.empty:
    warning(
        "FDI variability",
        "No False Data Injection Attack records found.",
    )
else:
    fdi_groups = (
        fdi_df
        .groupby("sensor_type")["value"]
        .agg(["count", "nunique", "min", "max", "std"])
    )

    print(fdi_groups.to_string())

    fdi_variable_groups = int(
        (fdi_groups["nunique"] > 1).sum()
    )

    check(
        "FDI variability",
        fdi_variable_groups > 0,
        (
            f"{fdi_variable_groups} sensor groups show "
            "multiple FDI values"
        ),
        "FDI values appear completely fixed",
    )


# ============================================================
# 16. TIMESTAMP VALIDITY
# ============================================================

section("16. TIMESTAMP VALIDITY")

timestamps = pd.to_datetime(
    df["timestamp"],
    errors="coerce",
)

invalid_timestamps = int(timestamps.isna().sum())

check(
    "Timestamp parsing",
    invalid_timestamps == 0,
    "All timestamps are valid",
    f"{invalid_timestamps:,} invalid timestamps",
)

if invalid_timestamps == 0:

    unique_timestamps = int(timestamps.nunique())

    print(f"Unique timestamps: {unique_timestamps:,}")

    # We intentionally do NOT require timestamps to be monotonically
    # increasing because Replay Attack can legitimately reproduce
    # older timestamps / records.
    backward_jumps = int(
        (timestamps.diff().dt.total_seconds() < 0).sum()
    )

    forward_jumps = int(
        (timestamps.diff().dt.total_seconds() > 0).sum()
    )

    print(f"Backward timestamp transitions: {backward_jumps:,}")
    print(f"Forward timestamp transitions:  {forward_jumps:,}")

    if backward_jumps > 0:
        warning(
            "Timestamp ordering",
            (
                f"{backward_jumps:,} backward timestamp transitions "
                "exist. This is expected when Replay Attack records "
                "are present and should NOT be fixed by sorting the CSV."
            ),
        )
    else:
        print(
            "✅ Timestamp ordering: "
            "No backward timestamp transitions."
        )


# ============================================================
# 17. OUTLIER / EXTREME VALUE REPORT
# ============================================================

section("17. EXTREME VALUE / OUTLIER REPORT")

numeric_summary = (
    df.groupby("sensor_type")["value"]
    .agg(
        count="count",
        min="min",
        max="max",
        mean="mean",
        std="std",
        unique="nunique",
    )
    .sort_index()
)

print(numeric_summary.to_string())

print()
print(
    "ℹ️ Extreme values are reported rather than automatically rejected."
)
print(
    "   Attack simulations may intentionally create values outside "
    "normal operating ranges."
)


# ============================================================
# 18. SOURCE DISTRIBUTION
# ============================================================

section("18. SOURCE DISTRIBUTION")

source_counts = df["source"].value_counts(dropna=False)

print(source_counts.to_string())

check(
    "Source field",
    df["source"].isna().sum() == 0,
    "No missing source values",
    f"{int(df['source'].isna().sum()):,} missing source values",
)


# ============================================================
# 19. STATUS DISTRIBUTION
# ============================================================

section("19. STATUS DISTRIBUTION")

status_counts = df["status"].value_counts(dropna=False)

print(status_counts.to_string())

check(
    "Status field",
    df["status"].isna().sum() == 0,
    "No missing status values",
    f"{int(df['status'].isna().sum()):,} missing status values",
)


# ============================================================
# 20. UNIT DISTRIBUTION
# ============================================================

section("20. UNIT DISTRIBUTION")

unit_counts = df["unit"].value_counts(dropna=False)

print(unit_counts.to_string())

check(
    "Unit field",
    df["unit"].isna().sum() == 0,
    "No missing units",
    f"{int(df['unit'].isna().sum()):,} missing units",
)


# ============================================================
# 21. FINAL DATASET SUMMARY
# ============================================================

section("21. FINAL DATASET SUMMARY")

print(f"Total records:          {len(df):,}")
print(f"Total columns:          {len(df.columns)}")
print(f"Classes:                {len(class_names)}")
print(f"Sensor types:           {len(actual_sensor_types)}")
print(f"Duplicate rows:         {duplicate_rows:,}")
print(f"Duplicate record IDs:   {duplicate_record_ids:,}")
print(f"Duplicate sequences:    {duplicate_sequence_numbers:,}")
print(f"Unexpected null issues: {len(unexpected_nulls)}")
print(f"Invalid labels:         {len(invalid_labels)}")
print(f"Numeric invalid values: {non_numeric_values:,}")


# ============================================================
# 22. FINAL DECISION
# ============================================================

section("22. FINAL AUDIT RESULT")

print(f"Passed checks:   {passed}")
print(f"Warnings:        {warnings}")
print(f"Failed checks:   {failed}")

print()

if failed == 0:
    print("╔" + "═" * 66 + "╗")
    print("║" + " " * 14 + "100K DATASET AUDIT PASSED" + " " * 27 + "║")
    print("║" + " " * 10 + "READY FOR PHASE 4 ML REVIEW" + " " * 28 + "║")
    print("╚" + "═" * 66 + "╝")
else:
    print("╔" + "═" * 66 + "╗")
    print("║" + " " * 17 + "100K AUDIT FAILED" + " " * 31 + "║")
    print("║" + " " * 8 + "DO NOT FREEZE DATASET YET" + " " * 33 + "║")
    print("╚" + "═" * 66 + "╝")

print()
print("Audit completed.")