"""
operational_state.py

Defines the common operational lifecycle states for all
industrial assets in LightX-IDS.
"""

from enum import Enum


class OperationalState(Enum):
    """
    Common lifecycle states shared by factories,
    production lines, machines, PLCs, and sensors.
    """

    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    MAINTENANCE = "MAINTENANCE"
    FAULT = "FAULT"
    EMERGENCY_STOP = "EMERGENCY_STOP"