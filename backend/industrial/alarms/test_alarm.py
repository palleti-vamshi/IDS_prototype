from backend.industrial.alarms.alarm import Alarm


alarm = Alarm(
    alarm_type="HIGH_TEMPERATURE",
    source="MTR-001-TMP",
    severity="WARNING",
    message="Motor temperature exceeded warning threshold.",
    value=82.0,
    threshold=80.0,
    unit="°C",
)


assert alarm.is_active
assert not alarm.is_acknowledged
assert not alarm.is_cleared


alarm.acknowledge()

assert alarm.is_active
assert alarm.is_acknowledged
assert not alarm.is_cleared


alarm.clear()

assert not alarm.is_active
assert alarm.is_acknowledged
assert alarm.is_cleared


data = alarm.to_dict()

assert data["alarm_type"] == "HIGH_TEMPERATURE"
assert data["source"] == "MTR-001-TMP"
assert data["severity"] == "WARNING"
assert data["value"] == 82.0
assert data["threshold"] == 80.0
assert data["unit"] == "°C"


print("=" * 60)
print("🎉 ALARM MODEL TEST PASSED")
print("=" * 60)