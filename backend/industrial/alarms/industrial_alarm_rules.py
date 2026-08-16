"""
industrial_alarm_rules.py

Default industrial alarm rules for LightX-IDS.
"""

from __future__ import annotations

from backend.industrial.alarms.alarm_rule import AlarmRule


def get_default_alarm_rules() -> list[AlarmRule]:
    """
    Return the default industrial alarm rules.

    Rules are based on the sensor codes and units
    used by the LightX-IDS industrial sensors.
    """

    return [

        # ==========================================
        # TEMPERATURE
        # ==========================================

        AlarmRule(
            alarm_type="HIGH_TEMPERATURE",
            source="TMP-001",
            severity="WARNING",
            message="Temperature exceeded safe operating limit.",
            threshold=80.0,
            unit="°C",
            direction="HIGH",
        ),

        AlarmRule(
            alarm_type="LOW_TEMPERATURE",
            source="TMP-001",
            severity="WARNING",
            message="Temperature dropped below safe operating limit.",
            threshold=10.0,
            unit="°C",
            direction="LOW",
        ),

        # ==========================================
        # PRESSURE
        # ==========================================

        AlarmRule(
            alarm_type="HIGH_PRESSURE",
            source="PRS-001",
            severity="CRITICAL",
            message="Pressure exceeded critical operating limit.",
            threshold=220.0,
            unit="kPa",
            direction="HIGH",
        ),

        AlarmRule(
            alarm_type="LOW_PRESSURE",
            source="PRS-001",
            severity="WARNING",
            message="Pressure dropped below safe operating limit.",
            threshold=50.0,
            unit="kPa",
            direction="LOW",
        ),

        # ==========================================
        # FLOW
        # ==========================================

        AlarmRule(
            alarm_type="HIGH_FLOW",
            source="FLW-001",
            severity="WARNING",
            message="Flow rate exceeded safe operating limit.",
            threshold=120.0,
            unit="L/min",
            direction="HIGH",
        ),

        AlarmRule(
            alarm_type="LOW_FLOW",
            source="FLW-001",
            severity="WARNING",
            message="Flow rate dropped below safe operating limit.",
            threshold=20.0,
            unit="L/min",
            direction="LOW",
        ),

        # ==========================================
        # CURRENT
        # ==========================================

        AlarmRule(
            alarm_type="HIGH_CURRENT",
            source="CUR-001",
            severity="CRITICAL",
            message="Electrical current exceeded safe operating limit.",
            threshold=30.0,
            unit="A",
            direction="HIGH",
        ),

        # ==========================================
        # LEVEL
        # ==========================================

        AlarmRule(
            alarm_type="HIGH_TANK_LEVEL",
            source="LVL-001",
            severity="CRITICAL",
            message="Tank level reached critical high limit.",
            threshold=98.0,
            unit="%",
            direction="HIGH",
        ),

        AlarmRule(
            alarm_type="LOW_TANK_LEVEL",
            source="LVL-001",
            severity="CRITICAL",
            message="Tank level reached critical low limit.",
            threshold=2.0,
            unit="%",
            direction="LOW",
        ),

        # ==========================================
        # RPM
        # ==========================================

        AlarmRule(
            alarm_type="HIGH_RPM",
            source="RPM-001",
            severity="WARNING",
            message="Machine RPM exceeded safe operating limit.",
            threshold=1800.0,
            unit="RPM",
            direction="HIGH",
        ),

        AlarmRule(
            alarm_type="LOW_RPM",
            source="RPM-001",
            severity="WARNING",
            message="Machine RPM dropped below safe operating limit.",
            threshold=1000.0,
            unit="RPM",
            direction="LOW",
        ),

        # ==========================================
        # VIBRATION
        # ==========================================

        AlarmRule(
            alarm_type="HIGH_VIBRATION",
            source="VIB-001",
            severity="CRITICAL",
            message="Machine vibration exceeded safe operating limit.",
            threshold=5.0,
            unit="g",
            direction="HIGH",
        ),

        # ==========================================
        # PROXIMITY
        # ==========================================

        AlarmRule(
            alarm_type="LOW_PROXIMITY",
            source="PRX-001",
            severity="WARNING",
            message="Object distance dropped below safe limit.",
            threshold=20.0,
            unit="mm",
            direction="LOW",
        ),

        # ==========================================
        # VOLTAGE
        # ==========================================

        AlarmRule(
            alarm_type="HIGH_VOLTAGE",
            source="VLT-001",
            severity="WARNING",
            message="Voltage exceeded safe operating limit.",
            threshold=250.0,
            unit="V",
            direction="HIGH",
        ),

        AlarmRule(
            alarm_type="LOW_VOLTAGE",
            source="VLT-001",
            severity="WARNING",
            message="Voltage dropped below safe operating limit.",
            threshold=200.0,
            unit="V",
            direction="LOW",
        ),

        # ==========================================
        # HUMIDITY
        # ==========================================

        AlarmRule(
            alarm_type="HIGH_HUMIDITY",
            source="HUM-001",
            severity="WARNING",
            message="Humidity exceeded safe operating limit.",
            threshold=80.0,
            unit="%",
            direction="HIGH",
        ),

        AlarmRule(
            alarm_type="LOW_HUMIDITY",
            source="HUM-001",
            severity="WARNING",
            message="Humidity dropped below safe operating limit.",
            threshold=20.0,
            unit="%",
            direction="LOW",
        ),
    ]
