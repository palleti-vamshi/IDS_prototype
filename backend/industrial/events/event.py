"""
event.py

Industrial event model for LightX-IDS.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class IndustrialEvent:
    """
    Represents a single industrial event.

    Events are historical records and are separate
    from application/debug logging.
    """

    event_type: str
    source: str
    severity: str
    message: str

    timestamp: datetime = field(
        default_factory=datetime.now
    )

    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict:
        """
        Convert event into a serializable dictionary.
        """

        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "source": self.source,
            "severity": self.severity,
            "message": self.message,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        return (
            f"[{self.severity}] "
            f"{self.event_type} | "
            f"{self.source} | "
            f"{self.message}"
        )