"""
alarm.py

Industrial alarm model for LightX-IDS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Alarm:
    """
    Represents an active or historical industrial alarm.
    """

    alarm_type: str
    source: str
    severity: str
    message: str

    value: float | None = None
    threshold: float | None = None
    unit: str | None = None

    alarm_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    created_at: datetime = field(
        default_factory=datetime.now
    )

    acknowledged_at: datetime | None = None

    cleared_at: datetime | None = None

    # ==========================================
    # Lifecycle
    # ==========================================

    @property
    def is_active(self) -> bool:
        """
        Return True while the alarm is active.
        """

        return self.cleared_at is None

    @property
    def is_acknowledged(self) -> bool:
        """
        Return True when the alarm has been acknowledged.
        """

        return self.acknowledged_at is not None

    @property
    def is_cleared(self) -> bool:
        """
        Return True when the alarm has been cleared.
        """

        return self.cleared_at is not None

    # ==========================================
    # Acknowledge
    # ==========================================

    def acknowledge(self) -> None:
        """
        Acknowledge the alarm.
        """

        if self.is_cleared:
            return

        if self.acknowledged_at is None:

            self.acknowledged_at = (
                datetime.now()
            )

    # ==========================================
    # Clear
    # ==========================================

    def clear(self) -> None:
        """
        Clear the alarm.
        """

        if self.cleared_at is None:

            self.cleared_at = (
                datetime.now()
            )

    # ==========================================
    # Serialization
    # ==========================================

    def to_dict(self) -> dict:

        return {

            "alarm_id":
                self.alarm_id,

            "alarm_type":
                self.alarm_type,

            "source":
                self.source,

            "severity":
                self.severity,

            "message":
                self.message,

            "value":
                self.value,

            "threshold":
                self.threshold,

            "unit":
                self.unit,

            "created_at":
                self.created_at.isoformat(),

            "acknowledged_at":
                (
                    self.acknowledged_at.isoformat()
                    if self.acknowledged_at
                    else None
                ),

            "cleared_at":
                (
                    self.cleared_at.isoformat()
                    if self.cleared_at
                    else None
                ),

            "active":
                self.is_active,

            "acknowledged":
                self.is_acknowledged,

            "cleared":
                self.is_cleared,
        }

    # ==========================================
    # String
    # ==========================================

    def __str__(self) -> str:

        return (
            f"[{self.severity}] "
            f"{self.alarm_type} | "
            f"{self.source} | "
            f"{self.message}"
        )