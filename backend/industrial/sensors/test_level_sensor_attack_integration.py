"""
test_level_sensor_attack_integration.py

Verifies the real LightX-IDS sensor attack path:

Tank
    ↓
LevelSensor
    ↓
BaseSensor.read()
    ↓
Sensor Spoofing Attack
    ↓
Modified sensor value
"""

from backend.industrial.machines.tank import Tank
from backend.industrial.sensors.level_sensor import LevelSensor

from backend.attacks.sensor.sensor_state import SensorState
from backend.attacks.stealth.stealth_state import StealthState


def main() -> None:

    print("=" * 60)
    print("LIGHTX-IDS SENSOR ATTACK INTEGRATION TEST")
    print("=" * 60)

    # --------------------------------------------------
    # Clean shared attack state first
    # --------------------------------------------------

    SensorState.reset()
    StealthState.reset()

    # --------------------------------------------------
    # Create tank
    # --------------------------------------------------

    tank = Tank("TANK_ATTACK_TEST")

    tank.level_percentage = 65.0

    # --------------------------------------------------
    # Create and attach level sensor
    # --------------------------------------------------

    sensor = LevelSensor(
        sensor_code="LVL-ATTACK-TEST",
        device_id="level_sensor_attack_test",
    )

    tank.attach_sensor(sensor)

    # --------------------------------------------------
    # NORMAL READING
    # --------------------------------------------------

    normal_reading = sensor.read()

    print()
    print("NORMAL")
    print("Tank Level     :", tank.level_percentage, "%")
    print("Sensor Reading :", normal_reading, "%")

    assert normal_reading == 65.0

    # --------------------------------------------------
    # ACTIVATE SENSOR SPOOFING
    # --------------------------------------------------

    SensorState.spoofing = True
    SensorState.spoof_value = 90.0

    spoofed_reading = sensor.read()

    print()
    print("SPOOFING ATTACK")
    print("Tank Level     :", tank.level_percentage, "%")
    print("Sensor Reading :", spoofed_reading, "%")

    # Physical tank remains unchanged.
    assert tank.level_percentage == 65.0

    # Sensor should report the spoofed value.
    assert spoofed_reading == 90.0

    # --------------------------------------------------
    # CLEAN ATTACK STATE
    # --------------------------------------------------

    SensorState.reset()
    StealthState.reset()

    restored_reading = sensor.read()

    print()
    print("AFTER ATTACK")
    print("Tank Level     :", tank.level_percentage, "%")
    print("Sensor Reading :", restored_reading, "%")

    assert restored_reading == 65.0

    print()
    print("=" * 60)
    print("🎉 SENSOR ATTACK INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()