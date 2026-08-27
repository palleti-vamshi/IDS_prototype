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
    print(
        "🚀 LightX-IDS Automatic Dataset Generator"
    )
    print("=" * 60)

    simulator = SimulationRunner()

    pipeline = DatasetPipeline()

    try:

        # ==========================================
        # Start Factory Simulator
        # ==========================================

        simulator.start()

        # Give simulator time to initialize
        time.sleep(2)

        # ==========================================
        # Start Dataset Pipeline
        # ==========================================

        pipeline.start()

        # Give collector time to subscribe
        time.sleep(2)

        # ==========================================
        # Create Attack Runner
        # ==========================================

        attacks = AttackRunner(
            pipeline.manager,
            simulator,
        )

        # ==========================================
        # Run Dataset Generation
        # ==========================================

        attacks.run()

    except KeyboardInterrupt:

        print(
            "\n⚠️ Dataset generation interrupted."
        )

    finally:

        print(
            "\n💾 Exporting dataset..."
        )

        pipeline.manager.export_dataset(
            OUTPUT_FILE
        )

        pipeline.stop()

        simulator.stop()

        print(
            "\n✅ Dataset generation completed."
        )

        print(
            f"📄 Dataset saved to: "
            f"{OUTPUT_FILE}"
        )

        print("=" * 60)


if __name__ == "__main__":

    main()