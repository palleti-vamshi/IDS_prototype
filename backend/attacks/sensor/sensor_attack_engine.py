"""
sensor_attack_engine.py

Central engine for realistic sensor attacks.
"""

from __future__ import annotations


class SensorAttackEngine:
    """
    Central manager for per-sensor attack state.

    Every industrial sensor owns its own attack
    profile instead of relying on global state.
    """

    def __init__(self) -> None:

        self.sensor_states = {}

    # ==================================================
    # Registration
    # ==================================================

    def register_sensor(
        self,
        sensor_code: str,
    ) -> None:

        if sensor_code not in self.sensor_states:

            self.sensor_states[sensor_code] = self._default_state()

    def unregister_sensor(
        self,
        sensor_code: str,
    ) -> None:

        self.sensor_states.pop(
            sensor_code,
            None,
        )

    # ==================================================
    # Default State
    # ==================================================

    def _default_state(
        self,
    ) -> dict:

        return {

            "spoof": False,

            "spoof_offset": 0.0,

            "drift": 0.0,

            "noise": 0.0,

            "freeze": False,

            "false_data": False,

            "last_value": None,

            "attack_name": None,

        }

    # ==================================================
    # Access
    # ==================================================

    def get_state(
        self,
        sensor_code: str,
    ) -> dict:

        if sensor_code not in self.sensor_states:

            self.register_sensor(
                sensor_code
            )

        return self.sensor_states[
            sensor_code
        ]

    # ==================================================
    # Update
    # ==================================================

    def update_state(
        self,
        sensor_code: str,
        **kwargs,
    ) -> None:

        state = self.get_state(
            sensor_code
        )

        state.update(
            kwargs
        )

    # ==================================================
    # Last Value
    # ==================================================

    def set_last_value(
        self,
        sensor_code: str,
        value: float,
    ) -> None:

        self.get_state(
            sensor_code
        )["last_value"] = value

    def get_last_value(
        self,
        sensor_code: str,
    ):

        return self.get_state(
            sensor_code
        )["last_value"]

    # ==================================================
    # Reset
    # ==================================================

    def reset_sensor(
        self,
        sensor_code: str,
    ) -> None:

        self.sensor_states[
            sensor_code
        ] = self._default_state()

    def reset_all(
        self,
    ) -> None:

        for sensor_code in list(
            self.sensor_states.keys()
        ):

            self.reset_sensor(
                sensor_code
            )

    # ==================================================
    # Information
    # ==================================================

    @property
    def total_registered(
        self,
    ) -> int:

        return len(
            self.sensor_states
        )

    def get_status(
        self,
    ) -> dict:

        return {

            "registered_sensors":
                self.total_registered,

            "sensor_states":
                self.sensor_states,
        }