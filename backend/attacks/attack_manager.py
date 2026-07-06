"""
Attack Manager

Purpose:
    Starts and manages cyber attack modules.
"""

import threading

from backend.core.logger import setup_logger


class AttackManager:
    """Coordinates all attack modules."""

    def __init__(self):
        self.logger = setup_logger("Attack Manager")
        self.attacks = []
        self.threads = []

        self.current_attack = None
        self.attack_active = False

    def register_attack(self, attack):
        """Register an attack module."""
        self.attacks.append(attack)

        self.logger.info(
            f"Registered attack: {attack.attack_name}"
        )

    def set_active_attack(self, attack_name: str):
        """Set the currently active attack."""
        self.current_attack = attack_name
        self.attack_active = True


    def clear_active_attack(self):
        """Clear the active attack."""
        self.current_attack = None
        self.attack_active = False


    def get_attack_state(self):
        """Return current attack state."""
        return self.attack_active, self.current_attack

    def start(self):
        """Start all registered attacks."""

        self.logger.info("Starting Attack Manager...")

        for attack in self.attacks:

            thread = threading.Thread(
                target=attack.start,
                daemon=True,
            )

            thread.start()
            self.threads.append(thread)

        self.logger.info("All attacks started.")

    def stop(self):
        """Stop all attacks."""

        self.logger.info("Stopping Attack Manager...")

        for attack in self.attacks:
            attack.stop()

        self.logger.info("All attacks stopped.")