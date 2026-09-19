"""
LightX-IDS Machine Learning Configuration

Central configuration for the Phase 4 machine-learning pipeline.

This file contains:
- Dataset paths
- Dataset schema
- Target configuration
- Feature configuration
- Train/validation/test split configuration
- Supported models
- Benchmark configuration
- Model/report directories
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = PROJECT_ROOT / "dataset"

MODEL_DIR = PROJECT_ROOT / "backend" / "ml" / "saved_models"

REPORT_DIR = PROJECT_ROOT / "backend" / "ml" / "reports"


# Create output directories automatically.
MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LIGHTX-IDS DATASETS
# ============================================================

LIGHTX_1K = (
    DATASET_DIR
    / "lightx_ids_dataset_1k.csv"
)

LIGHTX_10K = (
    DATASET_DIR
    / "lightx_ids_dataset_10k.csv"
)

LIGHTX_100K = (
    DATASET_DIR
    / "lightx_ids_dataset.csv"
)


# ============================================================
# TON-IOT DATASET
# ============================================================

TON_IOT_DIR = (
    PROJECT_ROOT
    / "dataset_engineering"
    / "datasets"
)


# ============================================================
# LIGHTX-IDS DATASET SCHEMA
# ============================================================

LIGHTX_REQUIRED_COLUMNS = [
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


# ============================================================
# TARGET CONFIGURATION
# ============================================================

TARGET_COLUMN = "label"


LIGHTX_LABEL_MAPPING = {
    0: "Normal",
    1: "Attack",
}


# ============================================================
# COLUMNS THAT MUST NOT BE USED AS FEATURES
# ============================================================

DROP_COLUMNS = [
    "record_id",
    "timestamp",
    "attack_type",
    "sequence_number",
    "device_message_count",
    "sensor_message_count",
]


# ============================================================
# NUMERIC FEATURES
# ============================================================

NUMERIC_COLUMNS = [
    "value",
    "value_change",
    "time_delta",
    "is_duplicate_value",
    "rolling_mean",
    "rolling_std",
    "rolling_max",
    "rolling_min",
    "percentage_change",
    "z_score",
    "device_mean_deviation",
]


# ============================================================
# CATEGORICAL FEATURES
# ============================================================

CATEGORICAL_COLUMNS = [
    "topic",
    "device_id",
    "sensor_type",
    "unit",
    "status",
    "source",
]


# ============================================================
# DATA SPLIT CONFIGURATION
# ============================================================

# Final benchmark protocol:
#
# Training      = 80%
# Validation    = 10%
# Testing       = 10%
#
# The validation set is used for threshold selection.
# The test set is used only for final evaluation.

TEST_SIZE = 0.20

VALIDATION_SIZE = 0.10

RANDOM_STATE = 42


# ============================================================
# THRESHOLD CONFIGURATION
# ============================================================

# The threshold is selected using the validation set only.
#
# F1 is used as the primary operating-point metric because
# LightX-IDS is an intrusion-detection problem where both
# missed attacks and false alarms matter.
#
# Accuracy remains a reported benchmark metric.

PRIMARY_THRESHOLD_METRIC = "f1"

THRESHOLD_MIN = 0.10

THRESHOLD_MAX = 0.90

THRESHOLD_STEP = 0.05

DEFAULT_THRESHOLD = 0.50


# ============================================================
# SUPPORTED MACHINE-LEARNING MODELS
# ============================================================

SUPPORTED_MODELS = [
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "xgboost",
]


# ============================================================
# MODEL PRIORITY
# ============================================================

# Used when considering lightweight deployment.
#
# This does NOT determine the benchmark winner.
# Final model selection must consider multiple IDS metrics
# and deployment characteristics.

LIGHTWEIGHT_MODEL_PRIORITY = [
    "decision_tree",
    "logistic_regression",
    "random_forest",
    "xgboost",
]


# ============================================================
# BENCHMARK NAMES
# ============================================================

BENCHMARK_1K = "benchmark_1k"

BENCHMARK_10K = "benchmark_10k"

BENCHMARK_100K = "benchmark_100k"

BENCHMARK_TON_IOT = "benchmark_ton_iot"