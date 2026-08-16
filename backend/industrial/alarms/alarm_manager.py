"""
alarm_manager.py

Central controller for the industrial alarm subsystem.
"""

from __future__ import annotations

from backend.industrial.alarms.alarm_engine import (
    AlarmEngine,
)

from backend.industrial.events.event_logger import (
    IndustrialEventLogger,
)


class AlarmManager:
    """
    High-level controller for industrial alarms.

    Responsibilities:
        • Register alarm rules
        • Evaluate incoming values
        • Track active alarms
        • Log alarm events
        • Clear alarms
        • Expose alarm status
    """

    def __init__(
        self,
        event_logger: IndustrialEventLogger | None = None,
    ) -> None:

        self.engine = AlarmEngine()

        self.event_logger = (
            event_logger
            if event_logger is not None
            else IndustrialEventLogger()
        )

        self.enabled = True

        # Tracks alarms that have already generated
        # an event during their current active period.
        self.logged_active_alarms = set()

    # ==================================================
    # Rule Management
    # ==================================================

    def register_rule(
        self,
        rule,
    ) -> None:

        self.engine.register_rule(
            rule
        )

    def remove_rule(
        self,
        rule,
    ) -> None:

        self.engine.remove_rule(
            rule
        )

    # ==================================================
    # Evaluation
    # ==================================================

    def evaluate(
        self,
        source: str,
        value: float,
    ) -> list:

        if not self.enabled:

            return []

        alarms = self.engine.evaluate(
            source,
            value,
        )

        # ==========================================
        # Currently active alarm keys
        # ==========================================

        current_active_keys = set()

        # ==========================================
        # Process triggered alarms
        # ==========================================

        for alarm in alarms:

            alarm_key = (
                f"{alarm.alarm_type}:"
                f"{alarm.source}"
            )

            current_active_keys.add(
                alarm_key
            )

            # ======================================
            # New alarm activation
            # ======================================

            if (
                alarm_key
                not in self.logged_active_alarms
            ):

                self.event_logger.log(
                    event_type="ALARM_TRIGGERED",
                    source=alarm.source,
                    severity=alarm.severity,
                    message=alarm.message,
                    metadata={
                        "alarm_key":
                            alarm_key,

                        "alarm_type":
                            alarm.alarm_type,

                        "value":
                            alarm.value,

                        "threshold":
                            alarm.threshold,

                        "unit":
                            alarm.unit,
                    },
                )

                self.logged_active_alarms.add(
                    alarm_key
                )

        # ==========================================
        # Remove recovered alarms from the
        # active-event tracking set.
        #
        # Historical events remain untouched.
        # ==========================================

        self.logged_active_alarms.intersection_update(
            current_active_keys
        )

        return alarms

    # ==================================================
    # Alarm Management
    # ==================================================

    def clear_alarm(
        self,
        alarm_key: str,
    ) -> None:

        self.engine.clear_alarm(
            alarm_key
        )

        self.logged_active_alarms.discard(
            alarm_key
        )

    def clear_all(self) -> None:

        self.engine.clear_all()

        self.logged_active_alarms.clear()

    # ==================================================
    # Status
    # ==================================================

    @property
    def active_alarms(self) -> int:

        return self.engine.active_count

    @property
    def total_rules(self) -> int:

        return self.engine.rule_count

    @property
    def total_triggered(self) -> int:

        return self.engine.total_triggered

    @property
    def total_events(self) -> int:

        return self.event_logger.total_events

    def get_status(self) -> dict:

        status = self.engine.get_status()

        status["enabled"] = self.enabled

        status["event_logger"] = (
            self.event_logger.get_status()
        )

        return status

    # ==================================================
    # Lifecycle
    # ==================================================

    def enable(self) -> None:

        self.enabled = True

    def disable(self) -> None:

        self.enabled = False

    def reset(self) -> None:

        self.engine.clear_all()

        self.event_logger.clear()

        self.logged_active_alarms.clear()

        self.enabled = True

    def __str__(self) -> str:

        return (
            f"AlarmManager("
            f"rules={self.total_rules}, "
            f"active={self.active_alarms}, "
            f"events={self.total_events})"
        )