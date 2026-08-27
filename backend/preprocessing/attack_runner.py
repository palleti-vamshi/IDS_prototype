"""
Attack Runner

Controls attack execution for Phase 3 dataset generation.

Responsibilities:
    • Execute the simulator's real attack objects
    • Wait for each attack to complete
    • Ensure attacks are executed through the simulator's AttackManager
    • Track attack progress
    • Track live dataset record progress
    • Display dataset generation progress
"""

from __future__ import annotations

import time

from backend.preprocessing.generation_config import (
    ATTACK_CLASSES,
    RECORDS_PER_CLASS,
    TARGET_RECORDS,
)


class AttackRunner:
    """
    Executes the real attack framework owned by the
    FactorySimulator and coordinates Phase 3 generation.
    """

    def __init__(
        self,
        dataset_manager,
        simulation_runner,
    ) -> None:

        self.dataset_manager = dataset_manager

        self.simulation_runner = simulation_runner

        # --------------------------------------------------
        # Use the simulator's REAL AttackManager
        # --------------------------------------------------

        self.attack_manager = (
            simulation_runner.get_attack_manager()
        )

        # --------------------------------------------------
        # Use the actual attack objects created by
        # AttackInitializer
        # --------------------------------------------------

        self.attacks = (
            simulation_runner.get_attacks()
        )

        self.total_attacks = len(
            self.attacks
        )

        self.completed_attacks = 0

    # ==================================================
    # Run
    # ==================================================

    def run(self) -> None:
        """
        Execute all attacks sequentially.
        """

        print()
        print("=" * 72)
        print("🚀 PHASE 3 ATTACK DATASET GENERATION")
        print("=" * 72)

        print(
            f"Attack Classes : "
            f"{self.total_attacks}"
        )

        print(
            f"Records/Class  : "
            f"{RECORDS_PER_CLASS}"
        )

        print(
            f"Target Records : "
            f"{TARGET_RECORDS}"
        )

        print("=" * 72)
        print()

        # --------------------------------------------------
        # Execute attacks one by one
        # --------------------------------------------------

        for index, attack in enumerate(
            self.attacks,
            start=1,
        ):

            class_name = attack.attack_name

            # ----------------------------------------------
            # Skip classes whose quota is already complete
            # ----------------------------------------------

            if self.dataset_manager.class_quota_reached(
                class_name
            ):

                print(
                    f"⏭️ Skipping {class_name} "
                    f"(quota already reached)"
                )

                self.completed_attacks += 1

                self._print_progress()

                continue

            # ----------------------------------------------
            # Start attack
            # ----------------------------------------------

            print()
            print("=" * 72)

            print(
                f"🚨 ATTACK "
                f"{index}/{self.total_attacks}"
            )

            print(
                f"Attack : "
                f"{class_name}"
            )

            print("=" * 72)

            attack_id = attack.attack_id

            print(
                f"▶ Starting: "
                f"{attack_id}"
            )

            # ----------------------------------------------
            # Start through REAL AttackManager
            # ----------------------------------------------

            self.attack_manager.start_attack(
                attack_id
            )

            # ----------------------------------------------
            # Wait for simulator to complete attack
            # ----------------------------------------------

            self._wait_for_attack(
                attack
            )

            # ----------------------------------------------
            # Attack completed
            # ----------------------------------------------

            self.completed_attacks += 1

            print()

            print(
                f"✅ Attack completed: "
                f"{class_name}"
            )

            self._print_attack_records(
                class_name
            )

            self._print_progress()

            # ----------------------------------------------
            # Small cooldown
            # ----------------------------------------------

            if (
                self.completed_attacks
                < self.total_attacks
            ):

                time.sleep(1)

        # --------------------------------------------------
        # Final summary
        # --------------------------------------------------

        self._print_final_summary()

    # ==================================================
    # Wait for Attack
    # ==================================================

    def _wait_for_attack(
        self,
        attack,
    ) -> None:
        """
        Wait until the simulator finishes the attack.

        While waiting, continuously display:

            • Attack time
            • Attack records
            • Total dataset records
            • Normal records
            • Attack records
            • Dataset percentage
        """

        last_display = None

        while True:

            # ----------------------------------------------
            # Current attack information
            # ----------------------------------------------

            elapsed = attack.elapsed_time

            duration = attack.duration

            attack_records = (
                self.dataset_manager.attack_count(
                    attack.attack_name
                )
            )

            total_records = (
                self.dataset_manager.record_count()
            )

            normal_records = (
                self.dataset_manager.normal_count()
            )

            total_attack_records = (
                self.dataset_manager.attack_records
            )

            dataset_percentage = (
                self._dataset_percentage()
            )

            # ----------------------------------------------
            # Build live status
            # ----------------------------------------------

            display_state = (
                int(elapsed * 10),
                attack_records,
                total_records,
                normal_records,
                total_attack_records,
            )

            # ----------------------------------------------
            # Only refresh when something changes
            # ----------------------------------------------

            if display_state != last_display:

                print(
                    "\r"
                    f"🚨 {attack.attack_name} | "
                    f"⏱️ {elapsed:.1f}/{duration:.1f}s | "
                    f"📦 Attack: "
                    f"{attack_records}/{RECORDS_PER_CLASS} | "
                    f"📊 Dataset: "
                    f"{total_records}/{TARGET_RECORDS} | "
                    f"📈 {dataset_percentage:.1f}%",
                    end="",
                    flush=True,
                )

                last_display = display_state

            # ----------------------------------------------
            # Attack finished normally
            # ----------------------------------------------

            if attack.is_finished:

                print()

                break

            # ----------------------------------------------
            # Attack stopped unexpectedly
            # ----------------------------------------------

            if not attack.is_running:

                print()

                print(
                    f"⚠️ Attack stopped before normal "
                    f"completion: "
                    f"{attack.attack_name}"
                )

                break

            time.sleep(0.1)

    # ==================================================
    # Attack Records
    # ==================================================

    def _print_attack_records(
        self,
        attack_name: str,
    ) -> None:
        """
        Display records collected for one attack class.
        """

        records = (
            self.dataset_manager.attack_count(
                attack_name
            )
        )

        print(
            f"📦 {attack_name} Records: "
            f"{records}/"
            f"{RECORDS_PER_CLASS}"
        )

        # ----------------------------------------------
        # Warn if quota was not reached
        # ----------------------------------------------

        if records < RECORDS_PER_CLASS:

            print(
                f"⚠️ WARNING: "
                f"{attack_name} produced only "
                f"{records}/"
                f"{RECORDS_PER_CLASS} records."
            )

        elif records == RECORDS_PER_CLASS:

            print(
                f"✅ {attack_name} quota reached."
            )

    # ==================================================
    # Overall Progress
    # ==================================================

    def _print_progress(
        self,
    ) -> None:
        """
        Display overall dataset generation progress.
        """

        total_records = (
            self.dataset_manager.record_count()
        )

        normal_records = (
            self.dataset_manager.normal_count()
        )

        attack_records = (
            self.dataset_manager.attack_records
        )

        print()
        print("-" * 72)

        print(
            f"📊 ATTACK PROGRESS     : "
            f"{self.completed_attacks}/"
            f"{self.total_attacks}"
        )

        print(
            f"📦 DATASET RECORDS    : "
            f"{total_records}/"
            f"{TARGET_RECORDS}"
        )

        print(
            f"🟢 NORMAL RECORDS     : "
            f"{normal_records}/"
            f"{RECORDS_PER_CLASS}"
        )

        print(
            f"🔴 ATTACK RECORDS     : "
            f"{attack_records}/"
            f"{TARGET_RECORDS - RECORDS_PER_CLASS}"
        )

        print(
            f"📈 DATASET PROGRESS   : "
            f"{self._dataset_percentage():.1f}%"
        )

        print("-" * 72)

    # ==================================================
    # Dataset Percentage
    # ==================================================

    def _dataset_percentage(
        self,
    ) -> float:
        """
        Calculate overall dataset completion percentage.
        """

        total_records = (
            self.dataset_manager.record_count()
        )

        if TARGET_RECORDS <= 0:

            return 0.0

        percentage = (
            total_records
            / TARGET_RECORDS
            * 100
        )

        return min(
            percentage,
            100.0,
        )

    # ==================================================
    # Final Summary
    # ==================================================

    def _print_final_summary(
        self,
    ) -> None:
        """
        Display final dataset generation statistics.
        """

        distribution = (
            self.dataset_manager.get_distribution()
        )

        print()
        print()
        print("=" * 72)
        print("🎉 DATASET GENERATION COMPLETED")
        print("=" * 72)

        print(
            f"Attacks Completed : "
            f"{self.completed_attacks}/"
            f"{self.total_attacks}"
        )

        print(
            f"Total Records     : "
            f"{distribution['total']}/"
            f"{TARGET_RECORDS}"
        )

        print(
            f"Normal Records    : "
            f"{distribution['normal']}"
        )

        print(
            f"Attack Records    : "
            f"{distribution['attack']}"
        )

        print(
            f"Quota Rejected    : "
            f"{distribution['quota_rejected']}"
        )

        print()
        print("📊 CLASS DISTRIBUTION")
        print("-" * 72)

        print(
            f"{'Class':35}"
            f"{'Records':>10}"
            f"{'Target':>10}"
        )

        print("-" * 72)

        print(
            f"{'Normal':35}"
            f"{distribution['normal']:>10}"
            f"{RECORDS_PER_CLASS:>10}"
        )

        for attack_name in ATTACK_CLASSES:

            count = (
                distribution["attacks"].get(
                    attack_name,
                    0,
                )
            )

            print(
                f"{attack_name:35}"
                f"{count:>10}"
                f"{RECORDS_PER_CLASS:>10}"
            )

        print("=" * 72)