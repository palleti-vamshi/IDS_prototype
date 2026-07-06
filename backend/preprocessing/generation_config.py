"""
Dataset Generation Configuration
"""

# Dataset
OUTPUT_DATASET = "dataset/lightx_ids_dataset.csv"

# Target number of records
TARGET_RECORDS = 1000

# -------------------------------------------------
# Normal Traffic
# -------------------------------------------------

# Longer normal periods
MIN_NORMAL_DURATION = 15
MAX_NORMAL_DURATION = 40

# -------------------------------------------------
# Attack Duration
# -------------------------------------------------

# Shorter attacks
MIN_ATTACK_DURATION = 5
MAX_ATTACK_DURATION = 12

# -------------------------------------------------
# Cooldown
# -------------------------------------------------

# Longer cooldown after attacks
MIN_COOLDOWN = 10
MAX_COOLDOWN = 25

# -------------------------------------------------
# Attack Selection Probability
# -------------------------------------------------

ATTACK_WEIGHTS = {
    "DoS": 0.25,
    "Replay": 0.25,
    "Injection": 0.25,
    "Spoofing": 0.25,
}