# Network Dataset — Cleaning & Standardization Report

## Original
- Rows: 211,043
- Columns: 44
- Nulls (raw pandas check): 0 — see note below on placeholder nulls

## Cleaning
- Duplicates removed: 20,569 (~10% of rows)
- Invalid label/type rows removed: 0
- Final row count: 190,474

## Label distribution (before cleaning)
- Attack (1): 161,043
- Normal (0): 50,000

## Attack type distribution
- normal: 50,000
- backdoor: 20,000
- ddos: 20,000
- dos: 20,000
- injection: 20,000
- password: 20,000
- ransomware: 20,000
- scanning: 20,000
- xss: 20,000
- mitm: 1,043

## Notes
- Most balanced attack-type distribution of all 4 files — every major class has exactly 20,000 rows except mitm (1,043), which is notably underrepresented and should be flagged to the ML team.
- Dataset includes both `dos` and `ddos` as separate classes — these were kept distinct (single-source vs distributed) rather than merged, since they represent different attack mechanics.
- Placeholder null handling: DNS, SSL, and HTTP fields used the string "-" instead of a true null to indicate "not applicable" (e.g. a plain TCP connection has no DNS or HTTP activity). Verified via value_counts: 176,198/211,043 rows had no DNS data, 210,642/211,043 had no SSL data. These were converted to real NaN before further processing rather than being treated as a valid category. These raw fields were excluded from the final standardized schema, since only IP/port/protocol/byte-count fields were mapped forward.
- Standard pandas `.isnull()` check reported 0 nulls only because of this placeholder issue — worth noting explicitly so this isn't misread as a genuinely complete dataset.

## Standardization
- Mapped to LightX schema: source_ip, destination_ip, source_port, destination_port, protocol, service, duration, src_bytes, dst_bytes, label, attack_type
- Final file: datasets/standardized/network_final.csv (190,474 rows, 11 columns)