"""
alarm_rule.py

Configurable industrial alarm rules for LightX-IDS.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlarmRule:
    """
    Defines the conditions required to trigger
    an industrial alarm.
    """

    alarm_type: str
    source: str
    severity: str
    message: str

    threshold: float

    unit: str

    direction: str = "HIGH"

    # ==========================================
    # Evaluation
    # ==========================================

    def evaluate(
        self,
        value: float,
    ) -> bool:
        """
        Evaluate whether the supplied value
        violates this alarm rule.
        """

        if self.direction == "HIGH":

            return value >= self.threshold

        if self.direction == "LOW":

            return value <= self.threshold

        raise ValueError(
            f"Unsupported alarm direction: "
            f"{self.direction}"
        )

    # ==========================================
    # Alarm Data
    # ==========================================

    def create_alarm(
        self,
        value: float,
    ):
        """
        Create an Alarm from this rule.

        The rule itself does not decide whether
        an alarm should exist. The caller should
        first call evaluate().
        """

        from backend.industrial.alarms.alarm import (
            Alarm,
        )

        if not self.evaluate(value):

            return None

        return Alarm(
            alarm_type=self.alarm_type,
            source=self.source,
            severity=self.severity,
            message=self.message,
            value=value,
            threshold=self.threshold,
            unit=self.unit,
        )

    # ==========================================
    # Status
    # ==========================================

    def get_status(self) -> dict:

        return {

            "alarm_type":
                self.alarm_type,

            "source":
                self.source,

            "severity":
                self.severity,

            "message":
                self.message,

            "threshold":
                self.threshold,

            "unit":
                self.unit,

            "direction":
                self.direction,
        }

    def __str__(self) -> str:

        return (
            f"{self.alarm_type} | "
            f"{self.source} | "
            f"{self.direction} "
            f"{self.threshold}{self.unit} | "
            f"{self.severity}"
        )