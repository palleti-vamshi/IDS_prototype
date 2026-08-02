"""
tank.py

Industrial Storage Tank implementation.
"""

from __future__ import annotations

from .base_machine import BaseMachine


class Tank(BaseMachine):
    """
    Industrial Storage Tank.

    Owns all tank operating variables.
    Sensors observe these variables.
    """

    def __init__(
        self,
        machine_code: str,
        name: str = "Tank",
        description: str = "Industrial Storage Tank",
    ) -> None:

        super().__init__(
            machine_code=machine_code,
            name=name,
            description=description,
        )

        # ==========================================
        # Operating Variables
        # ==========================================

        self.capacity = 1000.0          # Liters
        self.current_level = 500.0      # Liters
        self.level_percentage = 50.0    # %
        self.temperature = 25.0         # °C
        self.pressure = 101.3           # kPa
        self.inflow_rate = 0.0          # L/min
        self.outflow_rate = 0.0         # L/min
        self.load = 0.0

    def get_operating_state(self) -> dict:
        """
        Return current operating variables.
        """

        return {
            "capacity": self.capacity,
            "current_level": self.current_level,
            "level_percentage": self.level_percentage,
            "temperature": self.temperature,
            "pressure": self.pressure,
            "inflow_rate": self.inflow_rate,
            "outflow_rate": self.outflow_rate,
            "load": self.load,
        }