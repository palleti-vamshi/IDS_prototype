"""
Attack Scheduler

Purpose:
    Schedules attacks during simulation.
"""

import time

from backend.core.logger import setup_logger


class AttackScheduler:
    """Controls when attacks are executed."""

    def __init__(self):
        self.logger = setup_logger("Attack Scheduler")

    def wait(self, seconds: int):
        """
        Wait before executing the next attack.
        """
        self.logger.info(
            f"Waiting {seconds} seconds before next attack..."
        )

        time.sleep(seconds)