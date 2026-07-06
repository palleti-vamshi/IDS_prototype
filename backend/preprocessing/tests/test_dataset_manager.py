from backend.preprocessing.dataset_manager import DatasetManager
from backend.preprocessing.schemas import RawMQTTMessage

manager = DatasetManager()

raw = RawMQTTMessage(
    timestamp="2026-07-06T17:43:22",
    topic="factory/line1/temperature",
    payload='{"device_id":"temperature_sensor_01","timestamp":"2026-07-06T17:43:22","sensor_type":"temperature","value":28.3,"unit":"°C","status":"NORMAL"}',
    qos=0,
    retain=False,
)

manager.process_message(raw)

manager.export_dataset(
    "backend/datasets/lightx_dataset.csv"
)

print("Dataset Manager Test Passed")