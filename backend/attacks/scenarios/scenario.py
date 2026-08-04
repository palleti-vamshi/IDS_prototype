"""
scenario.py

Base attack scenario.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AttackScenario(ABC):
    """
    Base class for every attack scenario.
    """

    def __init__(
        self,
        scenario_name: str,
    ) -> None:

        self.scenario_name = scenario_name

        self.events = []

    # ==========================================
    # Build Scenario
    # ==========================================

    @abstractmethod
    def build(self) -> None:
        """
        Populate attack events.
        """
        raise NotImplementedError

    # ==========================================
    # Add Event
    # ==========================================

    def add_attack(
        self,
        attack,
        start_time: float,
    ) -> None:

        self.events.append(
            {
                "attack": attack,
                "start_time": start_time,
            }
        )

    # ==========================================
    # Events
    # ==========================================

    def get_events(self):

        return sorted(
            self.events,
            key=lambda event: event["start_time"],
        )

    # ==========================================
    # Information
    # ==========================================

    def get_status(self) -> dict:

        return {

            "scenario": self.scenario_name,

            "attacks": len(self.events),
        }