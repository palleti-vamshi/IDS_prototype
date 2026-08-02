"""
tank.py
"""

from .base_machine import BaseMachine


class Tank(BaseMachine):

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

        self.capacity = 1000.0
        self.current_level = 0.0