"""
attack_type.py

Attack categories supported by LightX-IDS.
"""

from __future__ import annotations

from enum import Enum


class AttackType(Enum):
    """
    Categories of cyber attacks.
    """

    NETWORK = "NETWORK"

    SENSOR = "SENSOR"

    PLC = "PLC"

    PROCESS = "PROCESS"

    STEALTH = "STEALTH"