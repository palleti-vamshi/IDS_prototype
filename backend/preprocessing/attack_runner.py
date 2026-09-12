"""
Phase 3 Attack Runner

Controls balanced attack execution for dataset generation.

Responsibilities
----------------
• Execute the REAL attack objects owned by the simulator.
• Execute attacks through the REAL AttackManager.
• Generate records according to CLASS_QUOTAS.
• Repeat an attack when a single run does not produce
  enough accepted records.
• Stop an active attack immediately when its class
  quota is reached.
• Track live dataset progress.
• Preserve the existing LightX-IDS attack architecture.

Important
---------
This class does NOT create another AttackManager and does
NOT create duplicate attack objects.

When used with SimulationRunner:
    SimulationRunner.get_attack_manager()
    SimulationRunner.get_attacks()

When used directly with FactorySimulator:
    FactorySimulator.attack_manager
    FactorySimulator.attack_initializer.get_campaign_attacks()
"""

from __future__ import annotations

import time

from backend.preprocessing.generation_config import (
    ALL_CLASSES,
    ATTACK_CLASSES,
    CLASS_QUOTAS,
    NORMAL_CLASS,
    TARGET_DATASET_SIZE,
)


class AttackRunner:
    """
    Controls balanced Phase 3 dataset generation.

    The existing FactorySimulator owns the industrial
    simulation and the real AttackManager.

    AttackRunner only coordinates the dataset campaign.
    """

    def __init__(
        self,
        dataset_manager,
        simulation_runner,
    ) -> None:

        self.dataset_manager = dataset_manager

        self.simulation_runner = simulation_runner

        # ==================================================
        # REAL AttackManager
        # ==================================================
        #
        # Normal Phase 3 execution uses SimulationRunner,
        # which exposes get_attack_manager().
        #
        # The fallback supports direct FactorySimulator
        # testing without modifying FactorySimulator.
        # ==================================================

        if hasattr(
            simulation_runner,
            "get_attack_manager",
        ):

            self.attack_manager = (
                simulation_runner
                .get_attack_manager()
            )

        else:

            self.attack_manager = (
                simulation_runner.attack_manager
            )

        # ==================================================
        # REAL Attack Objects
        # ==================================================
        #
        # SimulationRunner exposes get_attacks().
        #
        # FactorySimulator exposes the same registered
        # campaign attacks through AttackInitializer.
        # ==================================================

        if hasattr(
            simulation_runner,
            "get_attacks",
        ):

            self.attacks = list(
                simulation_runner.get_attacks()
            )

        else:

            attack_initializer = (
                simulation_runner.attack_initializer
            )

            if hasattr(
                attack_initializer,
                "get_campaign_attacks",
            ):

                self.attacks = list(
                    attack_initializer
                    .get_campaign_attacks()
                )

            else:

                self.attacks = list(
                    attack_initializer
                    .attacks
                    .values()
                )

        self.total_attacks = len(
            self.attacks
        )

        self.completed_attacks = 0

        self.total_attack_runs = 0

        # ==================================================
        # Validation
        # ==================================================

        self._validate_attack_configuration()

    # ==================================================
    # Validation
    # ==================================================

    def _validate_attack_configuration(
        self,
    ) -> None:
        """
        Validate that the real attack framework contains
        exactly the configured Phase 3 attack classes.
        """

        framework_names = {
            attack.attack_name
            for attack in self.attacks
        }

        configured_names = set(
            ATTACK_CLASSES
        )

        if framework_names != configured_names:

            missing = (
                configured_names
                - framework_names
            )

            unexpected = (
                framework_names
                - configured_names
            )

            raise ValueError(
                "Attack configuration mismatch.\n"
                f"Missing attacks: "
                f"{sorted(missing)}\n"
                f"Unexpected attacks: "
                f"{sorted(unexpected)}"
            )

    # ==================================================
    # Dataset Helpers
    # ==================================================

    def _records(
        self,
    ) -> int:
        """
        Return total accepted dataset records.
        """

        return (
            self.dataset_manager.record_count()
        )

    # --------------------------------------------------

    def _normal_records(
        self,
    ) -> int:
        """
        Return accepted Normal records.
        """

        return (
            self.dataset_manager.normal_count()
        )

    # --------------------------------------------------

    def _attack_records(
        self,
        attack_name: str,
    ) -> int:
        """
        Return accepted records for one attack class.
        """

        return (
            self.dataset_manager.attack_count(
                attack_name
            )
        )

    # --------------------------------------------------

    def _target_reached(
        self,
    ) -> bool:
        """
        Return True when the complete dataset target
        has been reached.
        """

        return (
            self._records()
            >= TARGET_DATASET_SIZE
        )

    # --------------------------------------------------

    def _all_attack_quotas_reached(
        self,
    ) -> bool:
        """
        Return True when every attack class has reached
        its configured quota.
        """

        for attack_name in ATTACK_CLASSES:

            target = CLASS_QUOTAS.get(
                attack_name,
                0,
            )

            current = (
                self._attack_records(
                    attack_name
                )
            )

            if current < target:

                return False

        return True

    # --------------------------------------------------

    def _all_quotas_reached(
        self,
    ) -> bool:
        """
        Return True when Normal and every attack class
        have reached their quotas.
        """

        normal_target = CLASS_QUOTAS[
            NORMAL_CLASS
        ]

        if (
            self._normal_records()
            < normal_target
        ):

            return False

        return (
            self._all_attack_quotas_reached()
        )

    # ==================================================
    # Dataset Percentage
    # ==================================================

    def _dataset_percentage(
        self,
    ) -> float:
        """
        Calculate overall dataset completion percentage.
        """

        if TARGET_DATASET_SIZE <= 0:

            return 0.0

        percentage = (
            self._records()
            / TARGET_DATASET_SIZE
            * 100
        )

        return min(
            percentage,
            100.0,
        )

    # ==================================================
    # Main Campaign
    # ==================================================

    def run(
        self,
    ) -> None:
        """
        Execute the complete balanced dataset campaign.

        Normal traffic is collected first.

        Every attack class is then executed sequentially
        until its accepted record quota is reached.
        """

        print()
        print("=" * 72)
        print(
            "🚀 PHASE 3 ATTACK DATASET GENERATION"
        )
        print("=" * 72)

        print(
            f"Attack Classes : "
            f"{self.total_attacks}"
        )

        print(
            f"Total Classes  : "
            f"{len(ALL_CLASSES)}"
        )

        print(
            f"Target Records : "
            f"{TARGET_DATASET_SIZE}"
        )

        print()
        print("📊 CLASS QUOTAS")
        print("-" * 72)

        for class_name in ALL_CLASSES:

            print(
                f"{class_name:35}"
                f"{CLASS_QUOTAS[class_name]:>10}"
            )

        print("=" * 72)
        print()

        # ==================================================
        # Campaign
        # ==================================================

        while not self._all_quotas_reached():

            # ----------------------------------------------
            # Normal traffic first
            # ----------------------------------------------

            if (
                self._normal_records()
                < CLASS_QUOTAS[NORMAL_CLASS]
            ):

                self._run_normal_phase()

            # ----------------------------------------------
            # Complete dataset safety
            # ----------------------------------------------

            if self._target_reached():

                break

            progress_made = False

            # ----------------------------------------------
            # Run attack classes sequentially
            # ----------------------------------------------

            for attack in self.attacks:

                if self._target_reached():

                    break

                class_name = (
                    attack.attack_name
                )

                target_records = (
                    CLASS_QUOTAS.get(
                        class_name,
                        0,
                    )
                )

                current_records = (
                    self._attack_records(
                        class_name
                    )
                )

                # ------------------------------------------
                # Already complete
                # ------------------------------------------

                if (
                    current_records
                    >= target_records
                ):

                    continue

                progress_made = True

                self._run_attack_until_quota(
                    attack
                )

                # ------------------------------------------
                # Cooldown
                # ------------------------------------------

                if not self._target_reached():

                    time.sleep(1)

            # ----------------------------------------------
            # Safety guard
            # ----------------------------------------------

            if not progress_made:

                print()
                print(
                    "⚠️ No attack campaign progress "
                    "was made in this cycle."
                )

                print(
                    "Stopping to prevent an infinite loop."
                )

                break

        self._print_final_summary()

    # ==================================================
    # Normal Phase
    # ==================================================

    def _run_normal_phase(
        self,
    ) -> None:
        """
        Collect Normal traffic until its quota is reached.

        The FactorySimulator continues running in the
        background while this method observes the dataset.
        """

        target = CLASS_QUOTAS[
            NORMAL_CLASS
        ]

        current = (
            self._normal_records()
        )

        if current >= target:

            return

        print()
        print("=" * 72)
        print(
            "🟢 NORMAL TRAFFIC COLLECTION"
        )
        print("=" * 72)

        print(
            f"Target : {target} records"
        )

        print(
            f"Current: {current} records"
        )

        print("=" * 72)

        last_display = None

        while (
            self._normal_records()
            < target
        ):

            if self._target_reached():

                break

            normal_records = (
                self._normal_records()
            )

            total_records = (
                self._records()
            )

            display_state = (
                normal_records,
                total_records,
            )

            if display_state != last_display:

                print(
                    "\r"
                    f"🟢 Normal: "
                    f"{normal_records}/"
                    f"{target} | "
                    f"📊 Dataset: "
                    f"{total_records}/"
                    f"{TARGET_DATASET_SIZE} | "
                    f"📈 "
                    f"{self._dataset_percentage():.1f}%",
                    end="",
                    flush=True,
                )

                last_display = display_state

            time.sleep(0.1)

        print()

        print(
            f"✅ Normal quota reached: "
            f"{self._normal_records()}/"
            f"{target}"
        )

    # ==================================================
    # Attack Execution
    # ==================================================

    def _run_attack_until_quota(
        self,
        attack,
    ) -> None:
        """
        Run the SAME registered attack object repeatedly
        until its accepted class quota is reached.
        """

        class_name = (
            attack.attack_name
        )

        target_records = (
            CLASS_QUOTAS.get(
                class_name,
                0,
            )
        )

        current_records = (
            self._attack_records(
                class_name
            )
        )

        run_number = 0

        while (
            current_records
            < target_records
        ):

            if self._target_reached():

                break

            run_number += 1

            self.total_attack_runs += 1

            current_records = (
                self._attack_records(
                    class_name
                )
            )

            print()
            print("=" * 72)

            print(
                f"🚨 ATTACK: "
                f"{class_name}"
            )

            print(
                f"Run       : "
                f"{run_number}"
            )

            print(
                f"Current   : "
                f"{current_records}/"
                f"{target_records}"
            )

            print("=" * 72)

            # ----------------------------------------------
            # Return reusable attack object to READY
            # ----------------------------------------------

            if not attack.is_running:

                if hasattr(
                    attack,
                    "reset",
                ):

                    attack.reset()

            # ----------------------------------------------
            # Start through REAL AttackManager
            # ----------------------------------------------

            self.attack_manager.start_attack(
                attack.attack_id
            )

            # ----------------------------------------------
            # Observe active attack
            # ----------------------------------------------

            self._wait_for_attack(
                attack,
                target_records,
            )

            # ----------------------------------------------
            # Recalculate accepted records
            # ----------------------------------------------

            current_records = (
                self._attack_records(
                    class_name
                )
            )

            print()
            print(
                f"📦 {class_name}: "
                f"{current_records}/"
                f"{target_records}"
            )

            if (
                current_records
                < target_records
            ):

                print(
                    f"🔁 {class_name} "
                    f"requires another run."
                )

            else:

                print(
                    f"✅ {class_name} quota reached."
                )

            if (
                current_records
                < target_records
            ):

                time.sleep(1)

    # ==================================================
    # Wait for Attack
    # ==================================================

    def _wait_for_attack(
        self,
        attack,
        target_records: int,
    ) -> None:
        """
        Observe one active attack run.

        The FactorySimulator owns the simulation loop.

        AttackRunner does NOT call attack.update()
        directly.

        When the accepted records for this attack reach
        target_records, the REAL AttackManager stops the
        attack immediately.
        """

        last_display = None

        while True:

            elapsed = (
                attack.elapsed_time
            )

            duration = (
                attack.duration
            )

            attack_records = (
                self._attack_records(
                    attack.attack_name
                )
            )

            total_records = (
                self._records()
            )

            normal_records = (
                self._normal_records()
            )

            dataset_percentage = (
                self._dataset_percentage()
            )

            display_state = (
                int(elapsed * 10),
                attack_records,
                total_records,
                normal_records,
            )

            if display_state != last_display:

                print(
                    "\r"
                    f"🚨 {attack.attack_name} | "
                    f"⏱️ {elapsed:.1f}/"
                    f"{duration:.1f}s | "
                    f"📦 Attack: "
                    f"{attack_records}/"
                    f"{target_records} | "
                    f"📊 Dataset: "
                    f"{total_records}/"
                    f"{TARGET_DATASET_SIZE} | "
                    f"📈 "
                    f"{dataset_percentage:.1f}%",
                    end="",
                    flush=True,
                )

                last_display = display_state

            # ------------------------------------------
            # CRITICAL: class quota reached
            # ------------------------------------------

            if (
                attack_records
                >= target_records
            ):

                print()

                print(
                    f"🛑 {attack.attack_name} "
                    f"quota reached — "
                    f"stopping attack immediately."
                )

                self.attack_manager.stop_attack(
                    attack.attack_id
                )

                break

            # ------------------------------------------
            # Complete dataset reached
            # ------------------------------------------

            if self._target_reached():

                print()

                if attack.is_running:

                    self.attack_manager.stop_attack(
                        attack.attack_id
                    )

                break

            # ------------------------------------------
            # Natural attack completion
            # ------------------------------------------

            if attack.is_finished:

                print()

                break

            # ------------------------------------------
            # Attack stopped
            # ------------------------------------------

            if not attack.is_running:

                print()

                print(
                    f"⚠️ Attack stopped before "
                    f"quota completion: "
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
            self._attack_records(
                attack_name
            )
        )

        target = CLASS_QUOTAS.get(
            attack_name,
            0,
        )

        print(
            f"📦 {attack_name} Records: "
            f"{records}/"
            f"{target}"
        )

        if records < target:

            print(
                f"⚠️ WARNING: "
                f"{attack_name} produced only "
                f"{records}/"
                f"{target} records."
            )

        elif records == target:

            print(
                f"✅ {attack_name} quota reached."
            )

        else:

            print(
                f"⚠️ {attack_name} exceeded "
                f"its configured quota."
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
            self._records()
        )

        normal_records = (
            self._normal_records()
        )

        attack_records = (
            self.dataset_manager.attack_records
        )

        normal_target = CLASS_QUOTAS.get(
            NORMAL_CLASS,
            0,
        )

        attack_target = (
            TARGET_DATASET_SIZE
            - normal_target
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
            f"{TARGET_DATASET_SIZE}"
        )

        print(
            f"🟢 NORMAL RECORDS      : "
            f"{normal_records}/"
            f"{normal_target}"
        )

        print(
            f"🔴 ATTACK RECORDS     : "
            f"{attack_records}/"
            f"{attack_target}"
        )

        print(
            f"📈 DATASET PROGRESS   : "
            f"{self._dataset_percentage():.1f}%"
        )

        print("-" * 72)

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
            self.dataset_manager
            .get_distribution()
        )

        print()
        print()
        print("=" * 72)
        print(
            "🎉 DATASET GENERATION COMPLETED"
        )
        print("=" * 72)

        print(
            f"Attack Runs       : "
            f"{self.total_attack_runs}"
        )

        print(
            f"Total Records     : "
            f"{distribution['total']}/"
            f"{TARGET_DATASET_SIZE}"
        )

        print(
            f"Normal Records    : "
            f"{distribution['normal']}/"
            f"{CLASS_QUOTAS[NORMAL_CLASS]}"
        )

        print(
            f"Attack Records    : "
            f"{distribution['attack']}/"
            f"{TARGET_DATASET_SIZE - CLASS_QUOTAS[NORMAL_CLASS]}"
        )

        print(
            f"Quota Rejected    : "
            f"{distribution['quota_rejected']}"
        )

        print(
            f"Sensor Quota "
            f"Rejected         : "
            f"{distribution.get('sensor_quota_rejected', 0)}"
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

        # ----------------------------------------------
        # Normal
        # ----------------------------------------------

        print(
            f"{NORMAL_CLASS:35}"
            f"{distribution['normal']:>10}"
            f"{CLASS_QUOTAS[NORMAL_CLASS]:>10}"
        )

        # ----------------------------------------------
        # Attacks
        # ----------------------------------------------

        for attack_name in ATTACK_CLASSES:

            count = (
                distribution[
                    "attacks"
                ].get(
                    attack_name,
                    0,
                )
            )

            target = CLASS_QUOTAS.get(
                attack_name,
                0,
            )

            print(
                f"{attack_name:35}"
                f"{count:>10}"
                f"{target:>10}"
            )

        print("-" * 72)

        # ----------------------------------------------
        # Final validation
        # ----------------------------------------------

        all_complete = (
            distribution["normal"]
            >= CLASS_QUOTAS[NORMAL_CLASS]
            and all(
                distribution[
                    "attacks"
                ].get(
                    attack_name,
                    0,
                )
                >= CLASS_QUOTAS.get(
                    attack_name,
                    0,
                )
                for attack_name
                in ATTACK_CLASSES
            )
        )

        if all_complete:

            print(
                "✅ ALL CLASSES REACHED "
                "THEIR TARGET."
            )

        else:

            print(
                "⚠️ SOME CLASSES HAVE NOT "
                "REACHED THEIR TARGET."
            )

        print("=" * 72)