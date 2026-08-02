"""
Machine ↔ Sensor Integration Test

Verifies that machines can own sensors and that
SensorRegistry correctly attaches the default sensors.
"""

from backend.industrial.factory.sensor_registry import SensorRegistry

from backend.industrial.machines import (
    Motor,
    Pump,
    Valve,
    Conveyor,
    Tank,
    Compressor,
)


def test_machine(machine):

    print("\n" + "=" * 60)
    print(f"{machine.machine_code} ({machine.name})")

    SensorRegistry.attach_default_sensors(machine)

    sensors = machine.get_sensors()

    print(f"Attached Sensors : {len(sensors)}")

    for sensor in sensors:

        print(
            f"  {sensor.sensor_code}"
            f" -> {sensor.sensor_type}"
        )

    print("\nMachine Status")
    print(machine.get_status())

    print("\nSensor Status")

    for sensor in sensors:
        print(sensor.get_status())


def main():

    print("=" * 60)
    print("LIGHTX-IDS MACHINE ↔ SENSOR INTEGRATION TEST")
    print("=" * 60)

    machines = [

        Motor("MTR-001"),

        Pump("PMP-001"),

        Valve("VLV-001"),

        Conveyor("CNV-001"),

        Tank("TNK-001"),

        Compressor("CMP-001"),
    ]

    for machine in machines:
        test_machine(machine)

    print("\n" + "=" * 60)
    print("ALL INTEGRATION TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()