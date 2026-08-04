"""
network_state.py

Global network state shared between
network attacks and the simulator.
"""


class NetworkState:
    """
    Shared communication state used by all
    network attacks.
    """

    # ==========================================
    # Network Delay
    # ==========================================

    delay = 0.0

    # ==========================================
    # Packet Loss
    # ==========================================

    packet_loss = 0.0

    # ==========================================
    # DoS Flood
    # ==========================================

    flood = False

    # ==========================================
    # MQTT Topic Hijacking
    # ==========================================

    hijacked_topic = None

    # ==========================================
    # Replay
    # ==========================================

    replay_enabled = False

    # ==========================================
    # Reset
    # ==========================================

    @classmethod
    def reset(cls):

        cls.delay = 0.0

        cls.packet_loss = 0.0

        cls.flood = False

        cls.hijacked_topic = None

        cls.replay_enabled = False