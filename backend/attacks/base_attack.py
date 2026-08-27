"""
base_attack.py

Abstract base class for all industrial cyber attacks.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from backend.core.logger import setup_logger

from backend.attacks.attack_state import AttackState
from backend.attacks.attack_type import AttackType
from backend.attacks.attack_target import AttackTarget
from backend.attacks.event_publisher import AttackEventPublisher


class BaseAttack(ABC):
    """
    Base class for every cyber attack in LightX-IDS.

    Every attack targets one industrial layer:

    • MACHINE
    • SENSOR
    • COMMUNICATION
    • PLC
    • PROCESS

    The AttackManager calls update() once every
    simulation tick.
    """

    def __init__(
        self,
        attack_id: str,
        attack_name: str,
        attack_type: AttackType,
        attack_target: AttackTarget,
        duration: float = 30.0,
    ) -> None:

        self.attack_id = attack_id

        self.attack_name = attack_name

        self.attack_type = attack_type

        self.attack_target = attack_target

        self.duration = duration

        self.elapsed_time = 0.0

        self.state = AttackState.CREATED

        self.targets: list[Any] = []

        self.enabled = True

        self.logger = setup_logger(
            attack_name
        )

        # ==========================================
        # Unique MQTT Event Publisher
        # ==========================================
        #
        # Every attack receives a unique MQTT
        # client ID.
        #
        # This is important because multiple attack
        # objects can exist simultaneously.
        #
        # Example:
        #
        # attack_event_DOS_001
        # attack_event_REPLAY_001
        # attack_event_SPOOF_001
        #
        # This prevents MQTT client-ID collisions.
        #

        self.event_publisher = AttackEventPublisher(
            client_id=(
                f"attack_event_{self.attack_id}"
            )
        )

    # ==================================================
    # Target Management
    # ==================================================

    def add_target(
        self,
        target: Any,
    ) -> None:
        """
        Register a target for this attack.
        """

        if target not in self.targets:

            self.targets.append(
                target
            )

        if self.state == AttackState.CREATED:

            self.state = AttackState.READY

    def remove_target(
        self,
        target: Any,
    ) -> None:

        if target in self.targets:

            self.targets.remove(
                target
            )

    def clear_targets(
        self,
    ) -> None:

        self.targets.clear()

    # ==================================================
    # Lifecycle
    # ==================================================

    def start(
        self,
    ) -> None:
        """
        Start attack.
        """

        if not self.enabled:

            return

        # ------------------------------------------
        # Prevent duplicate starts
        # ------------------------------------------

        if self.state == AttackState.RUNNING:

            return

        # ------------------------------------------
        # Reset runtime state
        # ------------------------------------------

        self.elapsed_time = 0.0

        self.state = AttackState.RUNNING

        # ------------------------------------------
        # Console / Logger
        # ------------------------------------------

        self._print_start_banner()

        self.logger.info(
            "%s started.",
            self.attack_name,
        )

        # ------------------------------------------
        # Publish START event
        # ------------------------------------------

        self.event_publisher.publish_start(
            self.get_status()
        )

    def stop(
        self,
    ) -> None:
        """
        Stop attack.
        """

        # ------------------------------------------
        # Ignore repeated stop calls
        # ------------------------------------------

        if self.state == AttackState.STOPPED:

            return

        self.state = AttackState.STOPPED

        # ------------------------------------------
        # Console / Logger
        # ------------------------------------------

        self._print_stop_banner()

        self.logger.info(
            "%s stopped.",
            self.attack_name,
        )

        # ------------------------------------------
        # Publish STOP event
        # ------------------------------------------

        self.event_publisher.publish_stop(
            self.get_status()
        )

    def pause(
        self,
    ) -> None:

        if self.state == AttackState.RUNNING:

            self.state = AttackState.PAUSED

    def resume(
        self,
    ) -> None:

        if self.state == AttackState.PAUSED:

            self.state = AttackState.RUNNING

    def reset(
        self,
    ) -> None:
        """
        Reset attack to READY state.
        """

        self.elapsed_time = 0.0

        self.state = AttackState.READY

    # ==================================================
    # Console Output
    # ==================================================

    def _print_start_banner(
        self,
    ) -> None:

        print("\033[91m")

        print("=" * 72)

        print(
            "🚨  LIGHTX-IDS ATTACK STARTED"
        )

        print("=" * 72)

        print(
            f"Attack ID      : {self.attack_id}"
        )

        print(
            f"Attack Name    : {self.attack_name}"
        )

        print(
            f"Attack Type    : "
            f"{self.attack_type.value}"
        )

        print(
            f"Target Layer   : "
            f"{self.attack_target.value}"
        )

        print(
            f"Duration       : "
            f"{self.duration:.0f} sec"
        )

        print("=" * 72)

        print("\033[0m")

    def _print_stop_banner(
        self,
    ) -> None:

        print("\033[92m")

        print("=" * 72)

        print(
            "✅  LIGHTX-IDS ATTACK COMPLETED"
        )

        print("=" * 72)

        print(
            f"Attack ID      : {self.attack_id}"
        )

        print(
            f"Attack Name    : {self.attack_name}"
        )

        print(
            f"Elapsed Time   : "
            f"{self.elapsed_time:.1f} sec"
        )

        print("=" * 72)

        print("\033[0m")

    # ==================================================
    # Runtime
    # ==================================================

    def update(
        self,
        dt: float,
    ) -> None:
        """
        Called every simulation tick.
        """

        if self.state != AttackState.RUNNING:

            return

        self.elapsed_time += dt

        print(
            f"{self.attack_name}: "
            f"{self.elapsed_time:.1f}/"
            f"{self.duration:.1f}"
        )

        # ------------------------------------------
        # Apply attack behaviour
        # ------------------------------------------

        self.apply(dt)

        # ------------------------------------------
        # Check completion
        # ------------------------------------------

        if self.elapsed_time >= self.duration:

            self.state = AttackState.COMPLETED

            self.logger.info(
                "%s completed.",
                self.attack_name,
            )

    # ==================================================
    # Attack Logic
    # ==================================================

    @abstractmethod
    def apply(
        self,
        dt: float,
    ) -> None:
        """
        Apply attack behaviour.
        """

        ...

    # ==================================================
    # Status
    # ==================================================

    @property
    def is_running(
        self,
    ) -> bool:

        return (
            self.state == AttackState.RUNNING
        )

    @property
    def is_finished(
        self,
    ) -> bool:

        return (
            self.state == AttackState.COMPLETED
        )

    # ==================================================
    # Status Information
    # ==================================================

    def get_status(
        self,
    ) -> dict:

        return {

            "attack_id":
                self.attack_id,

            "attack_name":
                self.attack_name,

            "type":
                self.attack_type.value,

            "target_layer":
                self.attack_target.value,

            "state":
                self.state.value,

            "duration":
                self.duration,

            "elapsed_time":
                round(
                    self.elapsed_time,
                    2,
                ),

            "targets":
                len(
                    self.targets
                ),

            "enabled":
                self.enabled,
        }

    # ==================================================
    # Cleanup
    # ==================================================

    def close(
        self,
    ) -> None:
        """
        Release resources owned by the attack.

        This is intentionally separate from stop().
        stop() represents the attack lifecycle, while
        close() releases the MQTT publisher.
        """

        self.event_publisher.disconnect()

    # ==================================================
    # String
    # ==================================================

    def __str__(
        self,
    ) -> str:

        return (
            f"{self.attack_id} | "
            f"{self.attack_name} | "
            f"{self.attack_type.value} | "
            f"{self.attack_target.value} | "
            f"{self.state.value}"
        )