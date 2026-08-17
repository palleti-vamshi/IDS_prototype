from __future__ import annotations

from typing import Any

from backend.dataset.dataset_schema import DatasetRecord


class DatasetCollector:
    """
    Collects sensor telemetry together with the actual
    cyber-attack state at the time of the reading.
    """

    def __init__(self) -> None:
        self.records: list[DatasetRecord] = []

    def collect(
        self,
        sensor_packet: dict,
        attack: Any = None,
    ) -> DatasetRecord:
        """
        Create one labelled dataset record.

        sensor_packet comes from the existing sensor
        create_packet() method.

        attack is the actual running BaseAttack object,
        if one is active.
        """

        attack_active = (
            attack is not None
            and attack.is_running
        )

        if attack_active:
            attack_id = attack.attack_id
            attack_name = attack.attack_name
            attack_type = attack.attack_type.value
            attack_target = attack.attack_target.value
            attack_state = attack.state.value

        else:
            attack_id = None
            attack_name = None
            attack_type = None
            attack_target = None
            attack_state = None

        record = DatasetRecord(
            timestamp=sensor_packet["timestamp"],

            sensor_code=sensor_packet["sensor_code"],
            device_id=sensor_packet["device_id"],
            sensor_type=sensor_packet["sensor_type"],
            value=float(sensor_packet["value"]),
            unit=sensor_packet["unit"],
            status=sensor_packet["status"],
            health=float(sensor_packet["health"]),

            attack_active=attack_active,
            attack_id=attack_id,
            attack_name=attack_name,
            attack_type=attack_type,
            attack_target=attack_target,
            attack_state=attack_state,
        )

        self.records.append(record)

        return record

    def get_records(self) -> list[dict]:
        """
        Return all collected records as dictionaries.
        """

        return [
            record.to_dict()
            for record in self.records
        ]

    @property
    def total_records(self) -> int:
        return len(self.records)

    def clear(self) -> None:
        """
        Remove all collected records.
        """

        self.records.clear()