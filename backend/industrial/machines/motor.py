"""
motor.py

Motor implementation.
"""

from .base_machine import BaseMachine


class Motor(BaseMachine):

    def __init__(
        self,
        machine_code: str,
        name: str,
        description: str = "",
    ) -> None:

        super().__init__(
            machine_code=machine_code,
            name=name,
            description=description,
        )

        # Motor Telemetry
        self.rpm = 0
        self.current = 0.0
        self.temperature = 25.0
        self.power = 0.0