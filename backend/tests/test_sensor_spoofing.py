"""
Dedicated Sensor Spoofing Targeting Test

Purpose:
    Validates per-sensor targeted spoofing behavior, ensuring
    only targeted sensors receive spoof modifications while unrelated
    sensors remain completely normal.
"""

from backend.attacks.sensor.sensor_spoofing_attack import SensorSpoofingAttack
from backend.attacks.sensor.sensor_state import SensorState
from backend.industrial.machines.motor import Motor
from backend.industrial.sensors.temperature_sensor import TemperatureSensor
from backend.industrial.sensors.current_sensor import CurrentSensor
from backend.industrial.sensors.rpm_sensor import RPMSensor


def create_test_setup():
    """Create motor and 3 physical sensors attached to it."""
    motor = Motor("MTR-001")

    tmp_sensor = TemperatureSensor(
        sensor_code="MTR-001-TMP",
        device_id="mtr_001_temperature_sensor",
    )
    cur_sensor = CurrentSensor(
        sensor_code="MTR-001-CUR",
        device_id="mtr_001_current_sensor",
    )
    rpm_sensor = RPMSensor(
        sensor_code="MTR-001-RPM",
        device_id="mtr_001_rpm_sensor",
    )

    tmp_sensor.attach_machine(motor)
    cur_sensor.attach_machine(motor)
    rpm_sensor.attach_machine(motor)

    return motor, tmp_sensor, cur_sensor, rpm_sensor


def test_targeted_single_sensor():
    """Test A-F: Specific sensor targeted, unrelated sensors unaffected."""
    print("\n--- Test: Single Target Spoofing (MTR-001-TMP) ---")
    motor, tmp_sensor, cur_sensor, rpm_sensor = create_test_setup()

    baseline_tmp = tmp_sensor.read()
    baseline_cur = cur_sensor.read()
    baseline_rpm = rpm_sensor.read()

    # Pre-attack: All sensor states inactive
    engine = tmp_sensor.attack_engine
    assert not engine.get_state("MTR-001-TMP")["spoof"]
    assert not engine.get_state("MTR-001-CUR")["spoof"]
    assert not engine.get_state("MTR-001-RPM")["spoof"]
    assert not SensorState.spoofing

    # Activate spoofing targeting MTR-001-TMP
    attack = SensorSpoofingAttack(duration=10.0, target_sensor="MTR-001-TMP")
    attack.start()
    assert attack.targets == ["MTR-001-TMP"]
    assert attack.active_targets == ["MTR-001-TMP"]
    assert attack.target_sensor == "MTR-001-TMP"

    # Tick simulation by 5 seconds (50% progress -> offset = 10.0)
    attack.update(5.0)
    assert attack.current_offset == 10.0

    # D: Verify states directly
    assert engine.get_state("MTR-001-TMP")["spoof"] is True
    assert engine.get_state("MTR-001-TMP")["spoof_offset"] == 10.0
    assert engine.get_state("MTR-001-CUR")["spoof"] is False
    assert engine.get_state("MTR-001-RPM")["spoof"] is False
    assert SensorState.spoofing is False

    # C: Verify readings
    spoofed_tmp = tmp_sensor.read()
    reading_cur = cur_sensor.read()
    reading_rpm = rpm_sensor.read()

    assert spoofed_tmp == baseline_tmp + 10.0, f"Expected {baseline_tmp + 10.0}, got {spoofed_tmp}"
    assert reading_cur == baseline_cur, f"Expected {baseline_cur}, got {reading_cur}"
    assert reading_rpm == baseline_rpm, f"Expected {baseline_rpm}, got {reading_rpm}"

    # E: Stop attack
    attack.stop()

    # F: Verify return to normal state
    assert engine.get_state("MTR-001-TMP")["spoof"] is False
    assert engine.get_state("MTR-001-CUR")["spoof"] is False
    assert engine.get_state("MTR-001-RPM")["spoof"] is False
    assert SensorState.spoofing is False

    assert tmp_sensor.read() == baseline_tmp
    assert cur_sensor.read() == baseline_cur
    assert rpm_sensor.read() == baseline_rpm

    print("✅ Single target spoofing test passed.")


def test_default_target_behavior():
    """Test G: Default behavior when no target is supplied."""
    print("\n--- Test: Default Target Selection ---")
    motor, tmp_sensor, cur_sensor, rpm_sensor = create_test_setup()

    baseline_tmp = tmp_sensor.read()
    baseline_cur = cur_sensor.read()
    baseline_rpm = rpm_sensor.read()

    attack = SensorSpoofingAttack(duration=10.0)
    # G: Must select exactly MTR-001-TMP
    assert attack.active_targets == ["MTR-001-TMP"]
    assert attack.target_sensor == "MTR-001-TMP"

    attack.start()
    assert attack.targets == ["MTR-001-TMP"]

    attack.update(5.0)
    assert tmp_sensor.attack_engine.get_state("MTR-001-TMP")["spoof"] is True
    assert cur_sensor.attack_engine.get_state("MTR-001-CUR")["spoof"] is False
    assert rpm_sensor.attack_engine.get_state("MTR-001-RPM")["spoof"] is False

    assert tmp_sensor.read() == baseline_tmp + 10.0
    assert cur_sensor.read() == baseline_cur
    assert rpm_sensor.read() == baseline_rpm

    attack.stop()
    assert tmp_sensor.attack_engine.get_state("MTR-001-TMP")["spoof"] is False
    assert tmp_sensor.read() == baseline_tmp

    print("✅ Default target selection test passed.")


def test_multiple_targets():
    """Test H: Explicit multiple targets using add_target()."""
    print("\n--- Test: Multiple Targets Spoofing ---")
    motor, tmp_sensor, cur_sensor, rpm_sensor = create_test_setup()

    baseline_tmp = tmp_sensor.read()
    baseline_cur = cur_sensor.read()
    baseline_rpm = rpm_sensor.read()

    attack = SensorSpoofingAttack(duration=10.0)
    attack.add_target("MTR-001-TMP")
    attack.add_target("MTR-001-CUR")

    assert attack.targets == ["MTR-001-TMP", "MTR-001-CUR"]
    assert attack.active_targets == ["MTR-001-TMP", "MTR-001-CUR"]

    attack.start()
    attack.update(5.0)

    engine = tmp_sensor.attack_engine
    assert engine.get_state("MTR-001-TMP")["spoof"] is True
    assert engine.get_state("MTR-001-CUR")["spoof"] is True
    assert engine.get_state("MTR-001-RPM")["spoof"] is False

    assert tmp_sensor.read() == baseline_tmp + 10.0
    assert cur_sensor.read() == baseline_cur + 10.0
    assert rpm_sensor.read() == baseline_rpm

    attack.stop()
    assert engine.get_state("MTR-001-TMP")["spoof"] is False
    assert engine.get_state("MTR-001-CUR")["spoof"] is False
    assert engine.get_state("MTR-001-RPM")["spoof"] is False

    assert tmp_sensor.read() == baseline_tmp
    assert cur_sensor.read() == baseline_cur
    assert rpm_sensor.read() == baseline_rpm

    print("✅ Multiple targets spoofing test passed.")


def main():
    print("=" * 60)
    print("LIGHTX-IDS SENSOR SPOOFING TARGETING TEST")
    print("=" * 60)

    test_targeted_single_sensor()
    test_default_target_behavior()
    test_multiple_targets()

    print("\n" + "=" * 60)
    print("🎉 ALL SENSOR SPOOFING TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
