"""
Dataset Generation Configuration

Phase 3
-------
Controls balanced dataset generation for LightX-IDS.

Dataset classes:
    1 Normal traffic
    17 attack types

The generator uses per-class quotas instead of relying only
on time-based attack durations.
"""

# ============================================================
# Dataset Output
# ============================================================

OUTPUT_DATASET = "dataset/lightx_ids_dataset.csv"


# ============================================================
# Dataset Generation Mode
# ============================================================

# Number of records required for EACH class.
#
# Initial validation:
#     100 records per class
#
# 18 classes × 100 = 1,800 records
#
# Later:
#     100,000 / 18 ≈ 5,555 records per class
#
#     1,000,000 / 18 ≈ 55,555 records per class

RECORDS_PER_CLASS = 10


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
# Total Dataset Size
# ============================================================

TOTAL_CLASSES = 1 + len(ATTACK_CLASSES)

TARGET_RECORDS = (
    RECORDS_PER_CLASS * TOTAL_CLASSES
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
# Validation
# ============================================================

if len(ATTACK_CLASSES) != 17:
    raise ValueError(
        f"Expected 17 attack classes, "
        f"found {len(ATTACK_CLASSES)}"
    )


if RECORDS_PER_CLASS <= 0:
    raise ValueError(
        "RECORDS_PER_CLASS must be greater than zero."
    )


if TARGET_RECORDS != (
    RECORDS_PER_CLASS * TOTAL_CLASSES
):
    raise ValueError(
        "TARGET_RECORDS calculation is inconsistent."
    )