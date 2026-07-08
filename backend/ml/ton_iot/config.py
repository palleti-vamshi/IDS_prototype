"""
TON-IoT Configuration
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    PROJECT_ROOT
    / "dataset_engineering"
    / "datasets"
    / "standardized"
    / "lightx_combined.csv"
)

TARGET_COLUMN = "label"

DROP_COLUMNS = [
    "date_raw",
    "timestamp",
    "attack_type",
]

NUMERIC_COLUMNS = [

    # Original Sensor Features
    "sensor_reading_1",
    "sensor_reading_2",
    "sensor_reading_3",
    "sensor_reading_4",

    # Engineered Sensor Features
    "sensor_mean",
    "sensor_max",
    "sensor_min",
    "sensor_std",
    "sensor_range",
    "sensor_ratio_12",
    "sensor_ratio_34",
    "sensor_missing_count",

    # Network Features
    "source_port",
    "destination_port",
    "duration",
    "src_bytes",
    "dst_bytes",
    "total_bytes",
    "byte_difference",
    "byte_ratio",
    "port_difference",
    "has_duration",
]

CATEGORICAL_COLUMNS = [
    "source_ip",
    "destination_ip",
    "protocol",
    "service",
]

TEST_SIZE = 0.20

VALIDATION_SIZE = 0.10

RANDOM_STATE = 42