"""
attack_scheduler.py

Schedules and controls cyber attack execution.

Responsibilities:
    • Manual attack triggering
    • Timed attack scheduling
    • Sequential attack scheduling
    • Random attack scheduling
    • Phase 3 campaign control

Important:
    AttackScheduler controls WHEN attacks start.

    AttackManager controls the runtime update of attacks.

    This separation prevents two independent controllers from
    modifying attack execution simultaneously.
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
        • Campaign

    The scheduler does NOT execute attack.update().
    AttackManager owns attack execution.
    """

    def __init__(self) -> None:

        self.logger = setup_logger(
            "AttackScheduler"
        )

        # ==================================================
        # Timed Scheduling
        # ==================================================

        self.scheduled_attacks = []

        # ==================================================
        # Random Scheduling
        # ==================================================

        self.random_attacks = []

        # ==================================================
        # Sequential Scheduling
        # ==================================================

        self.sequential_attacks = []

        self.current_index = 0

        # ==================================================
        # General Timing
        # ==================================================

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
        Immediately start an attack.

        Manual triggering is intentionally kept here because
        this is an explicit scheduler request.
        """

        if attack is None:

            return

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
        Schedule an attack for a specific simulation time.
        """

        if attack is None:

            return

        self.scheduled_attacks.append(
            (
                start_time,
                attack,
            )
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
        """
        Register an attack for random execution.
        """

        if attack is None:

            return

        if attack not in self.random_attacks:

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
        """
        Register attacks for sequential execution.
        """

        self.sequential_attacks = list(
            attacks
        )

        self.current_index = 0

    # ==================================================
    # Campaign
    # ==================================================

    def start_campaign(
        self,
        attacks: list,
    ) -> None:
        """
        Start a Phase 3 attack campaign.

        The campaign alternates between:

            NORMAL
                ↓
            ATTACK
                ↓
            NORMAL
                ↓
            ATTACK
                ↓
            ...

        Attack execution itself is handled by
        AttackManager.update().
        """

        if not attacks:

            self.logger.warning(
                "Cannot start campaign: "
                "attack list is empty."
            )

            return

        # Stop any previous campaign state.

        self.attack_queue = list(
            attacks
        )

        self.total_attacks = len(
            self.attack_queue
        )

        self.completed_attacks = 0

        self.phase = "NORMAL"

        self.phase_time = 0.0

        self.current_attack = None

        self.campaign_mode = True

        self.logger.info(
            "Campaign started with %d attacks.",
            self.total_attacks,
        )

        print()
        print("=" * 72)
        print(
            "🚀 LIGHTX-IDS ATTACK CAMPAIGN STARTED"
        )
        print("=" * 72)

        print(
            f"Total Attacks : "
            f"{self.total_attacks}"
        )

        print(
            f"Normal Phase  : "
            f"{self.normal_duration:.1f} sec"
        )

        print("=" * 72)
        print()

    # ==================================================
    # Campaign Finished
    # ==================================================

    def campaign_finished(
        self,
    ) -> bool:
        """
        Return True when every campaign attack has
        completed.
        """

        return (
            self.total_attacks > 0
            and self.completed_attacks
            >= self.total_attacks
        )

    # ==================================================
    # Update
    # ==================================================

    def update(
        self,
        dt: float,
    ) -> None:
        """
        Update scheduler state.

        IMPORTANT:
            This method does NOT call attack.update().

        AttackManager owns attack execution.
        """

        self.elapsed_time += dt

        # ==================================================
        # Timed Attacks
        # ==================================================

        pending = []

        for start_time, attack in (
            self.scheduled_attacks
        ):

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
                    (
                        start_time,
                        attack,
                    )
                )

        self.scheduled_attacks = pending

        # ==================================================
        # Sequential Attacks
        # ==================================================

        if (
            self.current_index
            < len(
                self.sequential_attacks
            )
        ):

            attack = (
                self.sequential_attacks[
                    self.current_index
                ]
            )

            if attack.state.name == "READY":

                attack.start()

            elif attack.is_finished:

                self.current_index += 1

        # ==================================================
        # Campaign Mode
        # ==================================================

        if not self.campaign_mode:

            return

        self.phase_time += dt

        # ==================================================
        # NORMAL PHASE
        # ==================================================

        if self.phase == "NORMAL":

            if (
                self.phase_time
                < self.normal_duration
            ):

                return

            self.phase = "ATTACK"

            self.phase_time = 0.0

            if self.attack_queue:

                self.current_attack = (
                    self.attack_queue.pop(0)
                )

                print()
                print("=" * 72)

                print(
                    f"🚀 Starting Attack "
                    f"{self.completed_attacks + 1}/"
                    f"{self.total_attacks}: "
                    f"{self.current_attack.attack_name}"
                )

                print("=" * 72)
                print()

                # Scheduler starts the attack.
                #
                # AttackManager.update() will handle
                # its subsequent runtime updates.

                self.current_attack.start()

            else:

                self._finish_campaign()

            return

        # ==================================================
        # ATTACK PHASE
        # ==================================================

        if self.phase == "ATTACK":

            if self.current_attack is None:

                self.phase = "NORMAL"

                self.phase_time = 0.0

                return

            # ==================================================
            # Detect Finished Attack
            # ==================================================

            if (
                self.current_attack.is_finished
                or self.current_attack.state.name
                == "STOPPED"
            ):

                finished_attack = (
                    self.current_attack
                )

                print()
                print(
                    f"✅ Attack completed: "
                    f"{finished_attack.attack_name}"
                )

                print(
                    f"   State: "
                    f"{finished_attack.state.value}"
                )

                print(
                    f"   Duration: "
                    f"{finished_attack.elapsed_time:.1f}s"
                )

                # ==================================================
                # Ensure Completed Attack Is Stopped
                # ==================================================

                if (
                    finished_attack.state.name
                    != "STOPPED"
                ):

                    finished_attack.stop()

                # ==================================================
                # Campaign Counter
                # ==================================================

                self.completed_attacks += 1

                print()
                print(
                    f"📊 Campaign Progress: "
                    f"{self.completed_attacks}/"
                    f"{self.total_attacks}"
                )
                print()

                self.current_attack = None

                # ==================================================
                # Campaign Finished?
                # ==================================================

                if self.campaign_finished():

                    self._finish_campaign()

                else:

                    self.phase = "NORMAL"

                    self.phase_time = 0.0

    # ==================================================
    # Campaign Completion
    # ==================================================

    def _finish_campaign(
        self,
    ) -> None:
        """
        Mark the current campaign as finished.
        """

        print()
        print("=" * 72)
        print(
            "🎉 ALL ATTACKS COMPLETED"
        )
        print("=" * 72)

        print(
            f"Completed: "
            f"{self.completed_attacks}/"
            f"{self.total_attacks}"
        )

        print("=" * 72)
        print()

        self.campaign_mode = False

        self.phase = "NORMAL"

        self.phase_time = 0.0

        self.current_attack = None

    # ==================================================
    # Random Attacks
    # ==================================================

    def update_random_attacks(
        self,
    ) -> None:
        """
        Randomly trigger one registered attack.
        """

        if not self.random_attacks:

            return

        if random.random() < 0.01:

            attack = random.choice(
                self.random_attacks
            )

            if attack.state.name == "READY":

                attack.start()

    # ==================================================
    # Reset
    # ==================================================

    def reset(
        self,
    ) -> None:
        """
        Reset scheduler state.
        """

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

    # ==================================================
    # Progress
    # ==================================================

    def print_progress(
        self,
    ) -> None:
        """
        Print campaign progress.
        """

        if not self.campaign_mode:

            return

        current = None

        if self.current_attack:

            current = (
                self.current_attack.attack_name
            )

        print(
            f"[Campaign] "
            f"{self.completed_attacks}/"
            f"{self.total_attacks} completed | "
            f"Phase: {self.phase} | "
            f"Phase Time: "
            f"{self.phase_time:.1f}s | "
            f"Current: {current}"
        )

    # ==================================================
    # Status
    # ==================================================

    def get_status(
        self,
    ) -> dict:
        """
        Return scheduler status.
        """

        return {

            "simulation_time":
                round(
                    self.elapsed_time,
                    2,
                ),

            "scheduled_attacks":
                len(
                    self.scheduled_attacks
                ),

            "random_attacks":
                len(
                    self.random_attacks
                ),

            "sequential_attacks":
                len(
                    self.sequential_attacks
                ),

            "campaign_mode":
                self.campaign_mode,

            "phase":
                self.phase,

            "phase_time":
                round(
                    self.phase_time,
                    2,
                ),

            "completed_attacks":
                self.completed_attacks,

            "total_attacks":
                self.total_attacks,

            "queued_attacks":
                len(
                    self.attack_queue
                ),

            "current_attack":
                (
                    self.current_attack.attack_name
                    if self.current_attack
                    else None
                ),

            "current_attack_state":
                (
                    self.current_attack.state.value
                    if self.current_attack
                    else None
                ),
        }

    # ==================================================
    # String
    # ==================================================

    def __str__(
        self,
    ) -> str:

        return (
            f"AttackScheduler("
            f"phase={self.phase}, "
            f"completed="
            f"{self.completed_attacks}/"
            f"{self.total_attacks})"
        )