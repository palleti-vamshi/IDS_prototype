"""
Test Replay Attack
"""

from backend.attacks.network.network_state import NetworkState
from backend.attacks.network.replay_attack import (
    ReplayAttack,
)
from backend.industrial.communication.communication_controller import (
    CommunicationController,
)
from backend.industrial.communication.packet_buffer import PacketBuffer


def main():

    attack = ReplayAttack()

    # ----------------------------------
    # Capture packets (standalone)
    # ----------------------------------

    attack.capture_packet(
        "factory/temp",
        {"value": 25},
    )

    attack.capture_packet(
        "factory/temp",
        {"value": 26},
    )

    attack.capture_packet(
        "factory/temp",
        {"value": 27},
    )

    print("\nCaptured Packets")

    for packet in attack.packet_buffer:
        print(packet)

    assert len(attack.packet_buffer) == 3

    # ----------------------------------
    # Start replay (standalone)
    # ----------------------------------

    attack.start()
    attack.update(1.0)
    assert attack.is_running
    assert NetworkState.replay_enabled

    print("\nReplay Output")

    for _ in range(5):

        topic, payload = attack.modify_packet(
            "factory/temp",
            {"value": 100},
        )

        print(topic, payload)
        assert payload["value"] in [25, 26, 27]

    attack.stop()
    assert not attack.is_running
    assert not NetworkState.replay_enabled

    # ----------------------------------
    # Integrated CommunicationController test
    # ----------------------------------

    comm = CommunicationController()
    comm.set_packet_buffer(PacketBuffer())
    attack.set_communication(comm)
    attack.capture_packet("factory/pressure", {"value": 101.3})
    attack.start()
    attack.update(1.0)

    _, payload = attack.modify_packet(
        "factory/pressure",
        {"value": 999.0},
    )
    assert payload["value"] == 101.3
    assert attack.replayed_packets == 1

    attack.stop()
    assert not attack.is_running
    assert not NetworkState.replay_enabled

    print("\n✅ All replay tests passed.")


if __name__ == "__main__":
    main()