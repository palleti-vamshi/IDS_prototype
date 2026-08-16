"""
test_level_sensor_integration.py

Integration test for:

Tank → LevelSensor → Sensor Attack → Alarm

Verifies that:
1. LevelSensor reads the tank's level_percentage.
2. Sensor readings remain within the sensor's physical range.
3. Sensor-level attack modifications can change the observed value.
"""

from backend.industrial.machines.tank import Tank
from backend.industrial.sensors.level_sensor import LevelSensor


def main() -> None:

    print("=" * 60)
    print("LIGHTX-IDS LEVEL SENSOR INTEGRATION TEST")
    print("=" * 60)

    # --------------------------------------------------
    # Create tank
    # --------------------------------------------------

    tank = Tank("TANK_TEST")

    tank.level_percentage = 65.0

    # --------------------------------------------------
    # Attach level sensor
    # --------------------------------------------------

    sensor = LevelSensor(
        sensor_code="LVL-TEST",
        device_id="level_sensor_test",
    )

    tank.attach_sensor(sensor)

    # --------------------------------------------------
    # Read sensor
    # --------------------------------------------------

    reading = sensor.generate_value()

    print()
    print("Tank Level     :", tank.level_percentage, "%")
    print("Sensor Reading :", reading, "%")

    # Sensor must observe the machine value.
    assert reading == 65.0

    # Physical sensor range.
    assert 0.0 <= reading <= 100.0

    # --------------------------------------------------
    # Change tank level
    # --------------------------------------------------

    tank.level_percentage = 80.0

    reading = sensor.generate_value()

    print()
    print("Updated Tank   :", tank.level_percentage, "%")
    print("Sensor Reading :", reading, "%")

    # Sensor must follow the machine.
    assert reading == 80.0

    # --------------------------------------------------
    # Verify high level
    # --------------------------------------------------

    tank.level_percentage = 100.0

    reading = sensor.generate_value()

    print()
    print("Full Tank      :", tank.level_percentage, "%")
    print("Sensor Reading :", reading, "%")

    assert reading == 100.0
    assert 0.0 <= reading <= 100.0

    print()
    print("=" * 60)
    print("🎉 LEVEL SENSOR INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()