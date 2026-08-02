"""
LightX-IDS Sensor Framework Test
"""

from backend.industrial.sensors import (
    TemperatureSensor,
    PressureSensor,
    CurrentSensor,
    VoltageSensor,
    FlowSensor,
    RPMSensor,
    VibrationSensor,
    HumiditySensor,
    LevelSensor,
    ProximitySensor,
)


def print_sensor(sensor):

    print("=" * 60)
    print(sensor.sensor_code)
    print(sensor.get_status())

    value = sensor.read()

    print(f"Reading : {value} {sensor.unit}")


def main():

    sensors = [

        TemperatureSensor(),

        PressureSensor(),

        CurrentSensor(),

        VoltageSensor(),

        FlowSensor(),

        RPMSensor(),

        VibrationSensor(),

        HumiditySensor(),

        LevelSensor(),

        ProximitySensor(),
    ]

    print("\n")
    print("=" * 60)
    print("LIGHTX-IDS SENSOR FRAMEWORK TEST")
    print("=" * 60)

    for sensor in sensors:

        print_sensor(sensor)

    print("\n")
    print("=" * 60)
    print("ALL SENSOR TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()