"""
Automatic Dataset Generator

Starts the complete LightX-IDS dataset generation pipeline.
"""

import time

from backend.preprocessing.pipeline import DatasetPipeline
from backend.preprocessing.simulation_runner import SimulationRunner
from backend.preprocessing.attack_runner import AttackRunner


OUTPUT_FILE = "dataset/lightx_ids_dataset.csv"


def main():
    print("=" * 60)
    print("🚀 LightX-IDS Automatic Dataset Generator")
    print("=" * 60)

    # Create components
    simulator = SimulationRunner()
    pipeline = DatasetPipeline()
    attacks = AttackRunner(
        pipeline.manager
    )

    try:
        # Start simulator
        simulator.start()

        # Give simulator time to initialize
        time.sleep(2)

        # Start preprocessing pipeline
        pipeline.start()

        # Run attack scenarios
        attacks.run()

    except KeyboardInterrupt:
        print("\n⚠️ Dataset generation interrupted.")

    finally:
        print("\n💾 Exporting dataset...")

        pipeline.manager.export_dataset(
            OUTPUT_FILE
        )
        pipeline.stop()
        simulator.stop()

        print("\n✅ Dataset generation completed.")
        print(f"📄 Dataset saved to: {OUTPUT_FILE}")

        print("=" * 60)


if __name__ == "__main__":
    main()