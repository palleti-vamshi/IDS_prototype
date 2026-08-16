from backend.industrial.alarms.alarm_manager import (
    AlarmManager,
)

from backend.industrial.alarms.alarm_rule import (
    AlarmRule,
)

from backend.industrial.events.event_logger import (
    IndustrialEventLogger,
)


# ==================================================
# Setup
# ==================================================

event_logger = IndustrialEventLogger()

manager = AlarmManager(
    event_logger=event_logger
)


# ==================================================
# Rule
# ==================================================

rule = AlarmRule(
    alarm_type="HIGH_TEMPERATURE",
    source="MTR-001-TMP",
    severity="WARNING",
    message="Motor temperature is too high.",
    threshold=80.0,
    unit="°C",
    direction="HIGH",
)

manager.register_rule(rule)

assert manager.total_rules == 1


# ==================================================
# Normal
# ==================================================

alarms = manager.evaluate(
    "MTR-001-TMP",
    70.0,
)

assert len(alarms) == 0
assert manager.active_alarms == 0
assert event_logger.total_events == 0


# ==================================================
# Trigger Alarm
# ==================================================

alarms = manager.evaluate(
    "MTR-001-TMP",
    90.0,
)

assert len(alarms) == 1
assert manager.active_alarms == 1

assert event_logger.total_events == 1

event = event_logger.get_latest(1)[0]

assert event.event_type == "ALARM_TRIGGERED"
assert event.source == "MTR-001-TMP"
assert event.severity == "WARNING"


# ==================================================
# Continued Alarm
# ==================================================

alarms = manager.evaluate(
    "MTR-001-TMP",
    95.0,
)

assert len(alarms) == 1

# No duplicate event.
assert event_logger.total_events == 1


# ==================================================
# Recovery
# ==================================================

alarms = manager.evaluate(
    "MTR-001-TMP",
    70.0,
)

assert len(alarms) == 0
assert manager.active_alarms == 0

# Existing event remains in history.
assert event_logger.total_events == 1


# ==================================================
# Re-trigger
# ==================================================

alarms = manager.evaluate(
    "MTR-001-TMP",
    90.0,
)

assert len(alarms) == 1
assert manager.active_alarms == 1

assert event_logger.total_events == 2


# ==================================================
# Status
# ==================================================

status = manager.get_status()

assert status["registered_rules"] == 1
assert status["active_alarms"] == 1
assert status["event_logger"]["total_events"] == 2


print("=" * 60)
print("🎉 ALARM → EVENT LOGGER INTEGRATION TEST PASSED")
print("=" * 60)