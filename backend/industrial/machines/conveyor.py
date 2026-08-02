"""
conveyor.py
"""

from .base_machine import BaseMachine


class Conveyor(BaseMachine):

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

        self.belt_speed = 0.0
        self.load_weight = 0.0