"""
Machine operational states.
"""

from enum import Enum


class MachineState(Enum):
    """Represents the operational state of an industrial machine."""

    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    MAINTENANCE = "MAINTENANCE"
    FAULT = "FAULT"