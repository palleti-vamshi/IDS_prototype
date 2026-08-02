"""
base_behavior.py

Abstract base class for all industrial machine behaviors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from backend.industrial.behavior.state_models import BehaviorState
from backend.industrial.common import OperationalState


class BaseBehavior(ABC):
    """
    Base class for all machine behavior models.

    A behavior model controls how a machine's operating
    variables evolve over time.
    """

    def __init__(self, machine) -> None:

        self.machine = machine

        self.state = BehaviorState.STOPPED

        self.time_in_state = 0.0

    # ==================================================
    # State Management
    # ==================================================

    def set_state(
        self,
        state: BehaviorState,
    ) -> None:
        """
        Change behavior state and synchronize
        the machine operational state.
        """

        self.state = state
        self.time_in_state = 0.0

        if state == BehaviorState.STOPPED:

            self.machine.state = OperationalState.STOPPED

        elif state == BehaviorState.MAINTENANCE:

            self.machine.state = OperationalState.MAINTENANCE

        elif state == BehaviorState.FAULT:

            self.machine.state = OperationalState.FAULT

        else:

            self.machine.state = OperationalState.RUNNING

    # ==================================================
    # Timing
    # ==================================================

    def update_time(
        self,
        dt: float,
    ) -> None:
        """
        Update elapsed simulation time.
        """

        self.time_in_state += dt

    # ==================================================
    # Utility
    # ==================================================

    def approach(
        self,
        current: float,
        target: float,
        rate: float,
        dt: float,
    ) -> float:
        """
        Smoothly move a value toward a target.
        """

        if current < target:

            current = min(
                current + rate * dt,
                target,
            )

        elif current > target:

            current = max(
                current - rate * dt,
                target,
            )

        return round(current, 2)

    # ==================================================
    # Behavior
    # ==================================================

    @abstractmethod
    def update(
        self,
        dt: float,
    ) -> None:
        """
        Update machine behavior.
        """
        raise NotImplementedError

    # ==================================================
    # Information
    # ==================================================

    def get_status(self) -> dict:
        """
        Return behavior information.
        """

        return {
            "machine": self.machine.machine_code,
            "behavior_state": self.state.value,
            "machine_state": self.machine.state.value,
            "time_in_state": round(
                self.time_in_state,
                2,
            ),
        }

    def __str__(self) -> str:

        return (
            f"{self.machine.machine_code}"
            f" [{self.state.value}]"
        )