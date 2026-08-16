"""
alarm_engine.py

Central industrial alarm evaluation engine for LightX-IDS.
"""

from __future__ import annotations

from backend.industrial.alarms.alarm_rule import AlarmRule


class AlarmEngine:
    """
    Evaluates registered alarm rules against
    industrial machine and sensor values.
    """

    def __init__(self) -> None:

        self.rules: list[AlarmRule] = []

        self.active_alarms = {}

        self.total_triggered = 0

    # ==================================================
    # Rule Registration
    # ==================================================

    def register_rule(
        self,
        rule: AlarmRule,
    ) -> None:

        if rule not in self.rules:

            self.rules.append(rule)

    def remove_rule(
        self,
        rule: AlarmRule,
    ) -> None:

        if rule in self.rules:

            self.rules.remove(rule)

    # ==================================================
    # Evaluation
    # ==================================================

    def evaluate(
        self,
        source: str,
        value: float,
    ) -> list:

        triggered = []

        for rule in self.rules:

            if rule.source != source:
                continue

            alarm = rule.create_alarm(value)

            alarm_key = (
                f"{rule.alarm_type}:"
                f"{rule.source}"
            )

            if alarm is not None:

                triggered.append(alarm)

                if alarm_key not in self.active_alarms:

                    self.active_alarms[
                        alarm_key
                    ] = alarm

                    self.total_triggered += 1

            else:

                self.active_alarms.pop(
                    alarm_key,
                    None,
                )

        return triggered

    # ==================================================
    # Clear
    # ==================================================

    def clear_alarm(
        self,
        alarm_key: str,
    ) -> None:

        self.active_alarms.pop(
            alarm_key,
            None,
        )

    def clear_all(self) -> None:

        self.active_alarms.clear()

    # ==================================================
    # Status
    # ==================================================

    @property
    def active_count(self) -> int:

        return len(
            self.active_alarms
        )

    @property
    def rule_count(self) -> int:

        return len(
            self.rules
        )

    def get_status(self) -> dict:

        return {

            "registered_rules":
                self.rule_count,

            "active_alarms":
                self.active_count,

            "total_triggered":
                self.total_triggered,

            "alarms": [
                {
                    "alarm_id": alarm.alarm_id,
                    "alarm_type": alarm.alarm_type,
                    "source": alarm.source,
                    "severity": alarm.severity,
                    "message": alarm.message,
                    "value": alarm.value,
                    "threshold": alarm.threshold,
                    "unit": alarm.unit,
                    "is_active": alarm.is_active,
                }
                for alarm in self.active_alarms.values()
            ],
        }

    def __str__(self) -> str:

        return (
            f"AlarmEngine("
            f"rules={self.rule_count}, "
            f"active={self.active_count})"
        )