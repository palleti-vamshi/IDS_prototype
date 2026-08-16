"""
test_sensor_alarm_integration.py

Full LightX-IDS integration test:

Tank
    ↓
LevelSensor
    ↓
Sensor Attack
    ↓
AlarmManager
    ↓
AlarmEngine
    ↓
IndustrialEventLogger
"""

from backend.industrial.machines.tank import Tank
from backend.industrial.sensors.level_sensor import LevelSensor

from backend.industrial.alarms.alarm_manager import AlarmManager
from backend.industrial.alarms.industrial_alarm_rules import (
    get_default_alarm_rules,
)

from backend.attacks.sensor.sensor_state import SensorState
from backend.attacks.stealth.stealth_state import StealthState


def main() -> None:

    print("=" * 60)
    print("LIGHTX-IDS SENSOR → ALARM → EVENT INTEGRATION TEST")
    print("=" * 60)

    # ==================================================
    # Clean shared attack state
    # ==================================================

    SensorState.reset()
    StealthState.reset()

    # ==================================================
    # Create Tank
    # ==================================================

    tank = Tank("TANK_ALARM_TEST")

    tank.level_percentage = 65.0

    # ==================================================
    # Create Level Sensor
    # ==================================================

    sensor = LevelSensor(
        sensor_code="LVL-001",
        device_id="level_sensor_alarm_test",
    )

    tank.attach_sensor(sensor)

    # ==================================================
    # Create Alarm Manager
    # ==================================================

    alarm_manager = AlarmManager()

    for rule in get_default_alarm_rules():
        alarm_manager.register_rule(rule)

    # ==================================================
    # NORMAL CONDITION
    # ==================================================

    normal_value = sensor.read()

    alarms = alarm_manager.evaluate(
        sensor.sensor_code,
        normal_value,
    )

    print()
    print("NORMAL CONDITION")
    print("Tank Level     :", tank.level_percentage, "%")
    print("Sensor Reading :", normal_value, "%")
    print("Active Alarms  :", len(alarms))
    print("Events         :", alarm_manager.total_events)

    assert normal_value == 65.0
    assert len(alarms) == 0
    assert alarm_manager.active_alarms == 0
    assert alarm_manager.total_events == 0

    # ==================================================
    # ACTIVATE SPOOFING ATTACK
    # ==================================================

    SensorState.spoofing = True
    SensorState.spoof_value = 99.0

    attacked_value = sensor.read()

    alarms = alarm_manager.evaluate(
        sensor.sensor_code,
        attacked_value,
    )

    print()
    print("SPOOFING ATTACK")
    print("Physical Tank  :", tank.level_percentage, "%")
    print("Sensor Reading :", attacked_value, "%")
    print("Active Alarms  :", len(alarms))
    print("Active Count   :", alarm_manager.active_alarms)
    print("Events         :", alarm_manager.total_events)

    # Physical tank must remain unchanged.
    assert tank.level_percentage == 65.0

    # Sensor observation is attacked.
    assert attacked_value == 99.0

    # 99% must trigger HIGH_TANK_LEVEL.
    assert len(alarms) == 1
    assert alarms[0].alarm_type == "HIGH_TANK_LEVEL"
    assert alarms[0].severity == "CRITICAL"

    # Alarm must become active.
    assert alarm_manager.active_alarms == 1

    # Exactly one event should be logged.
    assert alarm_manager.total_events == 1

    # ==================================================
    # RECOVER FROM ATTACK
    # ==================================================

    SensorState.reset()
    StealthState.reset()

    recovered_value = sensor.read()

    alarms = alarm_manager.evaluate(
        sensor.sensor_code,
        recovered_value,
    )

    print()
    print("AFTER ATTACK RECOVERY")
    print("Physical Tank  :", tank.level_percentage, "%")
    print("Sensor Reading :", recovered_value, "%")
    print("Active Alarms  :", len(alarms))
    print("Active Count   :", alarm_manager.active_alarms)
    print("Events         :", alarm_manager.total_events)

    assert recovered_value == 65.0

    # Alarm should clear.
    assert len(alarms) == 0
    assert alarm_manager.active_alarms == 0

    # Historical event must remain.
    assert alarm_manager.total_events == 1

    # ==================================================
    # TRIGGER AGAIN
    # ==================================================

    SensorState.spoofing = True
    SensorState.spoof_value = 99.0

    attacked_value = sensor.read()

    alarms = alarm_manager.evaluate(
        sensor.sensor_code,
        attacked_value,
    )

    print()
    print("SECOND ATTACK")
    print("Sensor Reading :", attacked_value, "%")
    print("Active Alarms  :", alarm_manager.active_alarms)
    print("Events         :", alarm_manager.total_events)

    assert attacked_value == 99.0
    assert len(alarms) == 1
    assert alarm_manager.active_alarms == 1

    # A new activation should create a new historical event.
    assert alarm_manager.total_events == 2

    # ==================================================
    # CLEAN UP
    # ==================================================

    SensorState.reset()
    StealthState.reset()

    print()
    print("=" * 60)
    print("🎉 SENSOR → ALARM → EVENT INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()