"""
Preprocessing pipeline for LightX-IDS.
"""

import threading

from backend.preprocessing.collector import MQTTCollector
from backend.preprocessing.dataset_manager import DatasetManager


class DatasetPipeline:
    """Connects the collector with the dataset manager."""

    def __init__(self):
        self.manager = DatasetManager()

        self.collector = MQTTCollector(
            message_callback=self.manager.process_message
        )

        self.thread = None

    def start(self):
        """Start the preprocessing pipeline."""

        self.collector.connect()

        self.thread = threading.Thread(
            target=self.collector.start,
            daemon=True,
        )

        self.thread.start()

        print("📊 Dataset Pipeline Started")

    def stop(self):
        """Stop the preprocessing pipeline."""

        self.collector.stop()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        print("🛑 Dataset Pipeline Stopped")