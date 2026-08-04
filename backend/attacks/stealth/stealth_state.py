"""
stealth_state.py

Shared stealth attack state.
"""


class StealthState:
    """
    Shared stealth attack state.
    """

    intermittent = False

    attack_probability = 0.0

    slow_drift = False

    drift_rate = 0.0

    @classmethod
    def reset(cls):

        cls.intermittent = False

        cls.attack_probability = 0.0

        cls.slow_drift = False

        cls.drift_rate = 0.0