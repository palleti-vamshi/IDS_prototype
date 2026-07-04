"""
MQTT Configuration for LightX-IDS
"""

# Broker Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

# MQTT Topics
TEMPERATURE_TOPIC = "factory/line1/temperature"
PRESSURE_TOPIC = "factory/line1/pressure"
PLC_TOPIC = "factory/line1/plc"
ALERT_TOPIC = "factory/alerts"

# MQTT Client IDs
TEMP_SENSOR_CLIENT = "temperature_sensor"
PRESSURE_SENSOR_CLIENT = "pressure_sensor"
PLC_CLIENT = "plc_controller"
SCADA_CLIENT = "scada_dashboard"