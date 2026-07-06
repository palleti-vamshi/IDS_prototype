"""
Dynamic Attack Runner

Runs randomized attack scenarios until the target dataset size is reached.
"""

import random
import time

from backend.attacks.attack_manager import AttackManager
from backend.attacks.dos_attack import DoSAttack
from backend.attacks.replay_attack import ReplayAttack
from backend.attacks.injection_attack import InjectionAttack
from backend.attacks.spoofing_attack import SpoofingAttack

from backend.preprocessing.generation_config import (
    TARGET_RECORDS,
    MIN_NORMAL_DURATION,
    MAX_NORMAL_DURATION,
    MIN_ATTACK_DURATION,
    MAX_ATTACK_DURATION,
    MIN_COOLDOWN,
    MAX_COOLDOWN,
    ATTACK_WEIGHTS,
)


ATTACKS = {
    "DoS": DoSAttack,
    "Replay": ReplayAttack,
    "Injection": InjectionAttack,
    "Spoofing": SpoofingAttack,
}


class AttackRunner:
    """Runs randomized attack scenarios."""

    def __init__(self, dataset_manager):
        self.dataset_manager = dataset_manager

    def run(self):

        print("\n🚀 Dynamic Dataset Generation Started\n")

        while self.dataset_manager.writer.record_count() < TARGET_RECORDS:

            current = self.dataset_manager.writer.record_count()

            print(
                f"\n📊 Progress: {current:,}/{TARGET_RECORDS:,} records"
            )

            # -----------------------------
            # Random normal traffic
            # -----------------------------
            normal_time = random.randint(
                MIN_NORMAL_DURATION,
                MAX_NORMAL_DURATION,
            )

            print(f"\n🟢 Normal Traffic ({normal_time}s)")
            time.sleep(normal_time)

            # -----------------------------
            # Random attack
            # -----------------------------
            attack_name = random.choices(
                population=list(ATTACKS.keys()),
                weights=list(ATTACK_WEIGHTS.values()),
                k=1,
            )[0]

            attack = ATTACKS[attack_name]()

            attack.duration = random.randint(
                MIN_ATTACK_DURATION,
                MAX_ATTACK_DURATION,
            )

            print(
                f"\n🚨 {attack.attack_name} "
                f"({attack.duration}s)"
            )

            manager = AttackManager()
            manager.register_attack(attack)
            manager.start()

            while any(thread.is_alive() for thread in manager.threads):
                time.sleep(1)

            # -----------------------------
            # Random cooldown
            # -----------------------------
            cooldown = random.randint(
                MIN_COOLDOWN,
                MAX_COOLDOWN,
            )

            print(f"\n⏳ Cooldown ({cooldown}s)")
            time.sleep(cooldown)

        print("\n🎉 Target Dataset Size Reached!")