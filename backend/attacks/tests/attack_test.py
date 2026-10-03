"""
Attack Framework Integration Test

Purpose:
    Tests representative attack modules individually using the AttackManager.
"""

from backend.attacks.attack_manager import AttackManager
from backend.attacks.network.dos_attack import DoSAttack
from backend.attacks.network.replay_attack import ReplayAttack
from backend.attacks.sensor.sensor_spoofing_attack import SensorSpoofingAttack
from backend.attacks.sensor.false_data_injection_attack import (
    FalseDataInjectionAttack,
)


def run_attack(attack):
    """Run a single attack using the AttackManager."""

    manager = AttackManager()

    manager.register_attack(attack)

    started = manager.start_attack(attack.attack_id)
    assert started, f"Failed to start {attack.attack_name}"
    assert attack.is_running

    while attack.is_running:
        manager.update(1.0)

    manager.stop_all()
    assert not attack.is_running

    print(f"\n✅ {attack.attack_name} Test Passed\n")


def main():
    print("=" * 60)
    print("LightX-IDS Attack Framework Integration Test")
    print("=" * 60)

    run_attack(DoSAttack(duration=3.0))
    run_attack(ReplayAttack(duration=3.0))
    run_attack(SensorSpoofingAttack(duration=3.0))
    run_attack(FalseDataInjectionAttack(duration=3.0))

    print("=" * 60)
    print("🎉 ALL ATTACK TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()