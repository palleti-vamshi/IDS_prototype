"""
Machine Learning Configuration
LightX-IDS Phase 4
"""

from pathlib import Path

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = PROJECT_ROOT / "dataset"

LIGHTX_1K = DATASET_DIR / "lightx_ids_raw_1k.csv"
LIGHTX_10K = DATASET_DIR / "lightx_ids_raw_10k.csv"
LIGHTX_100K = DATASET_DIR / "lightx_ids_raw_100k.csv"

TON_IOT_DIR = (
    PROJECT_ROOT
    / "dataset_engineering"
    / "datasets"
)

MODEL_DIR = PROJECT_ROOT / "backend" / "ml" / "saved_models"

REPORT_DIR = PROJECT_ROOT / "backend" / "ml" / "reports"

# =====================================================
# Dataset Configuration
# =====================================================

TARGET_COLUMN = "label"

DROP_COLUMNS = [
    "timestamp",
    "attack_type",
    "sequence_number",
]

NUMERIC_COLUMNS = [
    "value",
]

CATEGORICAL_COLUMNS = [
    "topic",
    "device_id",
    "sensor_type",
    "unit",
    "status",
    "source",
]

# =====================================================
# ML Configuration
# =====================================================

RANDOM_STATE = 42

TEST_SIZE = 0.20

VALIDATION_SIZE = 0.10