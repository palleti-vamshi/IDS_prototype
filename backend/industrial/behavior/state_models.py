"""
state_models.py

Behavior states used by the Industrial Behavior Engine.
"""

from enum import Enum


class BehaviorState(Enum):
    """
    Machine behavior states.

    These represent how a machine behaves during
    simulation, independent of its operational state.
    """

    STOPPED = "STOPPED"

    STARTING = "STARTING"

    WARMUP = "WARMUP"

    NORMAL = "NORMAL"

    HIGH_LOAD = "HIGH_LOAD"

    OVERLOADED = "OVERLOADED"

    IDLE = "IDLE"

    MAINTENANCE = "MAINTENANCE"

    FAULT = "FAULT"

    SHUTDOWN = "SHUTDOWN"