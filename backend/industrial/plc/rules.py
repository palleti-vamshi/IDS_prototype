"""
PLC Rules Module

Purpose:
    Defines the industrial operating rules
    for the virtual factory.
"""


class PLCRules:
    """Evaluates industrial sensor readings."""

    MIN_TEMPERATURE = 27.0
    MAX_TEMPERATURE = 30.0

    MIN_PRESSURE = 100.5
    MAX_PRESSURE = 102.5

    @classmethod
    def evaluate(
        cls,
        temperature: float | None,
        pressure: float | None,
    ) -> str:
        """
        Evaluate the current factory state.
        """

        if temperature is None or pressure is None:
            return "UNKNOWN"

        if not (
            cls.MIN_TEMPERATURE <= temperature <= cls.MAX_TEMPERATURE
        ):
            return "WARNING"

        if not (
            cls.MIN_PRESSURE <= pressure <= cls.MAX_PRESSURE
        ):
            return "WARNING"

        return "NORMAL"