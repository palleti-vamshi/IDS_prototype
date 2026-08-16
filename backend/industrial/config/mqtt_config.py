"""
MQTT Configuration for LightX-IDS
"""

# ==========================================================
# Broker Configuration
# ==========================================================

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60


# ==========================================================
# Sensor Topics
# ==========================================================

TEMPERATURE_TOPIC = "factory/line1/temperature"
PRESSURE_TOPIC = "factory/line1/pressure"
CURRENT_TOPIC = "factory/line1/current"
VOLTAGE_TOPIC = "factory/line1/voltage"
FLOW_TOPIC = "factory/line1/flow"
RPM_TOPIC = "factory/line1/rpm"
VIBRATION_TOPIC = "factory/line1/vibration"
HUMIDITY_TOPIC = "factory/line1/humidity"
LEVEL_TOPIC = "factory/line1/level"
PROXIMITY_TOPIC = "factory/line1/proximity"


# ==========================================================
# Industrial Topics
# ==========================================================

PLC_TOPIC = "factory/line1/plc"
ALERT_TOPIC = "factory/alerts"
ATTACK_STATE_TOPIC = "factory/attacks/state"

# Machine status topic
MACHINE_STATUS_TOPIC = "factory/line1/machines"


# ==========================================================
# Dataset Collection Topics
# ==========================================================

MQTT_TOPICS = [
    TEMPERATURE_TOPIC,
    PRESSURE_TOPIC,
    CURRENT_TOPIC,
    VOLTAGE_TOPIC,
    FLOW_TOPIC,
    RPM_TOPIC,
    VIBRATION_TOPIC,
    HUMIDITY_TOPIC,
    LEVEL_TOPIC,
    PROXIMITY_TOPIC,
    PLC_TOPIC,
    ALERT_TOPIC,
    ATTACK_STATE_TOPIC,
    MACHINE_STATUS_TOPIC,
]


# ==========================================================
# MQTT Client IDs
# ==========================================================

TEMP_SENSOR_CLIENT = "temperature_sensor"
PRESSURE_SENSOR_CLIENT = "pressure_sensor"
CURRENT_SENSOR_CLIENT = "current_sensor"
VOLTAGE_SENSOR_CLIENT = "voltage_sensor"
FLOW_SENSOR_CLIENT = "flow_sensor"
RPM_SENSOR_CLIENT = "rpm_sensor"
VIBRATION_SENSOR_CLIENT = "vibration_sensor"
HUMIDITY_SENSOR_CLIENT = "humidity_sensor"
LEVEL_SENSOR_CLIENT = "level_sensor"
PROXIMITY_SENSOR_CLIENT = "proximity_sensor"

PLC_CLIENT = "plc_controller"
SCADA_CLIENT = "scada_dashboard"
COLLECTOR_CLIENT = "dataset_collector"