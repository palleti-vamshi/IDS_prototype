"""
Preprocessing pipeline for LightX-IDS.
"""

from backend.preprocessing.collector import MQTTCollector
from backend.preprocessing.dataset_manager import DatasetManager


class DatasetPipeline:
    """Connects the collector with the dataset manager."""

    def __init__(self):
        self.manager = DatasetManager()

        self.collector = MQTTCollector(
            message_callback=self.manager.process_message
        )

    def start(self):
        """Start the preprocessing pipeline."""
        self.collector.connect()
        self.collector.start()

    def stop(self):
        """Stop the preprocessing pipeline."""
        self.collector.stop()