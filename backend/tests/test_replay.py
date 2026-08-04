"""
Test Replay Attack
"""

from backend.attacks.network.replay_attack import (
    ReplayAttack,
)


def main():

    attack = ReplayAttack()

    # ----------------------------------
    # Capture packets
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

    # ----------------------------------
    # Start replay
    # ----------------------------------

    attack.start()

    print("\nReplay Output")

    for _ in range(5):

        topic, payload = attack.modify_packet(
            "factory/temp",
            {"value": 100},
        )

        print(topic, payload)

    attack.stop()


if __name__ == "__main__":
    main()