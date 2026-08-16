"""
packet_buffer.py

Stores recently transmitted MQTT packets for
replay attacks and network analysis.
"""

from __future__ import annotations

from collections import deque
from copy import deepcopy


class PacketBuffer:
    """
    Circular packet buffer.

    Features
    --------
    • Fixed capacity
    • FIFO storage
    • Replay support
    """

    def __init__(
        self,
        capacity: int = 1000,
    ) -> None:

        self.capacity = capacity

        self.buffer = deque(
            maxlen=capacity
        )

    # ==================================================
    # Store Packet
    # ==================================================

    def add_packet(
        self,
        topic: str,
        payload,
    ) -> None:

        self.buffer.append(

            {
                "topic": topic,
                "payload": deepcopy(payload),
            }

        )

    # ==================================================
    # Replay
    # ==================================================

    def get_latest(
        self,
        count: int = 1,
    ) -> list:

        count = min(
            count,
            len(self.buffer),
        )

        return list(self.buffer)[-count:]

    def get_all(self) -> list:

        return list(self.buffer)

    # ==================================================
    # Utility
    # ==================================================

    def clear(self) -> None:

        self.buffer.clear()

    @property
    def size(self) -> int:

        return len(self.buffer)

    def __len__(self):

        return len(self.buffer)

    def __str__(self):

        return (
            f"PacketBuffer("
            f"{len(self.buffer)}/"
            f"{self.capacity})"
        )