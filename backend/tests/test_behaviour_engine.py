"""
Complete Behavior Engine Integration Test
"""

import time

from backend.industrial.behavior.behavior_engine import BehaviorEngine
from backend.industrial.behavior.state_models import BehaviorState

from backend.industrial.machines import (
    Motor,
    Pump,
    Tank,
    Conveyor,
    Valve,
    Compressor,
)


def print_header(title: str):

    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)


def print_states(machines, engine):

    print(
        f"{'Machine':<10}"
        f"{'Behavior':<15}"
        f"{'Machine State':<15}"
    )

    print("-" * 45)

    for machine in machines:

        behavior = engine.get_behavior(
            machine.machine_code
        )

        print(
            f"{machine.machine_code:<10}"
            f"{behavior.state.value:<15}"
            f"{machine.state.value:<15}"
        )


def main():

    print_header(
        "LIGHTX-IDS INDUSTRIAL BEHAVIOR ENGINE TEST"
    )

    machines = [

        Motor("MTR-001"),

        Pump("PMP-001"),

        Tank("TNK-001"),

        Conveyor("CNV-001"),

        Valve("VLV-001"),

        Compressor("CMP-001"),
    ]

    engine = BehaviorEngine()

    # ==========================================
    # Register
    # ==========================================

    print("\nRegistering Machines...\n")

    for machine in machines:

        engine.register_machine(machine)

        behavior = engine.get_behavior(
            machine.machine_code
        )

        behavior.set_state(
            BehaviorState.STARTING
        )

        print(
            f"✓ {machine.machine_code:<8}"
            f"{behavior.__class__.__name__}"
        )

    # ==========================================
    # STARTUP
    # ==========================================

    print_header("STARTUP")

    for second in range(15):

        engine.update(1)

        print(f"\nTime = {second+1}s")

        print_states(
            machines,
            engine,
        )

        time.sleep(1)

    # ==========================================
    # HIGH LOAD
    # ==========================================

    print_header("HIGH LOAD")

    for machine in machines:

        engine.get_behavior(
            machine.machine_code
        ).set_state(
            BehaviorState.HIGH_LOAD
        )

    for second in range(10):

        engine.update(1)

        print(f"\nTime = {second+1}s")

        print_states(
            machines,
            engine,
        )

        time.sleep(1)

    # ==========================================
    # FAULT
    # ==========================================

    print_header("FAULT")

    for machine in machines:

        engine.get_behavior(
            machine.machine_code
        ).set_state(
            BehaviorState.FAULT
        )

    for second in range(10):

        engine.update(1)

        print(f"\nTime = {second+1}s")

        print_states(
            machines,
            engine,
        )

        time.sleep(1)

    # ==========================================
    # Final Telemetry
    # ==========================================

    print_header("FINAL TELEMETRY")

    for machine in machines:

        print()

        print(machine.machine_code)

        print("-" * 40)

        telemetry = machine.get_telemetry()

        for key, value in telemetry.items():

            print(
                f"{key:<20}: {value}"
            )

    print_header(
        "ALL BEHAVIOR ENGINE TESTS PASSED"
    )


if __name__ == "__main__":
    main()