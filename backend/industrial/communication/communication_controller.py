"""
communication_controller.py

Simulates Industrial IIoT communication behaviour.

All network attacks modify this controller instead of
implementing networking logic themselves.
"""

from __future__ import annotations


class CommunicationController:
    """
    Controls the simulated communication channel.

    Features
    --------
    • Communication delay
    • Packet loss
    • Packet duplication
    • Communication freeze
    • Network congestion
    """

    def __init__(self) -> None:

        # Seconds of artificial delay
        self.delay = 0.0

        # Packet loss percentage
        self.packet_loss = 0.0

        # Packet duplication percentage
        self.packet_duplicate = 0.0

        # Freeze communication
        self.freeze = False

        # Network congestion level (0-100)
        self.congestion = 0.0

        # Enable / Disable controller
        self.enabled = True

    # ==================================================
    # Reset
    # ==================================================

    def reset(self) -> None:
        """
        Restore normal communication.
        """

        self.delay = 0.0
        self.packet_loss = 0.0
        self.packet_duplicate = 0.0
        self.freeze = False
        self.congestion = 0.0

    # ==================================================
    # Delay
    # ==================================================

    def set_delay(
        self,
        seconds: float,
    ) -> None:

        self.delay = max(0.0, seconds)

    # ==================================================
    # Packet Loss
    # ==================================================

    def set_packet_loss(
        self,
        percentage: float,
    ) -> None:

        self.packet_loss = max(
            0.0,
            min(100.0, percentage),
        )

    # ==================================================
    # Packet Duplication
    # ==================================================

    def set_packet_duplicate(
        self,
        percentage: float,
    ) -> None:

        self.packet_duplicate = max(
            0.0,
            min(100.0, percentage),
        )

    # ==================================================
    # Congestion
    # ==================================================

    def set_congestion(
        self,
        percentage: float,
    ) -> None:

        self.congestion = max(
            0.0,
            min(100.0, percentage),
        )

    # ==================================================
    # Freeze
    # ==================================================

    def enable_freeze(self) -> None:

        self.freeze = True

    def disable_freeze(self) -> None:

        self.freeze = False

    # ==================================================
    # Status
    # ==================================================

    def get_status(self) -> dict:

        return {

            "enabled": self.enabled,

            "delay": self.delay,

            "packet_loss": self.packet_loss,

            "packet_duplicate": self.packet_duplicate,

            "freeze": self.freeze,

            "congestion": self.congestion,
        }

    def __str__(self) -> str:

        return (
            "CommunicationController("
            f"delay={self.delay}, "
            f"loss={self.packet_loss}%, "
            f"duplicate={self.packet_duplicate}%, "
            f"freeze={self.freeze}, "
            f"congestion={self.congestion}%)"
        )