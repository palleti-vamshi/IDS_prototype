"""
packet_queue.py

Packet queue for simulating network latency,
congestion, and delayed transmission.
"""

from __future__ import annotations

from collections import deque


class PacketQueue:
    """
    FIFO packet queue.

    Features
    --------
    • Queue packets
    • Release packets
    • Queue size monitoring
    """

    def __init__(self) -> None:

        self.queue = deque()

    # ==================================================
    # Queue Packet
    # ==================================================

    def enqueue(
        self,
        packet,
    ) -> None:

        self.queue.append(packet)

    # ==================================================
    # Release Packet
    # ==================================================

    def dequeue(self):

        if self.queue:

            return self.queue.popleft()

        return None

    # ==================================================
    # Peek
    # ==================================================

    def peek(self):

        if self.queue:

            return self.queue[0]

        return None

    # ==================================================
    # Utility
    # ==================================================

    def clear(self) -> None:

        self.queue.clear()

    @property
    def size(self) -> int:

        return len(self.queue)

    def is_empty(self) -> bool:

        return len(self.queue) == 0

    def __len__(self):

        return len(self.queue)

    def __str__(self):

        return (
            f"PacketQueue("
            f"{len(self.queue)} packets)"
        )