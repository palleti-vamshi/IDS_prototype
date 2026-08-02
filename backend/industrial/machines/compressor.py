"""
compressor.py

Industrial Air Compressor implementation.
"""

from __future__ import annotations

from .base_machine import BaseMachine


class Compressor(BaseMachine):
    """
    Industrial Air Compressor.

    Owns all compressor operating variables.
    Sensors observe these variables.
    """

    def __init__(
        self,
        machine_code: str,
        name: str = "Compressor",
        description: str = "Industrial Air Compressor",
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
        self.temperature = 25.0
        self.current = 0.0
        self.power = 0.0
        self.air_flow = 0.0
        self.load = 0.0
        self.efficiency = 100.0

    def get_operating_state(self) -> dict:
        """
        Return current operating variables.
        """

        return {
            "pressure": self.pressure,
            "temperature": self.temperature,
            "current": self.current,
            "power": self.power,
            "air_flow": self.air_flow,
            "load": self.load,
            "efficiency": self.efficiency,
        }