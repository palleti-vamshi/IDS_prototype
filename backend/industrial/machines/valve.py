"""
valve.py

Industrial Valve implementation.
"""

from __future__ import annotations

from .base_machine import BaseMachine


class Valve(BaseMachine):
    """
    Industrial Control Valve.

    Owns all valve operating variables.
    Sensors observe these variables.
    """

    def __init__(
        self,
        machine_code: str,
        name: str = "Valve",
        description: str = "Industrial Control Valve",
    ) -> None:

        super().__init__(
            machine_code=machine_code,
            name=name,
            description=description,
        )

        # ==========================================
        # Operating Variables
        # ==========================================

        self.position = 0.0          # %
        self.is_open = False
        self.pressure = 101.3        # kPa
        self.flow_rate = 0.0         # L/min
        self.temperature = 25.0      # °C

    def get_operating_state(self) -> dict:
        """
        Return current operating variables.
        """

        return {
            "position": self.position,
            "is_open": self.is_open,
            "pressure": self.pressure,
            "flow_rate": self.flow_rate,
            "temperature": self.temperature,
        }