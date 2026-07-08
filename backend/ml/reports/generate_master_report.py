"""
Generate Master Benchmark Report

Combines all benchmark reports into one master report.
"""

from pathlib import Path

import pandas as pd

from backend.ml.config import REPORT_DIR

FILES = {
    "LightX-1K": "benchmark_1k.csv",
    "LightX-10K": "benchmark_10k.csv",
    "LightX-100K": "benchmark_100k.csv",
}

tables = []

for dataset_name, filename in FILES.items():

    path = REPORT_DIR / filename

    if not path.exists():
        print(f"Missing: {filename}")
        continue

    df = pd.read_csv(path)

    df.insert(
        0,
        "dataset",
        dataset_name,
    )

    tables.append(df)

master = pd.concat(
    tables,
    ignore_index=True,
)

master.to_csv(
    REPORT_DIR / "master_benchmark_report.csv",
    index=False,
)

print("\n======================================")
print("MASTER BENCHMARK REPORT CREATED")
print("======================================")

print(master)

print("\nSaved to:")

print(
    REPORT_DIR /
    "master_benchmark_report.csv"
)

# ----------------------------------------
# Summary
# ----------------------------------------

print("\n======================================")
print("FINAL SUMMARY")
print("======================================")

best_accuracy = master.loc[
    master["accuracy"].idxmax()
]

smallest = master.loc[
    master["model_size_mb"].idxmin()
]

fastest = master.loc[
    master["training_time"].idxmin()
]

print(
    f"Best Accuracy Model : "
    f"{best_accuracy['model']}"
)

print(
    f"Dataset             : "
    f"{best_accuracy['dataset']}"
)

print(
    f"Accuracy            : "
    f"{best_accuracy['accuracy']*100:.2f}%"
)

print()

print(
    f"Smallest Model      : "
    f"{smallest['model']}"
)

print(
    f"Size                : "
    f"{smallest['model_size_mb']:.3f} MB"
)

print()

print(
    f"Fastest Training    : "
    f"{fastest['model']}"
)

print(
    f"Training Time       : "
    f"{fastest['training_time']:.4f} sec"
)

print("\n======================================")