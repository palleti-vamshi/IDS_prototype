"""
LightX-IDS Phase 4.1 Temporal Root-Cause Diagnostic

READ-ONLY ANALYSIS:
- Does not modify datasets
- Does not modify ML code
- Does not train models
- Does not change labels
- Does not alter Phase 4.1 results

Purpose:
1. Reconstruct campaign timeline
2. Inspect Slow Drift Attack progression
3. Inspect temporal split distributions
4. Quantify Slow Drift Attack exposure
5. Prepare evidence for a controlled temporal experiment
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "dataset" / "lightx_ids_dataset_100k.csv"

print("=" * 80)
print("LIGHTX-IDS TEMPORAL ROOT-CAUSE DIAGNOSTIC")
print("=" * 80)

print(f"Repository : {ROOT}")
print(f"Dataset    : {DATASET}")

if not DATASET.exists():
    raise FileNotFoundError(f"Dataset not found: {DATASET}")


# ---------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------

df = pd.read_csv(DATASET)

print("\n[1] DATASET")
print("-" * 80)

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")

required = [
    "record_id",
    "timestamp",
    "device_id",
    "sensor_code",
    "value",
    "attack_type",
    "label",
    "sequence_number",
]

missing = [c for c in required if c not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

df = df.sort_values("record_id").reset_index(drop=True)


# ---------------------------------------------------------------------
# A. Campaign timeline
# ---------------------------------------------------------------------

print("\n[2] CAMPAIGN TIMELINE")
print("-" * 80)

campaign = (
    df.groupby("attack_type", dropna=False)
      .agg(
          rows=("record_id", "size"),
          first_record=("record_id", "min"),
          last_record=("record_id", "max"),
          first_timestamp=("timestamp", "min"),
          last_timestamp=("timestamp", "max"),
          label=("label", "first"),
      )
      .sort_values("first_record")
)

print(campaign.to_string())


# ---------------------------------------------------------------------
# B. Temporal split distribution
# ---------------------------------------------------------------------

print("\n[3] TEMPORAL SPLIT DISTRIBUTION")
print("-" * 80)

n = len(df)

train = df.iloc[: int(n * 0.80)]
val = df.iloc[int(n * 0.80): int(n * 0.90)]
test = df.iloc[int(n * 0.90):]

splits = {
    "TRAIN": train,
    "VALIDATION": val,
    "TEST": test,
}

for name, part in splits.items():

    print(f"\n{name}")
    print(f"Rows: {len(part):,}")

    print(
        part["attack_type"]
        .value_counts(dropna=False)
        .to_string()
    )

    slow = (part["attack_type"] == "Slow Drift Attack").sum()

    print(f"Slow Drift Attack samples: {slow:,}")


# ---------------------------------------------------------------------
# C. Slow Drift Attack progression
# ---------------------------------------------------------------------

print("\n[4] SLOW DRIFT PROGRESSION")
print("-" * 80)

slow = df[df["attack_type"] == "Slow Drift Attack"].copy()

if slow.empty:
    print("No Slow Drift Attack records found.")
else:

    print(f"Slow Drift Attack rows: {len(slow):,}")

    print(
        f"Record range: "
        f"{slow['record_id'].min()} -> {slow['record_id'].max()}"
    )

    print(
        f"Sequence range: "
        f"{slow['sequence_number'].min()} -> "
        f"{slow['sequence_number'].max()}"
    )

    print(
        f"Timestamp range: "
        f"{slow['timestamp'].min()} -> "
        f"{slow['timestamp'].max()}"
    )

    # Per-sensor progression
    progression = (
        slow.groupby(["device_id", "sensor_code"], dropna=False)
            .agg(
                rows=("value", "size"),
                first_value=("value", "first"),
                last_value=("value", "last"),
                min_value=("value", "min"),
                max_value=("value", "max"),
            )
    )

    progression["delta"] = (
        progression["last_value"] -
        progression["first_value"]
    )

    progression["absolute_delta"] = progression["delta"].abs()

    print("\nPer-sensor Slow Drift Attack progression:")
    print(progression.to_string())

    print("\nDelta statistics:")
    print(
        progression["delta"]
        .describe()
        .to_string()
    )


# ---------------------------------------------------------------------
# D. Slow Drift Attack by temporal split
# ---------------------------------------------------------------------

print("\n[5] SLOW DRIFT BY TEMPORAL SPLIT")
print("-" * 80)

for name, part in splits.items():

    sd = part[part["attack_type"] == "Slow Drift Attack"]

    print(f"\n{name}")
    print(f"Slow Drift Attack rows: {len(sd):,}")

    if len(sd) > 0:

        print(
            f"Record range: "
            f"{sd['record_id'].min()} -> "
            f"{sd['record_id'].max()}"
        )

        print(
            f"Value range: "
            f"{sd['value'].min():.6f} -> "
            f"{sd['value'].max():.6f}"
        )

        print(
            f"Mean value: "
            f"{sd['value'].mean():.6f}"
        )

        print(
            f"Std value: "
            f"{sd['value'].std():.6f}"
        )


# ---------------------------------------------------------------------
# E. Attack exposure matrix
# ---------------------------------------------------------------------

print("\n[6] ATTACK EXPOSURE MATRIX")
print("-" * 80)

attack_types = sorted(
    df.loc[df["label"] == 1, "attack_type"]
      .dropna()
      .unique()
)

exposure = pd.DataFrame(
    index=attack_types,
    columns=["TRAIN", "VALIDATION", "TEST"],
    data=0,
)

for attack in attack_types:

    for name, part in splits.items():

        exposure.loc[attack, name] = (
            part["attack_type"] == attack
        ).sum()

print(exposure.to_string())


# ---------------------------------------------------------------------
# F. Campaign transitions
# ---------------------------------------------------------------------

print("\n[7] CAMPAIGN TRANSITIONS")
print("-" * 80)

df["_prev_attack"] = df["attack_type"].shift(1)

transitions = (
    df.loc[df["attack_type"] != df["_prev_attack"],
           ["record_id", "_prev_attack", "attack_type"]]
      .copy()
)

print(transitions.to_string(index=False))


# ---------------------------------------------------------------------
# G. Slow Drift Attack exposure diagnosis
# ---------------------------------------------------------------------

print("\n[8] ROOT-CAUSE EVIDENCE")
print("-" * 80)

train_slow = (
    train["attack_type"] == "Slow Drift Attack"
).sum()

val_slow = (
    val["attack_type"] == "Slow Drift Attack"
).sum()

test_slow = (
    test["attack_type"] == "Slow Drift Attack"
).sum()

print(f"TRAIN Slow Drift Attack     : {train_slow:,}")
print(f"VALIDATION Slow Drift Attack: {val_slow:,}")
print(f"TEST Slow Drift Attack      : {test_slow:,}")

if train_slow == 0 and test_slow > 0:

    print(
        "\n>>> IMPORTANT:"
        "\n    Temporal training contains ZERO Slow Drift Attack samples."
        "\n    Therefore the temporal test is an unseen-attack"
        "\n    generalization experiment."
    )

if val_slow > 0 and test_slow > 0:

    print(
        "\n>>> Slow Drift Attack crosses validation -> test."
        "\n    This means the test contains a later portion of"
        "\n    the same campaign."
    )


# ---------------------------------------------------------------------
# H. Check expected simulation duration
# ---------------------------------------------------------------------

print("\n[9] SLOW DRIFT RUNTIME CONSISTENCY CHECK")
print("-" * 80)

EXPECTED_DURATION = 60.0
ATTACK_TICKS = 200
TICK_INTERVAL = 0.05

actual_simulation_duration = (
    ATTACK_TICKS * TICK_INTERVAL
)

print(f"Configured Slow Drift Attack duration : {EXPECTED_DURATION:.2f} s")
print(f"Attack runner ticks             : {ATTACK_TICKS}")
print(f"Tick interval                   : {TICK_INTERVAL:.2f} s")
print(
    f"Runner-implied duration         : "
    f"{actual_simulation_duration:.2f} s"
)

print(
    f"Configured max drift            : 10.0"
)

implied_drift = (
    actual_simulation_duration /
    EXPECTED_DURATION
) * 10.0

print(
    f"Expected drift at {actual_simulation_duration:.2f}s "
    f"if linear: {implied_drift:.4f}"
)

print("\nNOTE:")
print(
    "This is a diagnostic consistency calculation only."
)
print(
    "It does not modify the attack implementation or dataset."
)


# ---------------------------------------------------------------------
# I. Final summary
# ---------------------------------------------------------------------

print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print("=" * 80)

print(
    "1. Dataset campaign order reconstructed."
)

print(
    "2. Temporal train/validation/test attack exposure measured."
)

print(
    "3. Slow Drift Attack progression measured."
)

print(
    "4. Slow Drift Attack training exposure checked."
)

print(
    "5. Configured attack duration vs runner duration checked."
)

print(
    "\nNO FILES WERE MODIFIED BY THIS SCRIPT."
)

print("=" * 80)