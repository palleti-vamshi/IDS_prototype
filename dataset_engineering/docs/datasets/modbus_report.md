# Modbus Dataset — Cleaning & Standardization Report

## Original
- Rows: 31,106
- Columns: 8
- Nulls: none

## Cleaning
- Duplicates removed: 13,314 (43% of rows — expected, due to repeated Modbus polling of the same register values)
- Invalid label/type rows removed: 0
- Final row count: 17,792

## Label distribution (before cleaning)
- Attack (1): 16,106
- Normal (0): 15,000

## Attack type distribution
- normal: 15,000
- injection: 5,000
- backdoor: 5,000
- password: 5,000
- xss: 577
- scanning: 529

## Notes
- Contains real Modbus function codes (FC1–FC4), directly comparable to PLC traffic in our simulator.
- xss and scanning are small classes — flagged for the ML team as potentially harder to classify reliably.

## Standardization
- Mapped to LightX schema: sensor_reading_1–4, label, attack_type, timestamp
- Final file: datasets/standardized/modbus_final.csv (17,792 rows, 8 columns)