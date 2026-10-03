"""
Phase 3 Attack Runner

Controls realistic industrial campaign execution for dataset generation.

Responsibilities
----------------
• Execute the REAL attack objects owned by the simulator.
• Execute attacks through the REAL AttackManager.
• Coordinate an authentic industrial campaign:
    Normal Baseline -> Attack -> Cooldown -> Attack -> ... -> Final Normal
• Retain genuine telemetry without artificial class or sensor quotas.
• Natural attack exposure determined by duration, sensor scope, and physical locality.
• Track live dataset progress.
• Preserve the existing LightX-IDS attack architecture.
"""

from __future__ import annotations

import time

from backend.preprocessing.generation_config import (
    ALL_CLASSES,
    ATTACK_CLASSES,
    CLASS_QUOTAS,
    NORMAL_CLASS,
    TARGET_DATASET_SIZE,
    DEFAULT_BASELINE_DURATION,
    DEFAULT_ATTACK_DURATION,
    DEFAULT_COOLDOWN_DURATION,
)


class AttackRunner:
    """
    Controls realistic industrial campaign execution for LightX-IDS dataset generation.

    The existing FactorySimulator owns the industrial simulation and the real AttackManager.
    AttackRunner coordinates the campaign timeline across all 17 registered attack types.
    """

    def __init__(
        self,
        dataset_manager,
        simulation_runner,
    ) -> None:

        self.dataset_manager = dataset_manager
        self.simulation_runner = simulation_runner

        # Target dataset size from dataset_manager
        self.target_dataset_size = getattr(
            dataset_manager,
            "target_dataset_size",
            TARGET_DATASET_SIZE,
        )

        # ==================================================
        # REAL AttackManager
        # ==================================================
        if hasattr(simulation_runner, "get_attack_manager"):
            self.attack_manager = simulation_runner.get_attack_manager()
        else:
            self.attack_manager = simulation_runner.attack_manager

        # ==================================================
        # REAL Attack Objects
        # ==================================================
        if hasattr(simulation_runner, "get_attacks"):
            self.attacks = list(simulation_runner.get_attacks())
        else:
            attack_initializer = simulation_runner.attack_initializer
            if hasattr(attack_initializer, "get_campaign_attacks"):
                self.attacks = list(attack_initializer.get_campaign_attacks())
            else:
                self.attacks = list(attack_initializer.attacks.values())

        self.total_attacks = len(self.attacks)
        self.total_attack_runs = 0

        # ==================================================
        # Campaign Timing Configuration
        # ==================================================
        # 19 physical sensors publish every simulation tick.
        # Tick allocations are planned to allow all 17 attacks
        # and cooldowns to execute before reaching the target size.
        if self.target_dataset_size <= 1_500:
            self.baseline_ticks = 1
            self.attack_ticks = 2
            self.cooldown_ticks = 1
        elif self.target_dataset_size <= 15_000:
            self.baseline_ticks = 15
            self.attack_ticks = 20
            self.cooldown_ticks = 8
        elif self.target_dataset_size <= 150_000:
            self.baseline_ticks = 150
            self.attack_ticks = 200
            self.cooldown_ticks = 80
        else:
            total_ticks = self.target_dataset_size // 19
            self.attack_ticks = max(1, int(total_ticks * 0.65 // self.total_attacks))
            self.cooldown_ticks = max(1, int(total_ticks * 0.25 // self.total_attacks))
            self.baseline_ticks = max(1, int(total_ticks * 0.05))

        sim = getattr(self.simulation_runner, "simulator", None)
        clock = getattr(sim, "clock", None) if sim else None
        self.tick_rate = getattr(clock, "tick_rate", 0.05)

        self.baseline_duration = self.baseline_ticks * self.tick_rate
        self.attack_duration = self.attack_ticks * self.tick_rate
        self.cooldown_duration = self.cooldown_ticks * self.tick_rate

        # Validation
        self._validate_attack_configuration()

    # ==================================================
    # Validation
    # ==================================================

    def _validate_attack_configuration(self) -> None:
        """
        Validate that the real attack framework contains
        exactly the configured Phase 3 attack classes.
        """
        framework_names = {attack.attack_name for attack in self.attacks}
        configured_names = set(ATTACK_CLASSES)

        if framework_names != configured_names:
            missing = configured_names - framework_names
            unexpected = framework_names - configured_names
            raise ValueError(
                "Attack configuration mismatch.\n"
                f"Missing attacks: {sorted(missing)}\n"
                f"Unexpected attacks: {sorted(unexpected)}"
            )

    # ==================================================
    # Dataset Helpers
    # ==================================================

    def _records(self) -> int:
        return self.dataset_manager.record_count()

    def _normal_records(self) -> int:
        return self.dataset_manager.normal_count()

    def _attack_records(self, class_name: str) -> int:
        return self.dataset_manager.attack_count(class_name)

    def _target_reached(self) -> bool:
        if hasattr(self.dataset_manager, "is_target_reached"):
            return self.dataset_manager.is_target_reached()
        return self._records() >= self.target_dataset_size

    def _dataset_percentage(self) -> float:
        if self.target_dataset_size <= 0:
            return 0.0
        return min((self._records() / self.target_dataset_size) * 100.0, 100.0)

    def _sim_elapsed_time(self) -> float:
        """Return simulation clock elapsed time if available, else wall-clock."""
        sim = getattr(self.simulation_runner, "simulator", None)
        if sim and hasattr(sim, "clock") and hasattr(sim.clock, "elapsed_time"):
            return sim.clock.elapsed_time
        return time.time()

    def _wait_ticks(self, target_ticks: int, check_target: bool = True) -> None:
        """Wait for the specified number of simulation ticks."""
        sim = getattr(self.simulation_runner, "simulator", None)
        clock = getattr(sim, "clock", None) if sim else None

        if clock and hasattr(clock, "tick") and getattr(clock, "running", False):
            start_tick = clock.tick
            while (clock.tick - start_tick) < target_ticks:
                if check_target and self._target_reached():
                    break
                time.sleep(0.005)
        else:
            duration = target_ticks * self.tick_rate
            start_time = time.time()
            while (time.time() - start_time) < duration:
                if check_target and self._target_reached():
                    break
                time.sleep(0.005)

    # ==================================================
    # Main Campaign Execution
    # ==================================================

    def run(self) -> None:
        """
        Execute the realistic industrial campaign:
          1. Reset DatasetManager to clear warmup messages
          2. Normal Baseline Period
          3. Sequential Attack Cycles with Cooldowns
          4. Final Normal Baseline (to reach exact target size)
        """
        print()
        print("=" * 72)
        print("🚀 PHASE 3 REALISTIC INDUSTRIAL DATASET CAMPAIGN")
        print("=" * 72)
        print(f"Attack Classes       : {self.total_attacks}")
        print(f"Target Records       : {self.target_dataset_size}")
        print(f"Baseline Ticks       : {self.baseline_ticks} ({self.baseline_duration:.2f} s)")
        print(f"Attack Ticks         : {self.attack_ticks} ({self.attack_duration:.2f} s)")
        print(f"Cooldown Ticks       : {self.cooldown_ticks} ({self.cooldown_duration:.2f} s)")
        print("=" * 72)
        print()

        # Reset dataset manager so any warmup records before campaign start are cleared
        if hasattr(self.dataset_manager, "reset"):
            self.dataset_manager.reset()

        # Phase 1: Normal Baseline
        if not self._target_reached():
            self._run_baseline_phase(self.baseline_ticks)

        # Phase 2: Attack Cycles
        cycle = 0
        while not self._target_reached():
            cycle += 1
            print(f"\n--- Starting Campaign Cycle {cycle} ---")
            for attack in self.attacks:
                if self._target_reached():
                    break

                self._run_attack_period(attack, self.attack_ticks)

                if self._target_reached():
                    break

                self._run_cooldown_phase(self.cooldown_ticks)

            # After cycle 1, break to final baseline to reach exact target size
            if not self._target_reached():
                break

        # Phase 3: Final Baseline to reach exact target size
        if not self._target_reached():
            self._run_final_baseline()

        self._print_final_summary()

    # ==================================================
    # Baseline Phase
    # ==================================================

    def _run_baseline_phase(
        self,
        ticks: int,
        label: str = "NORMAL BASELINE",
    ) -> None:
        """Collect normal baseline traffic for the specified simulation ticks."""
        print(f"\n🟢 [{label}] Collecting normal background telemetry (ticks={ticks})...")
        self._wait_ticks(ticks, check_target=True)
        print(
            f"✅ [{label}] Completed | Records: {self._records()}/{self.target_dataset_size} "
            f"({self._dataset_percentage():.1f}%)"
        )

    # ==================================================
    # Final Baseline Phase
    # ==================================================

    def _run_final_baseline(self) -> None:
        """Collect remaining normal baseline traffic until exact target size is reached."""
        print(f"\n🟢 [FINAL NORMAL BASELINE] Collecting remaining normal telemetry...")
        while not self._target_reached():
            time.sleep(0.005)
        print(
            f"✅ [FINAL NORMAL BASELINE] Completed | Records: {self._records()}/{self.target_dataset_size} "
            f"({self._dataset_percentage():.1f}%)"
        )

    # ==================================================
    # Attack Period
    # ==================================================

    def _run_attack_period(
        self,
        attack,
        ticks: int,
    ) -> None:
        """Execute one attack for the configured simulation ticks."""
        class_name = attack.attack_name
        self.total_attack_runs += 1

        print(f"\n🚨 [ATTACK] {class_name} started (ticks={ticks})...")

        # Reset attack object to READY if needed
        if hasattr(attack, "reset") and getattr(attack, "is_running", False) is False:
            attack.reset()

        # Start via REAL AttackManager
        self.attack_manager.start_attack(attack.attack_id)
        time.sleep(0.01)  # Brief pause for MQTT start event propagation

        # Wait for configured attack ticks
        self._wait_ticks(ticks, check_target=True)

        # Stop via REAL AttackManager
        if attack.is_running:
            self.attack_manager.stop_attack(attack.attack_id)
            time.sleep(0.01)  # Brief pause for MQTT stop event propagation

        print(
            f"📦 [ATTACK] {class_name} completed | "
            f"Class Records: {self._attack_records(class_name)} | "
            f"Total: {self._records()}/{self.target_dataset_size} "
            f"({self._dataset_percentage():.1f}%)"
        )

    # ==================================================
    # Cooldown Phase
    # ==================================================

    def _run_cooldown_phase(
        self,
        ticks: int,
    ) -> None:
        """Run normal cooldown traffic between attacks."""
        self._wait_ticks(ticks, check_target=True)

    # ==================================================
    # Final Summary
    # ==================================================

    def _print_final_summary(self) -> None:
        """Display final dataset generation statistics and observed distribution."""
        distribution = self.dataset_manager.get_distribution()

        total = distribution["total"]
        normal = distribution["normal"]
        attack = distribution["attack"]
        normal_pct = (normal / total * 100.0) if total > 0 else 0.0
        attack_pct = (attack / total * 100.0) if total > 0 else 0.0

        print()
        print("=" * 72)
        print("🎉 DATASET GENERATION CAMPAIGN COMPLETED")
        print("=" * 72)
        print(f"Total Records Generated : {total} / {self.target_dataset_size}")
        print(f"Normal Records          : {normal} ({normal_pct:.2f}%)")
        print(f"Attack Records          : {attack} ({attack_pct:.2f}%)")
        print(f"Total Attack Runs       : {self.total_attack_runs}")
        print(f"Quota Rejections        : {distribution.get('quota_rejected', 0)}")
        print()
        print("📊 OBSERVED CLASS DISTRIBUTION")
        print("-" * 72)
        print(f"{'Class':35}{'Records':>10}{'Share %':>12}")
        print("-" * 72)
        print(f"{NORMAL_CLASS:35}{normal:>10}{normal_pct:>11.2f}%")

        for attack_name in ATTACK_CLASSES:
            count = distribution["attacks"].get(attack_name, 0)
            share_pct = (count / total * 100.0) if total > 0 else 0.0
            print(f"{attack_name:35}{count:>10}{share_pct:>11.2f}%")

        print("-" * 72)
        print("=" * 72)