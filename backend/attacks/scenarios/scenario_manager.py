"""
scenario_manager.py

Manages attack scenarios for the
LightX-IDS Industrial Digital Twin.
"""

from __future__ import annotations

from backend.core.logger import setup_logger


class ScenarioManager:
    """
    Registers, loads and manages
    attack scenarios.
    """

    def __init__(self) -> None:

        self.logger = setup_logger(
            "ScenarioManager"
        )

        # ==========================================
        # Registered Scenarios
        # ==========================================

        self.scenarios = {}

        # ==========================================
        # Active Scenario
        # ==========================================

        self.active_scenario = None

    # ==========================================
    # Registration
    # ==========================================

    def register(
        self,
        scenario,
    ) -> None:
        """
        Register a new scenario.
        """

        self.scenarios[
            scenario.scenario_name
        ] = scenario

        self.logger.info(
            "Registered scenario: %s",
            scenario.scenario_name,
        )

    # ==========================================
    # Load
    # ==========================================

    def load(
        self,
        scenario_name: str,
    ) -> list:
        """
        Load a scenario and return
        all scheduled attack events.
        """

        scenario = self.scenarios.get(
            scenario_name
        )

        if scenario is None:

            raise ValueError(
                f"Scenario '{scenario_name}' not found."
            )

        scenario.build()

        self.active_scenario = scenario

        self.logger.info(
            "Loaded scenario: %s",
            scenario_name,
        )

        return scenario.get_events()

    # ==========================================
    # Remove
    # ==========================================

    def remove(
        self,
        scenario_name: str,
    ) -> None:
        """
        Remove a registered scenario.
        """

        self.scenarios.pop(
            scenario_name,
            None,
        )

    # ==========================================
    # Clear
    # ==========================================

    def clear(self) -> None:
        """
        Clear active scenario.
        """

        self.active_scenario = None

    # ==========================================
    # Access
    # ==========================================

    def get_active(self):

        return self.active_scenario

    def get_scenario(
        self,
        scenario_name: str,
    ):

        return self.scenarios.get(
            scenario_name
        )

    @property
    def total_scenarios(self) -> int:

        return len(
            self.scenarios
        )

    # ==========================================
    # Status
    # ==========================================

    def get_status(self) -> dict:

        return {

            "registered_scenarios":
                self.total_scenarios,

            "active_scenario":
                (
                    self.active_scenario.scenario_name
                    if self.active_scenario
                    else None
                ),

            "available_scenarios":
                list(
                    self.scenarios.keys()
                ),
        }

    # ==========================================

    def __str__(self) -> str:

        return (
            f"ScenarioManager("
            f"{self.total_scenarios} scenarios)"
        )