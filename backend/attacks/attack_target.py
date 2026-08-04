"""
attack_target.py

Defines the target layer for cyber attacks.
"""

from __future__ import annotations

from enum import Enum


class AttackTarget(Enum):
    """
    Represents the subsystem affected
    by a cyber attack.
    """

    MACHINE = "MACHINE"

    SENSOR = "SENSOR"

    COMMUNICATION = "COMMUNICATION"

    PLC = "PLC"

    PROCESS = "PROCESS"