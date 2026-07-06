from backend.preprocessing.schemas import ParsedSensorRecord
from backend.preprocessing.labeler import Labeler

record = ParsedSensorRecord(
    timestamp="2026-07-06T17:43:22",
    topic="factory/line1/temperature",
    device_id="temperature_sensor_01",
    sensor_type="temperature",
    value=28.3,
    unit="°C",
    status="NORMAL",
)

labeler = Labeler()

result = labeler.label(record)

print(result)