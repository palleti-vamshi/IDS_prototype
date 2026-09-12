"""
Dataset Generation Configuration

Phase 3
-------
Controls balanced dataset generation for LightX-IDS.

Dataset classes:
    1 Normal
    17 attack types

The generator supports scalable dataset targets:
    1,000
    10,000
    100,000
    1,000,000 records

Records are distributed as evenly as mathematically possible
across all classes.
"""

# ============================================================
# Dataset Output
# ============================================================

OUTPUT_DATASET = "dataset/lightx_ids_dataset.csv"


# ============================================================
# Dataset Generation Target
# ============================================================

# Select the total number of records to generate.
#
# Supported validation / production targets:
#
#     1,000
#     10,000
#     100,000
#     1,000,000
#
# Keep this at 1,000 initially.

TARGET_DATASET_SIZE = 100_000


SUPPORTED_DATASET_SIZES = (
    1_000,
    10_000,
    100_000,
    1_000_000,
)


# ============================================================
# Class Definitions
# ============================================================

NORMAL_CLASS = "Normal"


ATTACK_CLASSES = [
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
]


# ============================================================
# Total Classes
# ============================================================

TOTAL_CLASSES = 1 + len(ATTACK_CLASSES)


ALL_CLASSES = [
    NORMAL_CLASS,
    *ATTACK_CLASSES,
]


# ============================================================
# Validation
# ============================================================

if len(ATTACK_CLASSES) != 17:
    raise ValueError(
        f"Expected 17 attack classes, "
        f"found {len(ATTACK_CLASSES)}"
    )


if TARGET_DATASET_SIZE not in SUPPORTED_DATASET_SIZES:
    raise ValueError(
        f"Unsupported TARGET_DATASET_SIZE: "
        f"{TARGET_DATASET_SIZE}. "
        f"Supported sizes: {SUPPORTED_DATASET_SIZES}"
    )


if TARGET_DATASET_SIZE < TOTAL_CLASSES:
    raise ValueError(
        "TARGET_DATASET_SIZE must be at least "
        f"{TOTAL_CLASSES} records."
    )


# ============================================================
# Balanced Class Quotas
# ============================================================

def calculate_class_quotas(
    total_records: int,
) -> dict[str, int]:
    """
    Calculate balanced record quotas for all classes.

    If the total cannot be divided equally among the
    18 classes, the remainder is distributed one record
    at a time to the first classes.

    Example:
        1,000 / 18

        Base quota = 55
        Remainder  = 10

        Therefore:
            first 10 classes -> 56 records
            remaining 8       -> 55 records

        Total = 1,000 records.
    """

    if total_records < TOTAL_CLASSES:
        raise ValueError(
            "Total records must be at least "
            f"{TOTAL_CLASSES}."
        )

    base_quota, remainder = divmod(
        total_records,
        TOTAL_CLASSES,
    )

    quotas = {}

    for index, class_name in enumerate(ALL_CLASSES):

        quotas[class_name] = (
            base_quota
            + (1 if index < remainder else 0)
        )

    return quotas


# ============================================================
# Active Class Quotas
# ============================================================

CLASS_QUOTAS = calculate_class_quotas(
    TARGET_DATASET_SIZE
)


# ============================================================
# Normal Traffic Timing
# ============================================================

MIN_NORMAL_DURATION = 15
MAX_NORMAL_DURATION = 40


# ============================================================
# Attack Timing
# ============================================================

MIN_ATTACK_DURATION = 5
MAX_ATTACK_DURATION = 12


# ============================================================
# Cooldown
# ============================================================

MIN_COOLDOWN = 10
MAX_COOLDOWN = 25


# ============================================================
# Dataset Balance
# ============================================================

BALANCED_DATASET = True


# ============================================================
# Final Consistency Validation
# ============================================================

if sum(CLASS_QUOTAS.values()) != TARGET_DATASET_SIZE:
    raise ValueError(
        "Class quota calculation is inconsistent."
    )


if len(CLASS_QUOTAS) != TOTAL_CLASSES:
    raise ValueError(
        "Class quota count does not match "
        "the total number of classes."
    )