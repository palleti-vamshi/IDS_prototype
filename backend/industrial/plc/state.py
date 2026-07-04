"""
PLC State Module

Purpose:
    Stores the latest industrial sensor values and PLC status.
"""


class PLCState:
    """Maintains the current state of the virtual factory."""

    def __init__(self):
        self.temperature = None
        self.pressure = None
        self.status = "UNKNOWN"

    def update_temperature(self, value: float) -> None:
        """Update the latest temperature reading."""
        self.temperature = value

    def update_pressure(self, value: float) -> None:
        """Update the latest pressure reading."""
        self.pressure = value

    def update_status(self, status: str) -> None:
        """Update the overall factory status."""
        self.status = status

    def get_state(self) -> dict:
        """Return the current PLC state."""
        return {
            "temperature": self.temperature,
            "pressure": self.pressure,
            "status": self.status,
        }