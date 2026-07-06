"""
Base Attack Module

Purpose:
    Provides the common functionality for all cyber attacks.
"""

import time
from abc import ABC, abstractmethod

from backend.core.logger import setup_logger
from backend.industrial.mqtt.publisher import MQTTPublisher
from backend.attacks.event_publisher import AttackEventPublisher


class BaseAttack(ABC):
    """Base class for all attack modules."""

    def __init__(
        self,
        attack_name: str,
        client_id: str,
        interval: float = 1.0,
        duration: int = 30,
    ):
        self.attack_name = attack_name
        self.interval = interval
        self.duration = duration

        self.logger = setup_logger(attack_name)

        self.publisher = MQTTPublisher(client_id)

        # NEW
        self.event_publisher = AttackEventPublisher()

        self.running = False

    @abstractmethod
    def execute(self):
        """Execute one attack iteration."""
        pass

    def start(self):
        """Start the attack."""

        self.running = True

        # Publish attack start event
        self.event_publisher.publish_start(self.attack_name)

        self.logger.info(f"{self.attack_name} started.")

        start_time = time.time()

        while self.running:

            elapsed = time.time() - start_time

            if elapsed >= self.duration:
                break

            self.execute()
            time.sleep(self.interval)

        self.stop()

    def stop(self):
        """Stop the attack."""

        self.running = False

        # Publish attack stop event
        self.event_publisher.publish_stop(self.attack_name)

        self.publisher.disconnect()

        self.logger.info(f"{self.attack_name} stopped.")