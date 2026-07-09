"""
LightX-IDS Machine Learning Configuration

Central configuration file for all ML modules.
"""

from pathlib import Path

# ==========================================================
# PROJECT PATHS
# ==========================================================

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

MODEL_DIR = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "saved_models"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "reports"
)

# Create directories automatically
MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# DATASET CONFIGURATION
# ==========================================================

TARGET_COLUMN = "label"

DROP_COLUMNS = [
    "timestamp",
    "attack_type",
    "sequence_number",
]

NUMERIC_COLUMNS = [

    # Original Feature
    "value",

    # Existing Engineered Features
    "value_change",
    "device_message_count",
    "sensor_message_count",
    "time_delta",
    "is_duplicate_value",

    # New Engineered Features
    "rolling_mean",
    "rolling_std",
    "rolling_max",
    "rolling_min",
    "percentage_change",
    "z_score",
    "device_mean_deviation",
]

CATEGORICAL_COLUMNS = [
    "topic",
    "device_id",
    "sensor_type",
    "unit",
    "status",
    "source",
]

# ==========================================================
# DATA SPLITTING
# ==========================================================

TEST_SIZE = 0.20
VALIDATION_SIZE = 0.10
RANDOM_STATE = 42

# ==========================================================
# MODEL CONFIGURATION
# ==========================================================

SUPPORTED_MODELS = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "xgboost",
]

# ==========================================================
# REPORT FILES
# ==========================================================

BENCHMARK_1K = "benchmark_1k"
BENCHMARK_10K = "benchmark_10k"
BENCHMARK_100K = "benchmark_100k"
BENCHMARK_TON_IOT = "benchmark_ton_iot"

# ==========================================================
# DEPLOYMENT TARGET
# ==========================================================

LIGHTWEIGHT_MODEL_PRIORITY = [
    "decision_tree",
    "logistic_regression",
    "random_forest",
    "xgboost",
]

TON_IOT_DIR = (
    PROJECT_ROOT
    / "dataset_engineering"
    / "datasets"
)