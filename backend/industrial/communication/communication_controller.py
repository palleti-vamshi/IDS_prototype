"""
communication_controller.py

Central communication engine for the
LightX-IDS Industrial IIoT network.
"""

from __future__ import annotations


class CommunicationController:
    """
    Controls the simulated IIoT communication layer.

    Features
    --------
    • Communication delay
    • Packet loss
    • Packet duplication
    • Communication freeze
    • Network congestion
    • Packet buffering
    • Packet queuing
    • Traffic statistics
    """

    def __init__(self) -> None:

        # ==========================================
        # Network Effects
        # ==========================================

        self.delay = 0.0

        self.packet_loss = 0.0

        self.packet_duplicate = 0.0

        self.freeze = False

        self.congestion = 0.0

        self.enabled = True

        # ==========================================
        # Phase 3 Components
        # ==========================================

        self.packet_buffer = None

        self.packet_queue = None

        self.statistics = None

    # ==================================================
    # Component Registration
    # ==================================================

    def set_packet_buffer(
        self,
        buffer,
    ) -> None:

        self.packet_buffer = buffer

    def set_packet_queue(
        self,
        queue,
    ) -> None:

        self.packet_queue = queue

    def set_statistics(
        self,
        statistics,
    ) -> None:

        self.statistics = statistics

    # ==================================================
    # Reset
    # ==================================================

    def reset(self) -> None:

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

        self.delay = max(
            0.0,
            seconds,
        )

    # ==================================================
    # Packet Loss
    # ==================================================

    def set_packet_loss(
        self,
        percentage: float,
    ) -> None:

        self.packet_loss = max(
            0.0,
            min(
                100.0,
                percentage,
            ),
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
            min(
                100.0,
                percentage,
            ),
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
            min(
                100.0,
                percentage,
            ),
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

    def get_status(
        self,
    ) -> dict:

        return {

            "enabled": self.enabled,

            "delay": self.delay,

            "packet_loss": self.packet_loss,

            "packet_duplicate": self.packet_duplicate,

            "freeze": self.freeze,

            "congestion": self.congestion,

            "packet_buffer": (
                self.packet_buffer is not None
            ),

            "packet_queue": (
                self.packet_queue is not None
            ),

            "statistics": (
                self.statistics is not None
            ),
        }

    def __str__(
        self,
    ) -> str:

        return (
            "CommunicationController("
            f"delay={self.delay}, "
            f"loss={self.packet_loss}%, "
            f"duplicate={self.packet_duplicate}%, "
            f"freeze={self.freeze}, "
            f"congestion={self.congestion}%)"
        )