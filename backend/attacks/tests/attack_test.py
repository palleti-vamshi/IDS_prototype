"""
Attack Framework Integration Test

Purpose:
    Tests all attack modules individually using the AttackManager.
"""

import time

from backend.attacks.attack_manager import AttackManager
from backend.attacks.dos_attack import DoSAttack
from backend.attacks.replay_attack import ReplayAttack
from backend.attacks.spoofing_attack import SpoofingAttack
from backend.attacks.injection_attack import InjectionAttack


def run_attack(attack):
    """Run a single attack using the AttackManager."""

    manager = AttackManager()

    manager.register_attack(attack)

    manager.start()

    while any(thread.is_alive() for thread in manager.threads):
        time.sleep(1)

    print(f"\n✅ {attack.attack_name} Test Passed\n")


def main():
    print("=" * 60)
    print("LightX-IDS Attack Framework Integration Test")
    print("=" * 60)

    run_attack(DoSAttack())
    run_attack(ReplayAttack())
    run_attack(SpoofingAttack())
    run_attack(InjectionAttack())

    print("=" * 60)
    print("🎉 ALL ATTACK TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()