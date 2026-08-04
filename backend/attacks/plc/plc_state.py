"""
plc_state.py

Shared PLC attack state.
"""


class PLCState:
    """
    Shared PLC state used by all PLC attacks.
    """

    # ==========================================
    # Command Injection
    # ==========================================

    command_injection = False

    injected_command = None

    # ==========================================
    # Unauthorized Command
    # ==========================================

    unauthorized_command = False

    # ==========================================
    # Setpoint Manipulation
    # ==========================================

    manipulated_setpoint = None

    # ==========================================
    # Reset
    # ==========================================

    @classmethod
    def reset(cls):

        cls.command_injection = False

        cls.injected_command = None

        cls.unauthorized_command = False

        cls.manipulated_setpoint = None