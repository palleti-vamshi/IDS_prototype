# Thermostat Dataset — Cleaning & Standardization Report

## Original
- Rows: 32,774
- Columns: 6
- Nulls: none

## Cleaning
- Duplicates removed: 424 (1.3% of rows)
- Invalid label/type rows removed: 0
- Final row count: 32,350

## Label distribution (before cleaning)
- Attack (1): 17,774
- Normal (0): 15,000

## Attack type distribution
- normal: 15,000
- injection: 5,000
- backdoor: 5,000
- password: 5,000
- ransomware: 2,264
- xss: 449
- scanning: 61

## Notes
- Very few duplicates compared to Modbus — sensor readings vary enough between polls that exact duplicates are rare.
- scanning is a very small class (61 rows out of 32,774) — flagged as a potential weak spot for the ML team; may need oversampling or should be evaluated with caution.

## Standardization
- Mapped to LightX schema: sensor_reading_1 (current_temperature), sensor_reading_2 (thermostat_status), label, attack_type, timestamp
- Final file: datasets/standardized/thermostat_final.csv (32,350 rows, 6 columns)