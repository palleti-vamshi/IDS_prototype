# Weather Dataset — Cleaning & Standardization Report

## Original
- Rows: 39,260
- Columns: 7
- Nulls: none
- Duplicates: 0

## Cleaning
- Duplicates removed: 0
- Invalid label/type rows removed: 0
- Final row count: 39,260 (unchanged)

## Label distribution
- Attack (1): 24,260
- Normal (0): 15,000

## Attack type distribution
- normal: 15,000
- ddos: 5,000
- backdoor: 5,000
- injection: 5,000
- password: 5,000
- ransomware: 2,865
- xss: 866
- scanning: 529

## Notes
- Cleanest of the 4 files — no duplicates, no nulls, no rows dropped at any stage.
- Wider range of attack types than Modbus/Thermostat (includes ddos), giving more variety for training.
- scanning and xss remain comparatively small classes, consistent with the pattern seen across all TON-IoT IoT-device files.

## Standardization
- Mapped to LightX schema: sensor_reading_1 (temperature), sensor_reading_2 (pressure), sensor_reading_3 (humidity), label, attack_type, timestamp
- Final file: datasets/standardized/weather_final.csv (39,260 rows, 7 columns)