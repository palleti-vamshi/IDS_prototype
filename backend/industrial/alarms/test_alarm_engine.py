from backend.industrial.alarms.alarm_engine import (
    AlarmEngine,
)

from backend.industrial.alarms.alarm_rule import (
    AlarmRule,
)


engine = AlarmEngine()


# ==========================================
# Register Rules
# ==========================================

temperature_rule = AlarmRule(
    alarm_type="HIGH_TEMPERATURE",
    source="MTR-001-TMP",
    severity="WARNING",
    message="Motor temperature is too high.",
    threshold=80.0,
    unit="°C",
    direction="HIGH",
)

pressure_rule = AlarmRule(
    alarm_type="LOW_PRESSURE",
    source="PMP-001-PRS",
    severity="CRITICAL",
    message="Pump pressure is critically low.",
    threshold=50.0,
    unit="kPa",
    direction="LOW",
)


engine.register_rule(
    temperature_rule
)

engine.register_rule(
    pressure_rule
)


assert engine.rule_count == 2


# ==========================================
# Normal Value
# ==========================================

alarms = engine.evaluate(
    "MTR-001-TMP",
    60.0,
)

assert len(alarms) == 0
assert engine.active_count == 0


# ==========================================
# Trigger Temperature Alarm
# ==========================================

alarms = engine.evaluate(
    "MTR-001-TMP",
    90.0,
)

assert len(alarms) == 1
assert engine.active_count == 1


# ==========================================
# Pressure Alarm
# ==========================================

alarms = engine.evaluate(
    "PMP-001-PRS",
    30.0,
)

assert len(alarms) == 1
assert engine.active_count == 2


# ==========================================
# Recover Temperature
# ==========================================

alarms = engine.evaluate(
    "MTR-001-TMP",
    70.0,
)

assert len(alarms) == 0
assert engine.active_count == 1


# ==========================================
# Status
# ==========================================

status = engine.get_status()

assert status["registered_rules"] == 2
assert status["active_alarms"] == 1
assert status["total_triggered"] == 2


print("=" * 60)
print("🎉 ALARM ENGINE TEST PASSED")
print("=" * 60)