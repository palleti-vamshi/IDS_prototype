"""
test_dependency.py

Validation tests for the LightX-IDS
Machine Dependency Engine.
"""

from backend.industrial.machines.tank import Tank
from backend.industrial.machines.pump import Pump
from backend.industrial.machines.valve import Valve
from backend.industrial.machines.conveyor import Conveyor
from backend.industrial.machines.motor import Motor
from backend.industrial.machines.compressor import Compressor

from backend.industrial.dependencies.dependency_engine import (
    DependencyEngine,
)


def test_tank_to_pump():
    """Test Tank → Pump dependency."""

    tank = Tank("TANK_001")
    pump = Pump("PUMP_001")

    pump.flow_rate = 75.0
    pump.pressure = 150.0

    tank.level_percentage = 10.0

    engine = DependencyEngine()

    engine.register_machine(tank)
    engine.register_machine(pump)

    engine.register_dependency(
        "TANK_001",
        "PUMP_001",
    )

    engine.update(1.0)

    assert pump.flow_rate == 37.5
    assert pump.pressure == 105.0

    print("✅ Tank → Pump dependency passed")


def test_pump_to_valve():
    """Test Pump → Valve dependency."""

    pump = Pump("PUMP_001")
    valve = Valve("VALVE_001")

    pump.flow_rate = 20.0

    valve.flow_rate = 100.0
    valve.pressure = 150.0

    engine = DependencyEngine()

    engine.register_machine(pump)
    engine.register_machine(valve)

    engine.register_dependency(
        "PUMP_001",
        "VALVE_001",
    )

    engine.update(1.0)

    assert valve.flow_rate == 60.0
    assert valve.pressure == 120.0

    print("✅ Pump → Valve dependency passed")


def test_valve_to_tank():
    """Test Valve → Tank dependency."""

    valve = Valve("VALVE_001")
    tank = Tank("TANK_001")

    valve.position = 10.0

    tank.outflow_rate = 40.0

    engine = DependencyEngine()

    engine.register_machine(valve)
    engine.register_machine(tank)

    engine.register_dependency(
        "VALVE_001",
        "TANK_001",
    )

    engine.update(1.0)

    assert tank.outflow_rate == 20.0

    print("✅ Valve → Tank dependency passed")


def test_motor_to_conveyor():
    """Test Motor → Conveyor dependency."""

    motor = Motor("MOTOR_001")
    conveyor = Conveyor("CONVEYOR_001")

    motor.load = 95.0

    conveyor.belt_speed = 2.5
    conveyor.rpm = 1500.0

    engine = DependencyEngine()

    engine.register_machine(motor)
    engine.register_machine(conveyor)

    engine.register_dependency(
        "MOTOR_001",
        "CONVEYOR_001",
    )

    engine.update(1.0)

    assert conveyor.belt_speed == 1.75
    assert conveyor.rpm == 1200.0

    print("✅ Motor → Conveyor dependency passed")


def test_compressor_to_valve():
    """Test Compressor → Valve dependency."""

    compressor = Compressor("COMPRESSOR_001")
    valve = Valve("VALVE_001")

    compressor.pressure = 100.0

    valve.position = 50.0

    engine = DependencyEngine()

    engine.register_machine(compressor)
    engine.register_machine(valve)

    engine.register_dependency(
        "COMPRESSOR_001",
        "VALVE_001",
    )

    engine.update(1.0)

    assert valve.position == 40.0

    print("✅ Compressor → Valve dependency passed")


def main():
    """Run all dependency tests."""

    print("=" * 60)
    print("LIGHTX-IDS MACHINE DEPENDENCY ENGINE TEST")
    print("=" * 60)

    test_tank_to_pump()
    test_pump_to_valve()
    test_valve_to_tank()
    test_motor_to_conveyor()
    test_compressor_to_valve()

    print("=" * 60)
    print("🎉 ALL MACHINE DEPENDENCY TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()