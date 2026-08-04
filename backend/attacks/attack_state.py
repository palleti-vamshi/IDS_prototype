"""
attack_state.py

Lifecycle states for industrial cyber attacks.
"""

from __future__ import annotations

from enum import Enum


class AttackState(Enum):
    """
    Represents the lifecycle state
    of an attack.
    """

    CREATED = "CREATED"

    READY = "READY"

    RUNNING = "RUNNING"

    PAUSED = "PAUSED"

    STOPPED = "STOPPED"

    COMPLETED = "COMPLETED"