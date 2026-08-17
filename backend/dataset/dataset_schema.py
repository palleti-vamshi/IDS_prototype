from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class DatasetRecord:
    timestamp: str

    sensor_code: str
    device_id: str
    sensor_type: str
    value: float
    unit: str
    status: str
    health: float

    attack_active: bool
    attack_id: Optional[str]
    attack_name: Optional[str]
    attack_type: Optional[str]
    attack_target: Optional[str]
    attack_state: Optional[str]

    def to_dict(self) -> dict:
        return asdict(self)