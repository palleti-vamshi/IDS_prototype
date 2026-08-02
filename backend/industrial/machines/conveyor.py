"""
conveyor.py

Industrial Conveyor implementation.
"""

from __future__ import annotations

from .base_machine import BaseMachine


class Conveyor(BaseMachine):
    """
    Industrial Conveyor.

    Owns all conveyor operating variables.
    Sensors observe these variables.
    """

    def __init__(
        self,
        machine_code: str,
        name: str = "Conveyor",
        description: str = "Industrial Conveyor Belt",
    ) -> None:

        super().__init__(
            machine_code=machine_code,
            name=name,
            description=description,
        )

        # ==========================================
        # Operating Variables
        # ==========================================

        self.belt_speed = 0.0
        self.load_weight = 0.0
        self.current = 0.0
        self.temperature = 25.0
        self.rpm = 0.0
        self.proximity = 500.0
        self.power = 0.0
        self.load = 0.0
        self.efficiency = 100.0

    def get_operating_state(self) -> dict:
        """
        Return current operating variables.
        """

        return {
            "belt_speed": self.belt_speed,
            "load_weight": self.load_weight,
            "current": self.current,
            "temperature": self.temperature,
            "rpm": self.rpm,
            "proximity": self.proximity,
            "power": self.power,
            "load": self.load,
            "efficiency": self.efficiency,
        }