"""
Factory operational states.

This module defines the lifecycle states of a digital twin factory.
"""

from enum import Enum


class FactoryState(Enum):
    """Represents the operational state of a factory."""

    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    MAINTENANCE = "MAINTENANCE"
    FAULT = "FAULT"
    EMERGENCY_STOP = "EMERGENCY_STOP"