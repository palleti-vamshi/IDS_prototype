"""
event_logger.py

Industrial event history manager for LightX-IDS.
"""

from __future__ import annotations

from backend.industrial.events.event import (
    IndustrialEvent,
)


class IndustrialEventLogger:
    """
    Stores and manages industrial events.

    This is intentionally separate from the normal
    application logger.
    """

    def __init__(
        self,
        max_events: int = 10000,
    ) -> None:

        if max_events <= 0:
            raise ValueError(
                "max_events must be greater than zero."
            )

        self.max_events = max_events

        self.events: list[IndustrialEvent] = []

    # ==================================================
    # Record
    # ==================================================

    def record(
        self,
        event: IndustrialEvent,
    ) -> IndustrialEvent:
        """
        Record an industrial event.
        """

        self.events.append(event)

        # Keep only the newest events.
        if len(self.events) > self.max_events:

            self.events = self.events[
                -self.max_events:
            ]

        return event

    # ==================================================
    # Create + Record
    # ==================================================

    def log(
        self,
        event_type: str,
        source: str,
        severity: str,
        message: str,
        metadata: dict | None = None,
    ) -> IndustrialEvent:
        """
        Create and record an industrial event.
        """

        event = IndustrialEvent(
            event_type=event_type,
            source=source,
            severity=severity,
            message=message,
            metadata=metadata or {},
        )

        return self.record(event)

    # ==================================================
    # Access
    # ==================================================

    def get_events(self) -> list[IndustrialEvent]:
        """
        Return a copy of the event history.
        """

        return list(self.events)

    def get_latest(
        self,
        count: int = 10,
    ) -> list[IndustrialEvent]:
        """
        Return the latest events.
        """

        if count <= 0:
            return []

        return self.events[-count:]

    # ==================================================
    # Filtering
    # ==================================================

    def get_by_source(
        self,
        source: str,
    ) -> list[IndustrialEvent]:

        return [
            event
            for event in self.events
            if event.source == source
        ]

    def get_by_severity(
        self,
        severity: str,
    ) -> list[IndustrialEvent]:

        return [
            event
            for event in self.events
            if event.severity == severity
        ]

    def get_by_type(
        self,
        event_type: str,
    ) -> list[IndustrialEvent]:

        return [
            event
            for event in self.events
            if event.event_type == event_type
        ]

    # ==================================================
    # Management
    # ==================================================

    def clear(self) -> None:

        self.events.clear()

    # ==================================================
    # Information
    # ==================================================

    @property
    def total_events(self) -> int:

        return len(self.events)

    def get_status(self) -> dict:

        return {
            "total_events": self.total_events,
            "max_events": self.max_events,
        }

    def __len__(self) -> int:

        return len(self.events)