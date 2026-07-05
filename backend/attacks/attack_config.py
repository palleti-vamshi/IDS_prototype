"""
Attack Configuration for LightX-IDS
"""

# ==========================================
# MQTT Topics
# ==========================================

FACTORY_LINE = 1

TEMPERATURE_TOPIC = f"factory/line{FACTORY_LINE}/temperature"

PRESSURE_TOPIC = f"factory/line{FACTORY_LINE}/pressure"

# ==========================================
# MQTT Client IDs
# ==========================================

DOS_ATTACK_CLIENT = "dos_attack"

REPLAY_ATTACK_CLIENT = "replay_attack"

SPOOFING_ATTACK_CLIENT = "spoofing_attack"

INJECTION_ATTACK_CLIENT = "injection_attack"


# ==========================================
# DoS Attack Configuration
# ==========================================

DOS_PACKET_INTERVAL = 0.01
DOS_ATTACK_DURATION = 30


# ==========================================
# Replay Attack Configuration
# ==========================================

REPLAY_PACKET_INTERVAL = 0.5
REPLAY_ATTACK_DURATION = 30


# ==========================================
# Spoofing Attack Configuration
# ==========================================

SPOOFING_PACKET_INTERVAL = 0.5
SPOOFING_ATTACK_DURATION = 30


# ==========================================
# Data Injection Attack Configuration
# ==========================================

INJECTION_PACKET_INTERVAL = 0.5
INJECTION_ATTACK_DURATION = 30


# ==========================================
# Fake Device IDs
# ==========================================

FAKE_TEMPERATURE_SENSOR = "fake_temperature_sensor"
FAKE_PRESSURE_SENSOR = "fake_pressure_sensor"


# ==========================================
# Attack Status Labels
# ==========================================

DOS_STATUS = "DOS"
REPLAY_STATUS = "REPLAY"
SPOOFING_STATUS = "SPOOFING"
INJECTION_STATUS = "INJECTION"