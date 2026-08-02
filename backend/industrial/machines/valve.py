"""
valve.py
"""

from .base_machine import BaseMachine


class Valve(BaseMachine):

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

        self.position = 0.0
        self.is_open = False