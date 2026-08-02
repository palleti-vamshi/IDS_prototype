"""
Tests for Machine Framework.
"""

from backend.industrial.machines import (
    Motor,
    Pump,
    Valve,
    Conveyor,
    Tank,
    Compressor,
)


class MockSensor:
    def __init__(self, sensor_code: str):
        self.sensor_code = sensor_code


def main():

    print("=" * 60)
    print("LIGHTX-IDS MACHINE FRAMEWORK TEST")
    print("=" * 60)

    machines = [
        Motor("MTR-001", "Assembly Motor"),
        Pump("PMP-001", "Cooling Pump"),
        Valve("VLV-001", "Main Valve"),
        Conveyor("CNV-001", "Main Conveyor"),
        Tank("TNK-001", "Storage Tank"),
        Compressor("CMP-001", "Air Compressor"),
    ]

    for machine in machines:

        print(f"\nTesting {machine.name}")

        machine.start()

        machine.update_runtime(2.5)

        machine.update_health(95)

        machine.update_telemetry(dummy_value=10)

        sensor = MockSensor("TMP-001")

        machine.attach_sensor(sensor)

        print(machine.get_status())

        machine.maintenance()

        machine.fault()

        machine.stop()

    print("\n")
    print("=" * 60)
    print("ALL MACHINE TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()