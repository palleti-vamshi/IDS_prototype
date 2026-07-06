from backend.preprocessing.schemas import RawMQTTMessage
from backend.preprocessing.parser import MessageParser

raw = RawMQTTMessage(
    timestamp="2026-07-06T17:43:22",
    topic="factory/line1/temperature",
    payload='{"device_id":"temperature_sensor_01","timestamp":"2026-07-06T17:43:22","sensor_type":"temperature","value":28.3,"unit":"°C","status":"NORMAL"}',
    qos=0,
    retain=False,
)

parsed = MessageParser.parse(raw)

print(parsed)