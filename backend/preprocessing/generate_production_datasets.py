"""
generate_production_datasets.py

Generates the required Phase 3 production datasets:
- 1K records: dataset/lightx_ids_dataset_1k.csv
- 10K records: dataset/lightx_ids_dataset_10k.csv
- 100K records: dataset/lightx_ids_dataset_100k.csv

Follows strict safety rules:
- Does not modify Phase 4 ML code.
- Uses real simulation, authentic attacks, and natural exposure.
- Runs comprehensive audits on each dataset upon completion.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import time

from backend.preprocessing.dataset_manager import DatasetManager
from backend.preprocessing.pipeline import DatasetPipeline
from backend.preprocessing.simulation_runner import SimulationRunner
from backend.preprocessing.attack_runner import AttackRunner
from backend.preprocessing.generation_config import SIMULATION_TICK_RATE
from backend.preprocessing.tests.comprehensive_dataset_audit import audit_dataset


def generate_single_dataset(output_path: str, target_size: int) -> dict:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 80)
    print(f"🚀 GENERATING PRODUCTION DATASET: {target_size:,} records")
    print(f"Target Output: {path}")
    print("=" * 80)

    manager = DatasetManager(target_dataset_size=target_size)
    pipeline = DatasetPipeline(manager=manager)
    simulator = SimulationRunner(tick_rate=SIMULATION_TICK_RATE)

    start_time = time.time()
    try:
        simulator.start()
        time.sleep(1.0)

        pipeline.start()
        time.sleep(1.0)

        runner = AttackRunner(manager, simulator)
        runner.run()

    finally:
        print(f"\n💾 Saving dataset to: {output_path}...")
        manager.export_dataset(output_path)
        pipeline.stop()
        simulator.stop()
        elapsed = time.time() - start_time
        print(f"✅ Generation finished in {elapsed:.2f} seconds ({elapsed / 60:.2f} minutes).")

    # Run comprehensive audit
    print("\n🔍 Running Comprehensive Audit...")
    report = audit_dataset(output_path, expected_size=target_size)
    return report


def main():
    parser = argparse.ArgumentParser(description="LightX-IDS Phase 3 Production Dataset Generator")
    parser.add_argument(
        "--size",
        type=int,
        choices=[1000, 10000, 100000],
        help="Specific size to generate (1000, 10000, 100000). If omitted, all three are generated.",
    )
    args = parser.parse_args()

    targets = [
        (1000, "dataset/lightx_ids_dataset_1k.csv"),
        (10000, "dataset/lightx_ids_dataset_10k.csv"),
        (100000, "dataset/lightx_ids_dataset_100k.csv"),
    ]

    if args.size:
        targets = [(sz, out) for sz, out in targets if sz == args.size]

    reports = {}
    for size, out_file in targets:
        rep = generate_single_dataset(out_file, size)
        reports[size] = rep

    print("\n" + "=" * 80)
    print("🎉 ALL REQUESTED DATASETS GENERATED AND AUDITED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
