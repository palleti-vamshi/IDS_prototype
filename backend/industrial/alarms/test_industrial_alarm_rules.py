"""
test_industrial_alarm_rules.py

Tests the complete default industrial alarm rule set.
"""

from backend.industrial.alarms.alarm_rule import AlarmRule
from backend.industrial.alarms.industrial_alarm_rules import (
    get_default_alarm_rules,
)


def main() -> None:

    rules = get_default_alarm_rules()

    # ==========================================
    # Basic validation
    # ==========================================

    assert isinstance(rules, list)

    assert all(
        isinstance(rule, AlarmRule)
        for rule in rules
    )

    # ==========================================
    # All 10 sensor sources
    # ==========================================

    expected_sources = {
        "TMP-001",
        "PRS-001",
        "FLW-001",
        "CUR-001",
        "LVL-001",
        "RPM-001",
        "VIB-001",
        "PRX-001",
        "VLT-001",
        "HUM-001",
    }

    actual_sources = {
        rule.source
        for rule in rules
    }

    assert actual_sources == expected_sources

    # ==========================================
    # Expected rule counts
    # ==========================================

    expected_counts = {
        "TMP-001": 2,
        "PRS-001": 2,
        "FLW-001": 2,
        "CUR-001": 1,
        "LVL-001": 2,
        "RPM-001": 2,
        "VIB-001": 1,
        "PRX-001": 1,
        "VLT-001": 2,
        "HUM-001": 2,
    }

    for source, expected_count in expected_counts.items():

        actual_count = sum(
            rule.source == source
            for rule in rules
        )

        assert actual_count == expected_count

    # ==========================================
    # Direction validation
    # ==========================================

    assert all(
        rule.direction in {"HIGH", "LOW"}
        for rule in rules
    )

    # ==========================================
    # Evaluation tests
    # ==========================================

    high_rpm = next(
        rule
        for rule in rules
        if rule.alarm_type == "HIGH_RPM"
    )

    assert high_rpm.evaluate(1900.0)
    assert not high_rpm.evaluate(1500.0)

    high_vibration = next(
        rule
        for rule in rules
        if rule.alarm_type == "HIGH_VIBRATION"
    )

    assert high_vibration.evaluate(6.0)
    assert not high_vibration.evaluate(2.0)

    low_proximity = next(
        rule
        for rule in rules
        if rule.alarm_type == "LOW_PROXIMITY"
    )

    assert low_proximity.evaluate(10.0)
    assert not low_proximity.evaluate(100.0)

    high_voltage = next(
        rule
        for rule in rules
        if rule.alarm_type == "HIGH_VOLTAGE"
    )

    assert high_voltage.evaluate(260.0)
    assert not high_voltage.evaluate(230.0)

    low_voltage = next(
        rule
        for rule in rules
        if rule.alarm_type == "LOW_VOLTAGE"
    )

    assert low_voltage.evaluate(190.0)
    assert not low_voltage.evaluate(230.0)

    high_humidity = next(
        rule
        for rule in rules
        if rule.alarm_type == "HIGH_HUMIDITY"
    )

    assert high_humidity.evaluate(90.0)
    assert not high_humidity.evaluate(60.0)

    # ==========================================
    # Rule creation test
    # ==========================================

    alarm = high_rpm.create_alarm(1900.0)

    assert alarm is not None
    assert alarm.alarm_type == "HIGH_RPM"
    assert alarm.source == "RPM-001"
    assert alarm.value == 1900.0

    print("=" * 60)
    print("🎉 INDUSTRIAL ALARM RULE CONFIGURATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
