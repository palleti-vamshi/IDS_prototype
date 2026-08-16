"""
traffic_statistics.py

Collects communication statistics for the
Industrial IIoT network.
"""

from __future__ import annotations


class TrafficStatistics:
    """
    Tracks communication metrics.

    Features
    --------
    • Packets sent
    • Packets dropped
    • Packets delayed
    • Packets replayed
    • Packets duplicated
    """

    def __init__(self) -> None:

        self.reset()

    # ==================================================
    # Counters
    # ==================================================

    def packet_sent(self) -> None:

        self.packets_sent += 1

    def packet_dropped(self) -> None:

        self.packets_dropped += 1

    def packet_delayed(self) -> None:

        self.packets_delayed += 1

    def packet_replayed(self) -> None:

        self.packets_replayed += 1

    def packet_duplicated(self) -> None:

        self.packets_duplicated += 1

    # ==================================================
    # Reset
    # ==================================================

    def reset(self) -> None:

        self.packets_sent = 0

        self.packets_dropped = 0

        self.packets_delayed = 0

        self.packets_replayed = 0

        self.packets_duplicated = 0

    # ==================================================
    # Status
    # ==================================================

    def get_status(self) -> dict:

        return {

            "packets_sent":
                self.packets_sent,

            "packets_dropped":
                self.packets_dropped,

            "packets_delayed":
                self.packets_delayed,

            "packets_replayed":
                self.packets_replayed,

            "packets_duplicated":
                self.packets_duplicated,
        }

    def __str__(self) -> str:

        return (

            "TrafficStatistics("

            f"sent={self.packets_sent}, "

            f"dropped={self.packets_dropped}, "

            f"delayed={self.packets_delayed}, "

            f"replayed={self.packets_replayed}, "

            f"duplicated={self.packets_duplicated})"

        )