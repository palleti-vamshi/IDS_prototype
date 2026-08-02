"""
motor.py

Industrial Motor implementation.
"""

from __future__ import annotations

from .base_machine import BaseMachine


class Motor(BaseMachine):
    """
    Industrial electric motor.

    The motor owns its physical operating variables.
    Sensors attached through the SensorRegistry observe
    these variables.
    """

    def __init__(
        self,
        machine_code: str,
        name: str = "Motor",
        description: str = "Industrial Electric Motor",
    ) -> None:

        super().__init__(
            machine_code=machine_code,
            name=name,
            description=description,
        )

        # ==========================================
        # Operating Variables
        # ==========================================

        self.rpm = 0.0
        self.current = 0.0
        self.temperature = 25.0
        self.vibration = 0.10
        self.power = 0.0
        self.load = 0.0
        self.efficiency = 100.0

    def get_operating_state(self) -> dict:
        """
        Return current operating variables.
        """

        return {
            "rpm": self.rpm,
            "current": self.current,
            "temperature": self.temperature,
            "vibration": self.vibration,
            "power": self.power,
            "load": self.load,
            "efficiency": self.efficiency,
        }