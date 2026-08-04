"""
process_state.py

Shared process attack state.
"""


class ProcessState:
    """
    Shared process attack state.
    """

    # ==========================================
    # Motor Overload
    # ==========================================

    motor_overload = False

    overload_factor = 1.5

    # ==========================================
    # Valve Stuck
    # ==========================================

    valve_stuck = False

    # ==========================================
    # Reset
    # ==========================================

    @classmethod
    def reset(cls):

        cls.motor_overload = False

        cls.overload_factor = 1.5

        cls.valve_stuck = False