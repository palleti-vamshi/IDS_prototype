"""
compressor.py
"""

from .base_machine import BaseMachine


class Compressor(BaseMachine):

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

        self.pressure = 0.0
        self.temperature = 25.0