"""
Factory Simulator Integration Test
"""

from backend.industrial.simulator.factory_simulator import (
    FactorySimulator,
)


def print_header(title: str):

    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70)


def main():

    print_header(
        "LIGHTX-IDS FACTORY SIMULATOR TEST"
    )

    simulator = FactorySimulator()

    print("\nInitializing simulator...\n")

    simulator.initialize()

    # ==================================================
    # Factory
    # ==================================================

    print_header("FACTORY")

    print(simulator.factory.get_status())

    # ==================================================
    # Production Line
    # ==================================================

    print_header("PRODUCTION LINE")

    print(simulator.production_line.get_status())

    # ==================================================
    # Machines
    # ==================================================

    print_header("MACHINES")

    for machine in simulator.machines:

        print(machine.get_status())

    # ==================================================
    # Sensors
    # ==================================================

    print_header("SENSORS")

    for sensor in simulator.sensors:

        print(sensor.get_status())

    # ==================================================
    # Behaviors
    # ==================================================

    print_header("BEHAVIOR ENGINE")

    print(
        simulator.behavior_engine.get_status()
    )

    # ==================================================
    # Clock
    # ==================================================

    print_header("SIMULATION CLOCK")

    print(
        simulator.clock.get_status()
    )

    # ==================================================
    # Execute One Tick
    # ==================================================

    print_header(
        "EXECUTING ONE SIMULATION STEP"
    )

    simulator.clock.start()

    simulator.simulation_step()

    simulator.publish_cycle()

    simulator.clock.stop()

    # ==================================================
    # Final Status
    # ==================================================

    print_header(
        "SIMULATOR STATUS"
    )

    print(
        simulator.get_status()
    )

    print_header(
        "FACTORY SIMULATOR TEST PASSED"
    )


if __name__ == "__main__":
    main()