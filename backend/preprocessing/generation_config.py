"""
Dataset Generation Configuration
"""

# Dataset
OUTPUT_DATASET = "dataset/lightx_ids_dataset.csv"

# Target number of records
TARGET_RECORDS = 100000

# Random normal traffic duration
MIN_NORMAL_DURATION = 5
MAX_NORMAL_DURATION = 20

# Random attack duration
MIN_ATTACK_DURATION = 10
MAX_ATTACK_DURATION = 30

# Random cooldown
MIN_COOLDOWN = 5
MAX_COOLDOWN = 15

# Attack probabilities
ATTACK_WEIGHTS = {
    "DoS": 0.30,
    "Replay": 0.25,
    "Injection": 0.20,
    "Spoofing": 0.25,
}