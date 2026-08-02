"""
pump.py

Industrial Pump implementation.
"""

from __future__ import annotations

from .base_machine import BaseMachine


class Pump(BaseMachine):
    """
    Industrial Pump.

    Owns all operating variables.
    Sensors observe these variables.
    """

    def __init__(
        self,
        machine_code: str,
        name: str = "Pump",
        description: str = "Industrial Cooling Pump",
    ) -> None:

        super().__init__(
            machine_code=machine_code,
            name=name,
            description=description,
        )

        # ==========================================
        # Operating Variables
        # ==========================================

        self.pressure = 101.3
        self.flow_rate = 0.0
        self.current = 0.0
        self.temperature = 25.0
        self.power = 0.0
        self.load = 0.0
        self.efficiency = 100.0

    def get_operating_state(self) -> dict:
        """
        Return current operating variables.
        """

        return {
            "pressure": self.pressure,
            "flow_rate": self.flow_rate,
            "current": self.current,
            "temperature": self.temperature,
            "power": self.power,
            "load": self.load,
            "efficiency": self.efficiency,
        }