"""
constraints.py

Industrial operating constraints for the
LightX-IDS Digital Twin.
"""

from __future__ import annotations


class PhysicsConstraints:
    """
    Centralized industrial operating limits.
    """

    # ==================================================
    # Motor
    # ==================================================

    MOTOR_MAX_RPM = 2000.0
    MOTOR_MAX_CURRENT = 30.0
    MOTOR_MAX_TEMP = 120.0
    MOTOR_MAX_LOAD = 100.0

    # ==================================================
    # Pump
    # ==================================================

    PUMP_MAX_FLOW = 150.0
    PUMP_MAX_PRESSURE = 250.0
    PUMP_MAX_TEMP = 110.0

    # ==================================================
    # Valve
    # ==================================================

    VALVE_MIN_POSITION = 0.0
    VALVE_MAX_POSITION = 100.0

    # ==================================================
    # Tank
    # ==================================================

    TANK_MIN_LEVEL = 0.0
    TANK_MAX_LEVEL_PERCENT = 100.0
    TANK_MAX_TEMP = 90.0

    # ==================================================
    # Conveyor
    # ==================================================

    CONVEYOR_MAX_SPEED = 5.0

    # ==================================================
    # Compressor
    # ==================================================

    COMPRESSOR_MAX_PRESSURE = 280.0
    COMPRESSOR_MAX_FLOW = 200.0

    # ==================================================
    # Environment
    # ==================================================

    AMBIENT_TEMPERATURE = 25.0

    # ==================================================
    # Safety
    # ==================================================

    HEALTH_CRITICAL = 15.0