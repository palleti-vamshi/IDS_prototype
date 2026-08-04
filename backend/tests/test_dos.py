from backend.attacks.attack_manager import AttackManager
from backend.attacks.network.dos_attack import DoSAttack

manager = AttackManager()

attack = DoSAttack(duration=10)

manager.register_attack(attack)

print("Registered:", manager.get_status())

manager.start_attack(attack.attack_id)

for i in range(12):

    print(f"\nTick {i}")

    manager.update(1)

    print(attack.get_status())

manager.stop_all()

print("\nFinal Status")

print(manager.get_status())