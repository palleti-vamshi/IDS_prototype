from backend.industrial.alarms.alarm_rule import (
    AlarmRule,
)


# ==========================================
# HIGH Rule
# ==========================================

high_rule = AlarmRule(
    alarm_type="HIGH_TEMPERATURE",
    source="MTR-001-TMP",
    severity="WARNING",
    message="Motor temperature is too high.",
    threshold=80.0,
    unit="°C",
    direction="HIGH",
)


assert not high_rule.evaluate(75.0)
assert high_rule.evaluate(80.0)
assert high_rule.evaluate(90.0)


alarm = high_rule.create_alarm(90.0)

assert alarm is not None
assert alarm.value == 90.0
assert alarm.threshold == 80.0
assert alarm.is_active


# ==========================================
# LOW Rule
# ==========================================

low_rule = AlarmRule(
    alarm_type="LOW_PRESSURE",
    source="PMP-001-PRS",
    severity="CRITICAL",
    message="Pump pressure is critically low.",
    threshold=50.0,
    unit="kPa",
    direction="LOW",
)


assert not low_rule.evaluate(75.0)
assert low_rule.evaluate(50.0)
assert low_rule.evaluate(30.0)


alarm = low_rule.create_alarm(30.0)

assert alarm is not None
assert alarm.value == 30.0
assert alarm.threshold == 50.0


# ==========================================
# Status
# ==========================================

status = high_rule.get_status()

assert status["alarm_type"] == "HIGH_TEMPERATURE"
assert status["threshold"] == 80.0
assert status["direction"] == "HIGH"


print("=" * 60)
print("🎉 ALARM RULE TEST PASSED")
print("=" * 60)