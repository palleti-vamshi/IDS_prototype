"""
sensor_state.py

Shared sensor attack state.
"""


class SensorState:

    spoofing = False

    spoof_value = None

    freeze = False

    drift = 0.0

    noise = 0.0

    false_data = False

    @classmethod
    def reset(cls):

        cls.spoofing = False

        cls.spoof_value = None

        cls.freeze = False

        cls.drift = 0.0

        cls.noise = 0.0

        cls.false_data = False