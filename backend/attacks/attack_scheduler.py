"""
attack_scheduler.py

Schedules and controls cyber attack execution.
"""

from __future__ import annotations

import random

from backend.core.logger import setup_logger


class AttackScheduler:
    """
    Controls when attacks should start.

    Supports:
        • Manual
        • Timed
        • Random
        • Sequential
    """

    def __init__(self) -> None:

        self.logger = setup_logger(
            "AttackScheduler"
        )

        self.scheduled_attacks = []

        self.random_attacks = []

        self.sequential_attacks = []

        self.current_index = 0

        self.elapsed_time = 0.0

        # ==================================================
        # Campaign Mode
        # ==================================================

        self.campaign_mode = False

        self.attack_duration = 30.0

        self.normal_duration = 30.0

        self.phase = "NORMAL"

        self.phase_time = 0.0

        self.current_attack = None

        self.completed_attacks = 0

        self.total_attacks = 0

        self.attack_queue = []

    # ==================================================
    # Manual
    # ==================================================

    def trigger(
        self,
        attack,
    ) -> None:
        """
        Start an attack immediately.
        """

        if not attack.is_running:
            attack.start()

    # ==================================================
    # Timed Scheduling
    # ==================================================

    def schedule(
        self,
        attack,
        start_time: float,
    ) -> None:
        """
        Schedule an attack at a simulation time.
        """

        self.scheduled_attacks.append(
            (start_time, attack)
        )

        self.scheduled_attacks.sort(
            key=lambda item: item[0]
        )

    # ==================================================
    # Random Scheduling
    # ==================================================

    def register_random(
        self,
        attack,
    ) -> None:

        self.random_attacks.append(
            attack
        )

    # ==================================================
    # Sequential Scheduling
    # ==================================================

    def register_sequence(
        self,
        attacks: list,
    ) -> None:

        self.sequential_attacks = attacks

        self.current_index = 0


    # ==================================================
    # Campaign Mode
    # ==================================================

    def start_campaign(
        self,
        attacks: list,
    ) -> None:

        self.attack_queue = attacks.copy()

        self.total_attacks = len(attacks)

        self.completed_attacks = 0

        self.phase = "NORMAL"

        self.phase_time = 0.0

        self.current_attack = None

        self.campaign_mode = True

        self.logger.info(
            "Campaign started with %d attacks.",
            self.total_attacks,
        )


    def campaign_finished(
        self,
    ) -> bool:

        return (
            self.completed_attacks
            >= self.total_attacks
        )
    # ==================================================
    # Update
    # ==================================================

    def update(
        self,
        dt: float,
    ) -> None:

        self.elapsed_time += dt

        # ------------------------------------------
        # Timed Attacks
        # ------------------------------------------

        pending = []

        for start_time, attack in self.scheduled_attacks:

            if (
                self.elapsed_time >= start_time
                and not attack.is_running
            ):

                attack.start()

                self.logger.info(
                    "Timed attack started: %s",
                    attack.attack_name,
                )

            else:

                pending.append(
                    (start_time, attack)
                )

        self.scheduled_attacks = pending


        # ------------------------------------------
        # Sequential Attacks
        # ------------------------------------------

        if self.current_index < len(
            self.sequential_attacks
        ):

            attack = self.sequential_attacks[
                self.current_index
            ]

            if attack.state.name == "READY":

                attack.start()

            elif attack.is_finished:

                self.current_index += 1


        # ------------------------------------------
        # Campaign Mode
        # ------------------------------------------

        if self.campaign_mode:

            self.phase_time += dt

            # ==========================
            # NORMAL PHASE
            # ==========================

            if self.phase == "NORMAL":

                if (
                    self.phase_time
                    >= self.normal_duration
                ):

                    self.phase = "ATTACK"

                    self.phase_time = 0.0

                    if self.attack_queue:

                        self.current_attack = (
                            self.attack_queue.pop(0)
                        )

                        self.current_attack.start()

                        print(
                            f"\n🚀 Starting Attack "
                            f"{self.completed_attacks+1}/"
                            f"{self.total_attacks}: "
                            f"{self.current_attack.attack_name}\n"
                        )

            # ==========================
            # ATTACK PHASE
            # ==========================

            elif self.phase == "ATTACK":

                if (
                    self.current_attack
                    and self.current_attack.is_finished
                ):

                    self.current_attack.stop()

                    self.completed_attacks += 1

                    print(
                        f"✅ Completed "
                        f"{self.completed_attacks}/"
                        f"{self.total_attacks}\n"
                    )

                    self.current_attack = None

                    self.phase = "NORMAL"

                    self.phase_time = 0.0

                    if self.campaign_finished():

                        print()

                        print("=" * 70)

                        print("🎉 ALL ATTACKS COMPLETED")

                        print("=" * 70)

                        self.campaign_mode = False

        # ------------------------------------------
        # Random Attacks
        # ------------------------------------------

        if self.random_attacks:

            if random.random() < 0.01:

                attack = random.choice(
                    self.random_attacks
                )

                if (
                    attack.state.name == "READY"
                ):

                    attack.start()

    # ==================================================
    # Reset
    # ==================================================

    def reset(self) -> None:

        self.elapsed_time = 0.0

        self.current_index = 0

        self.phase = "NORMAL"

        self.phase_time = 0.0

        self.current_attack = None

        self.completed_attacks = 0

        self.total_attacks = 0

        self.attack_queue.clear()

        self.campaign_mode = False

        self.scheduled_attacks.clear()

    def print_progress(self) -> None:

        if not self.campaign_mode:

            return

        print(
            f"[Campaign] "
            f"{self.completed_attacks}/"
            f"{self.total_attacks} "
            f"completed | "
            f"Phase: {self.phase}"
        )

    # ==================================================
    # Status
    # ==================================================

    def get_status(self) -> dict:

        return {

            "simulation_time": round(
                self.elapsed_time,
                2,
            ),

            "scheduled_attacks": len(
                self.scheduled_attacks
            ),

            "random_attacks": len(
                self.random_attacks
            ),

            "sequential_attacks": len(
                self.sequential_attacks
            ),
        }