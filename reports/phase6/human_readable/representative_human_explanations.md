# LightX-IDS: Representative Human-Readable Explanations

**Phase 6.6 Artifact** | Model: `backend/ml/saved_models/xgboost_h3_32.pkl` | Dataset: `dataset/lightx_ids_dataset_100k.csv` (Seed 42 Test Split)

> [!IMPORTANT]
> SHAP values explain **model decision behavior** and feature attribution, not physical causality.
> All confidence categories are qualitative communication labels, not calibrated statistical probability guarantees.

---

## Case 1: DoS Attack (Record #3203)

- **Recorded Attack Type (Ground Truth):** `DoS Attack`
- **Model Prediction:** `ATTACK`
- **Assigned Attack Probability:** `99.36%` (high model confidence)
- **Raw Margin (Base Value):** `+5.0460` (Base: `-0.2719`)
- **Borderline Flag:** `False`

### Summary
> Attack detected with a 99.36% model-assigned attack probability (high model confidence). The prediction was driven primarily by plant-wide duplicate-value ratio and recent inter-arrival timing pattern. These features contributed strongly toward the Attack prediction, while MQTT topic identity contributed toward the Normal side.

### Key Attack-Directed Contributors (+)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `plant_duplicate_ratio_19` | plant-wide duplicate-value ratio | `+3.3264` | **very strong** | `0.3158` |
| 2 | `rolling_time_delta_5` | recent inter-arrival timing pattern | `+0.8334` | **moderate** | `0.0630` |
| 3 | `rolling_time_delta_std_5` | recent timing variability | `+0.7326` | **moderate** | `0.0025` |
| 4 | `time_delta` | current inter-arrival time | `+0.6391` | **moderate** | `0.0657` |
| 5 | `rolling_global_td_10` | recent network-wide inter-arrival pattern | `+0.2765` | **weak** | `0.0000` |

### Key Normal-Directed Contributors (-)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `topic` | MQTT topic identity | `-0.1110` | **weak** | `factory/line1/pressure` |
| 2 | `device_mean_deviation` | deviation from device historical mean | `-0.1001` | **weak** | `-0.8271` |
| 3 | `rel_volatility` | relative value volatility | `-0.0865` | **weak** | `0.0000` |
| 4 | `packet_rate_10` | recent packet rate | `-0.0831` | **weak** | `9643.2015` |
| 5 | `rolling_seq_std_5` | sequence number jitter | `-0.0646` | **weak** | `1.0954` |

### Operator Guidance
*Operator interpretation: The model detected an abnormal telemetry pattern characterized by plant-wide duplicate-value ratio and recent inter-arrival timing pattern. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.*

### Formatted Console View
```text
==============================================================================
LIGHTX-IDS EXPLANATION | RECORD #3203 | PREDICTION: ATTACK
==============================================================================
Assigned Attack Probability : 99.36% (high model confidence)
Model Margin (Base Value)   : +5.0460 (Base: -0.2719)
Recorded Context            : The dataset records this sample as DoS Attack.

SUMMARY:
  Attack detected with a 99.36% model-assigned attack probability (high model confidence). The prediction was driven primarily by plant-wide duplicate-value ratio and recent inter-arrival timing pattern. These features contributed strongly toward the Attack prediction, while MQTT topic identity contributed toward the Normal side.

KEY ATTACK-DIRECTED CONTRIBUTORS (+):
  1. plant-wide duplicate-value ratio (plant_duplicate_ratio_19) [Raw: 0.3157894736842105]
     SHAP Impact: +3.3264 (very strong)
  2. recent inter-arrival timing pattern (rolling_time_delta_5) [Raw: 0.0630332]
     SHAP Impact: +0.8334 (moderate)
  3. recent timing variability (rolling_time_delta_std_5) [Raw: 0.0024977112923635332]
     SHAP Impact: +0.7326 (moderate)
  4. current inter-arrival time (time_delta) [Raw: 0.065724]
     SHAP Impact: +0.6391 (moderate)
  5. recent network-wide inter-arrival pattern (rolling_global_td_10) [Raw: 3.6999999999999997e-06]
     SHAP Impact: +0.2765 (weak)

KEY NORMAL-DIRECTED CONTRIBUTORS (-):
  1. MQTT topic identity (topic) [Raw: factory/line1/pressure]
     SHAP Impact: -0.1110 (weak)
  2. deviation from device historical mean (device_mean_deviation) [Raw: -0.8271265189421086]
     SHAP Impact: -0.1001 (weak)
  3. relative value volatility (rel_volatility) [Raw: 0.0]
     SHAP Impact: -0.0865 (weak)
  4. recent packet rate (packet_rate_10) [Raw: 9643.201542912248]
     SHAP Impact: -0.0831 (weak)
  5. sequence number jitter (rolling_seq_std_5) [Raw: 1.0954451150103344]
     SHAP Impact: -0.0646 (weak)

OPERATOR GUIDANCE:
  Operator interpretation: The model detected an abnormal telemetry pattern characterized by plant-wide duplicate-value ratio and recent inter-arrival timing pattern. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.

SCIENTIFIC & OPERATIONAL LIMITATIONS:
  • SHAP explains model decision behavior and feature attribution, not physical causality.
  • Confidence categories are qualitative communication labels, not calibrated statistical probability guarantees.
  • The model's explanation does not independently infer or verify the ground-truth attack category.
  • Operator recommendations are advisory; all operational actions must be verified against physical systems and plant safety protocols.
==============================================================================
```

---

## Case 2: Replay Attack (Record #10977)

- **Recorded Attack Type (Ground Truth):** `Replay Attack`
- **Model Prediction:** `ATTACK`
- **Assigned Attack Probability:** `99.99%` (high model confidence)
- **Raw Margin (Base Value):** `+9.1711` (Base: `-0.2719`)
- **Borderline Flag:** `False`

### Summary
> Attack detected with a 99.99% model-assigned attack probability (high model confidence). The prediction was driven primarily by recent network-wide timing variability and recent packet rate. These features contributed strongly toward the Attack prediction, while short-term rolling mean contributed toward the Normal side.

### Key Attack-Directed Contributors (+)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `rolling_global_td_std_10` | recent network-wide timing variability | `+4.4048` | **very strong** | `2.3475` |
| 2 | `packet_rate_10` | recent packet rate | `+1.8355` | **strong** | `-6.5934` |
| 3 | `rolling_time_delta_std_5` | recent timing variability | `+1.5541` | **strong** | `1.5694` |
| 4 | `rolling_global_td_10` | recent network-wide inter-arrival pattern | `+0.4237` | **moderate** | `-0.1518` |
| 5 | `rolling_seq_std_5` | sequence number jitter | `+0.4221` | **moderate** | `25.8399` |

### Key Normal-Directed Contributors (-)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `rolling_mean_3` | short-term rolling mean | `-0.0531` | **weak** | `0.1000` |
| 2 | `topic` | MQTT topic identity | `-0.0505` | **weak** | `factory/line1/vibration` |
| 3 | `rolling_std_5` | medium-term value variability | `-0.0313` | **weak** | `0.0000` |
| 4 | `rel_volatility` | relative value volatility | `-0.0284` | **weak** | `0.0000` |
| 5 | `percentage_change` | recent percentage change in sensor value | `-0.0038` | **weak** | `0.0000` |

### Operator Guidance
*Operator interpretation: The model detected an abnormal telemetry pattern characterized by recent network-wide timing variability and recent packet rate. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.*

### Formatted Console View
```text
==============================================================================
LIGHTX-IDS EXPLANATION | RECORD #10977 | PREDICTION: ATTACK
==============================================================================
Assigned Attack Probability : 99.99% (high model confidence)
Model Margin (Base Value)   : +9.1711 (Base: -0.2719)
Recorded Context            : The dataset records this sample as Replay Attack.

SUMMARY:
  Attack detected with a 99.99% model-assigned attack probability (high model confidence). The prediction was driven primarily by recent network-wide timing variability and recent packet rate. These features contributed strongly toward the Attack prediction, while short-term rolling mean contributed toward the Normal side.

KEY ATTACK-DIRECTED CONTRIBUTORS (+):
  1. recent network-wide timing variability (rolling_global_td_std_10) [Raw: 2.347476522645402]
     SHAP Impact: +4.4048 (very strong)
  2. recent packet rate (packet_rate_10) [Raw: -6.593448617584587]
     SHAP Impact: +1.8355 (strong)
  3. recent timing variability (rolling_time_delta_std_5) [Raw: 1.5694158065191648]
     SHAP Impact: +1.5541 (strong)
  4. recent network-wide inter-arrival pattern (rolling_global_td_10) [Raw: -0.1517657000000002]
     SHAP Impact: +0.4237 (moderate)
  5. sequence number jitter (rolling_seq_std_5) [Raw: 25.839891640639685]
     SHAP Impact: +0.4221 (moderate)

KEY NORMAL-DIRECTED CONTRIBUTORS (-):
  1. short-term rolling mean (rolling_mean_3) [Raw: 0.1]
     SHAP Impact: -0.0531 (weak)
  2. MQTT topic identity (topic) [Raw: factory/line1/vibration]
     SHAP Impact: -0.0505 (weak)
  3. medium-term value variability (rolling_std_5) [Raw: 0.0]
     SHAP Impact: -0.0313 (weak)
  4. relative value volatility (rel_volatility) [Raw: 0.0]
     SHAP Impact: -0.0284 (weak)
  5. recent percentage change in sensor value (percentage_change) [Raw: 0.0]
     SHAP Impact: -0.0038 (weak)

OPERATOR GUIDANCE:
  Operator interpretation: The model detected an abnormal telemetry pattern characterized by recent network-wide timing variability and recent packet rate. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.

SCIENTIFIC & OPERATIONAL LIMITATIONS:
  • SHAP explains model decision behavior and feature attribution, not physical causality.
  • Confidence categories are qualitative communication labels, not calibrated statistical probability guarantees.
  • The model's explanation does not independently infer or verify the ground-truth attack category.
  • Operator recommendations are advisory; all operational actions must be verified against physical systems and plant safety protocols.
==============================================================================
```

---

## Case 3: Sensor Freeze Attack (Record #48510)

- **Recorded Attack Type (Ground Truth):** `Sensor Freeze Attack`
- **Model Prediction:** `ATTACK`
- **Assigned Attack Probability:** `99.94%` (high model confidence)
- **Raw Margin (Base Value):** `+7.4103` (Base: `-0.2719`)
- **Borderline Flag:** `False`

### Summary
> Attack detected with a 99.94% model-assigned attack probability (high model confidence). The prediction was driven primarily by plant-wide duplicate-value ratio and recent inter-arrival timing pattern. These features contributed strongly toward the Attack prediction, while sequence gap deviation contributed toward the Normal side.

### Key Attack-Directed Contributors (+)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `plant_duplicate_ratio_19` | plant-wide duplicate-value ratio | `+5.5510` | **very strong** | `1.0000` |
| 2 | `rolling_time_delta_5` | recent inter-arrival timing pattern | `+1.4363` | **strong** | `0.1688` |
| 3 | `time_delta` | current inter-arrival time | `+0.7335` | **moderate** | `0.1706` |
| 4 | `value` | current sensor value | `+0.0742` | **weak** | `0.1000` |
| 5 | `device_mean_deviation` | deviation from device historical mean | `+0.0556` | **weak** | `-0.4936` |

### Key Normal-Directed Contributors (-)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `seq_gap_dev` | sequence gap deviation | `-0.0832` | **weak** | `0.0000` |
| 2 | `topic` | MQTT topic identity | `-0.0788` | **weak** | `factory/line1/vibration` |
| 3 | `z_score` | statistical z-score relative to baseline | `-0.0678` | **weak** | `-0.2543` |
| 4 | `rolling_std_5` | medium-term value variability | `-0.0548` | **weak** | `0.0000` |
| 5 | `percentage_change` | recent percentage change in sensor value | `-0.0299` | **weak** | `0.0000` |

### Operator Guidance
*Operator interpretation: The model detected an abnormal telemetry pattern characterized by plant-wide duplicate-value ratio and recent inter-arrival timing pattern. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.*

### Formatted Console View
```text
==============================================================================
LIGHTX-IDS EXPLANATION | RECORD #48510 | PREDICTION: ATTACK
==============================================================================
Assigned Attack Probability : 99.94% (high model confidence)
Model Margin (Base Value)   : +7.4103 (Base: -0.2719)
Recorded Context            : The dataset records this sample as Sensor Freeze Attack.

SUMMARY:
  Attack detected with a 99.94% model-assigned attack probability (high model confidence). The prediction was driven primarily by plant-wide duplicate-value ratio and recent inter-arrival timing pattern. These features contributed strongly toward the Attack prediction, while sequence gap deviation contributed toward the Normal side.

KEY ATTACK-DIRECTED CONTRIBUTORS (+):
  1. plant-wide duplicate-value ratio (plant_duplicate_ratio_19) [Raw: 1.0]
     SHAP Impact: +5.5510 (very strong)
  2. recent inter-arrival timing pattern (rolling_time_delta_5) [Raw: 0.16879899999999973]
     SHAP Impact: +1.4363 (strong)
  3. current inter-arrival time (time_delta) [Raw: 0.170567]
     SHAP Impact: +0.7335 (moderate)
  4. current sensor value (value) [Raw: 0.1]
     SHAP Impact: +0.0742 (weak)
  5. deviation from device historical mean (device_mean_deviation) [Raw: -0.4935867262885385]
     SHAP Impact: +0.0556 (weak)

KEY NORMAL-DIRECTED CONTRIBUTORS (-):
  1. sequence gap deviation (seq_gap_dev) [Raw: 0.0]
     SHAP Impact: -0.0832 (weak)
  2. MQTT topic identity (topic) [Raw: factory/line1/vibration]
     SHAP Impact: -0.0788 (weak)
  3. statistical z-score relative to baseline (z_score) [Raw: -0.25428710870750076]
     SHAP Impact: -0.0678 (weak)
  4. medium-term value variability (rolling_std_5) [Raw: 0.0]
     SHAP Impact: -0.0548 (weak)
  5. recent percentage change in sensor value (percentage_change) [Raw: 0.0]
     SHAP Impact: -0.0299 (weak)

OPERATOR GUIDANCE:
  Operator interpretation: The model detected an abnormal telemetry pattern characterized by plant-wide duplicate-value ratio and recent inter-arrival timing pattern. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.

SCIENTIFIC & OPERATIONAL LIMITATIONS:
  • SHAP explains model decision behavior and feature attribution, not physical causality.
  • Confidence categories are qualitative communication labels, not calibrated statistical probability guarantees.
  • The model's explanation does not independently infer or verify the ground-truth attack category.
  • Operator recommendations are advisory; all operational actions must be verified against physical systems and plant safety protocols.
==============================================================================
```

---

## Case 4: Motor Overload Attack (Record #75660)

- **Recorded Attack Type (Ground Truth):** `Motor Overload Attack`
- **Model Prediction:** `ATTACK`
- **Assigned Attack Probability:** `99.66%` (high model confidence)
- **Raw Margin (Base Value):** `+5.6721` (Base: `-0.2719`)
- **Borderline Flag:** `False`

### Summary
> Attack detected with a 99.66% model-assigned attack probability (high model confidence). The prediction was driven primarily by recent percentage change in sensor value and plant-wide duplicate-value ratio. These features contributed strongly toward the Attack prediction, while recent inter-arrival timing pattern contributed toward the Normal side.

### Key Attack-Directed Contributors (+)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `percentage_change` | recent percentage change in sensor value | `+1.7844` | **strong** | `0.0006` |
| 2 | `plant_duplicate_ratio_19` | plant-wide duplicate-value ratio | `+1.1052` | **strong** | `0.6316` |
| 3 | `rel_volatility` | relative value volatility | `+0.6408` | **moderate** | `0.0109` |
| 4 | `packet_rate_10` | recent packet rate | `+0.4972` | **moderate** | `41.8717` |
| 5 | `rolling_std_10` | recent value variability | `+0.4485` | **moderate** | `0.0908` |

### Key Normal-Directed Contributors (-)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `rolling_time_delta_5` | recent inter-arrival timing pattern | `-1.1036` | **strong** | `0.2577` |
| 2 | `time_delta` | current inter-arrival time | `-0.2385` | **weak** | `0.2379` |
| 3 | `topic` | MQTT topic identity | `-0.0422` | **weak** | `factory/line1/temperature` |
| 4 | `seq_gap_dev` | sequence gap deviation | `-0.0094` | **weak** | `0.0000` |
| 5 | `is_negative_time_delta` | negative timestamp anomaly indicator | `-0.0001` | **weak** | `0` |

### Operator Guidance
*Operator interpretation: The model detected an abnormal telemetry pattern characterized by recent percentage change in sensor value and plant-wide duplicate-value ratio. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.*

### Formatted Console View
```text
==============================================================================
LIGHTX-IDS EXPLANATION | RECORD #75660 | PREDICTION: ATTACK
==============================================================================
Assigned Attack Probability : 99.66% (high model confidence)
Model Margin (Base Value)   : +5.6721 (Base: -0.2719)
Recorded Context            : The dataset records this sample as Motor Overload Attack.

SUMMARY:
  Attack detected with a 99.66% model-assigned attack probability (high model confidence). The prediction was driven primarily by recent percentage change in sensor value and plant-wide duplicate-value ratio. These features contributed strongly toward the Attack prediction, while recent inter-arrival timing pattern contributed toward the Normal side.

KEY ATTACK-DIRECTED CONTRIBUTORS (+):
  1. recent percentage change in sensor value (percentage_change) [Raw: 0.0006280092108015278]
     SHAP Impact: +1.7844 (strong)
  2. plant-wide duplicate-value ratio (plant_duplicate_ratio_19) [Raw: 0.631578947368421]
     SHAP Impact: +1.1052 (strong)
  3. relative value volatility (rel_volatility) [Raw: 0.010855473213873694]
     SHAP Impact: +0.6408 (moderate)
  4. recent packet rate (packet_rate_10) [Raw: 41.87166335182725]
     SHAP Impact: +0.4972 (moderate)
  5. recent value variability (rolling_std_10) [Raw: 0.09082951062163509]
     SHAP Impact: +0.4485 (moderate)

KEY NORMAL-DIRECTED CONTRIBUTORS (-):
  1. recent inter-arrival timing pattern (rolling_time_delta_5) [Raw: 0.25769739999999997]
     SHAP Impact: -1.1036 (strong)
  2. current inter-arrival time (time_delta) [Raw: 0.237901]
     SHAP Impact: -0.2385 (weak)
  3. MQTT topic identity (topic) [Raw: factory/line1/temperature]
     SHAP Impact: -0.0422 (weak)
  4. sequence gap deviation (seq_gap_dev) [Raw: 0.0]
     SHAP Impact: -0.0094 (weak)
  5. negative timestamp anomaly indicator (is_negative_time_delta) [Raw: 0]
     SHAP Impact: -0.0001 (weak)

OPERATOR GUIDANCE:
  Operator interpretation: The model detected an abnormal telemetry pattern characterized by recent percentage change in sensor value and plant-wide duplicate-value ratio. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.

SCIENTIFIC & OPERATIONAL LIMITATIONS:
  • SHAP explains model decision behavior and feature attribution, not physical causality.
  • Confidence categories are qualitative communication labels, not calibrated statistical probability guarantees.
  • The model's explanation does not independently infer or verify the ground-truth attack category.
  • Operator recommendations are advisory; all operational actions must be verified against physical systems and plant safety protocols.
==============================================================================
```

---

## Case 5: Slow Drift Attack (Record #88360)

- **Recorded Attack Type (Ground Truth):** `Slow Drift Attack`
- **Model Prediction:** `ATTACK`
- **Assigned Attack Probability:** `99.99%` (high model confidence)
- **Raw Margin (Base Value):** `+9.0006` (Base: `-0.2719`)
- **Borderline Flag:** `False`

### Summary
> Attack detected with a 99.99% model-assigned attack probability (high model confidence). The prediction was driven primarily by plant-wide duplicate-value ratio and current inter-arrival time. These features contributed strongly toward the Attack prediction, while sequence number jitter contributed toward the Normal side.

### Key Attack-Directed Contributors (+)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `plant_duplicate_ratio_19` | plant-wide duplicate-value ratio | `+5.1410` | **very strong** | `0.1579` |
| 2 | `time_delta` | current inter-arrival time | `+0.8796` | **moderate** | `0.3178` |
| 3 | `rolling_time_delta_5` | recent inter-arrival timing pattern | `+0.8566` | **moderate** | `0.3117` |
| 4 | `rolling_time_delta_std_5` | recent timing variability | `+0.7122` | **moderate** | `0.0197` |
| 5 | `rolling_global_td_std_10` | recent network-wide timing variability | `+0.4984` | **moderate** | `0.1005` |

### Key Normal-Directed Contributors (-)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `rolling_seq_std_5` | sequence number jitter | `-0.0993` | **weak** | `1.8166` |
| 2 | `topic` | MQTT topic identity | `-0.0671` | **weak** | `factory/line1/flow` |
| 3 | `value` | current sensor value | `-0.0566` | **weak** | `33.9200` |
| 4 | `seq_gap_dev` | sequence gap deviation | `-0.0533` | **weak** | `3.0000` |
| 5 | `rolling_mean_3` | short-term rolling mean | `-0.0144` | **weak** | `33.9100` |

### Operator Guidance
*Operator interpretation: The model detected an abnormal telemetry pattern characterized by plant-wide duplicate-value ratio and current inter-arrival time. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.*

### Formatted Console View
```text
==============================================================================
LIGHTX-IDS EXPLANATION | RECORD #88360 | PREDICTION: ATTACK
==============================================================================
Assigned Attack Probability : 99.99% (high model confidence)
Model Margin (Base Value)   : +9.0006 (Base: -0.2719)
Recorded Context            : The dataset records this sample as Slow Drift Attack.

SUMMARY:
  Attack detected with a 99.99% model-assigned attack probability (high model confidence). The prediction was driven primarily by plant-wide duplicate-value ratio and current inter-arrival time. These features contributed strongly toward the Attack prediction, while sequence number jitter contributed toward the Normal side.

KEY ATTACK-DIRECTED CONTRIBUTORS (+):
  1. plant-wide duplicate-value ratio (plant_duplicate_ratio_19) [Raw: 0.15789473684210525]
     SHAP Impact: +5.1410 (very strong)
  2. current inter-arrival time (time_delta) [Raw: 0.317805]
     SHAP Impact: +0.8796 (moderate)
  3. recent inter-arrival timing pattern (rolling_time_delta_5) [Raw: 0.31165460000000034]
     SHAP Impact: +0.8566 (moderate)
  4. recent timing variability (rolling_time_delta_std_5) [Raw: 0.019743005705974283]
     SHAP Impact: +0.7122 (moderate)
  5. recent network-wide timing variability (rolling_global_td_std_10) [Raw: 0.10045407261923159]
     SHAP Impact: +0.4984 (moderate)

KEY NORMAL-DIRECTED CONTRIBUTORS (-):
  1. sequence number jitter (rolling_seq_std_5) [Raw: 1.8165902124587041]
     SHAP Impact: -0.0993 (weak)
  2. MQTT topic identity (topic) [Raw: factory/line1/flow]
     SHAP Impact: -0.0671 (weak)
  3. current sensor value (value) [Raw: 33.92]
     SHAP Impact: -0.0566 (weak)
  4. sequence gap deviation (seq_gap_dev) [Raw: 3.0]
     SHAP Impact: -0.0533 (weak)
  5. short-term rolling mean (rolling_mean_3) [Raw: 33.91]
     SHAP Impact: -0.0144 (weak)

OPERATOR GUIDANCE:
  Operator interpretation: The model detected an abnormal telemetry pattern characterized by plant-wide duplicate-value ratio and current inter-arrival time. Review the affected telemetry stream and recent communication behavior; verify physical sensor readings and correlate with plant logs.

SCIENTIFIC & OPERATIONAL LIMITATIONS:
  • SHAP explains model decision behavior and feature attribution, not physical causality.
  • Confidence categories are qualitative communication labels, not calibrated statistical probability guarantees.
  • The model's explanation does not independently infer or verify the ground-truth attack category.
  • Operator recommendations are advisory; all operational actions must be verified against physical systems and plant safety protocols.
==============================================================================
```

---

## Case 6: Normal (Record #93364)

- **Recorded Attack Type (Ground Truth):** `not provided`
- **Model Prediction:** `NORMAL`
- **Assigned Attack Probability:** `0.01%` (low attack probability)
- **Raw Margin (Base Value):** `-9.2341` (Base: `-0.2719`)
- **Borderline Flag:** `False`

### Summary
> The model assigned a 0.01% attack probability (low attack probability) and predicted Normal. The strongest contributions pushed toward the Normal class, particularly plant-wide duplicate-value ratio and recent inter-arrival timing pattern. Minor evidence toward Attack came from recent network-wide inter-arrival pattern, but was outweighed by normal indications.

### Key Attack-Directed Contributors (+)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `rolling_global_td_10` | recent network-wide inter-arrival pattern | `+0.0974` | **weak** | `0.0000` |
| 2 | `z_score` | statistical z-score relative to baseline | `+0.0969` | **weak** | `0.2810` |
| 3 | `rolling_std_3` | short-term value variability | `+0.0432` | **weak** | `0.0000` |
| 4 | `time_delta` | current inter-arrival time | `+0.0355` | **weak** | `0.3383` |
| 5 | `device_mean_deviation` | deviation from device historical mean | `+0.0277` | **weak** | `1.6644` |

### Key Normal-Directed Contributors (-)
| Rank | Feature | Description | SHAP Value | Contribution Strength | Raw Value |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | `plant_duplicate_ratio_19` | plant-wide duplicate-value ratio | `-4.1898` | **very strong** | `0.8421` |
| 2 | `rolling_time_delta_5` | recent inter-arrival timing pattern | `-3.1309` | **very strong** | `0.3246` |
| 3 | `rolling_time_delta_std_5` | recent timing variability | `-0.7790` | **moderate** | `0.0250` |
| 4 | `rolling_global_td_std_10` | recent network-wide timing variability | `-0.1607` | **weak** | `0.0000` |
| 5 | `topic` | MQTT topic identity | `-0.1540` | **weak** | `factory/line1/temperature` |

### Operator Guidance
*Operator interpretation: Telemetry patterns fall within nominal operating boundaries. The model did not detect an anomalous pattern in this sample. Standard monitoring continues.*

### Formatted Console View
```text
==============================================================================
LIGHTX-IDS EXPLANATION | RECORD #93364 | PREDICTION: NORMAL
==============================================================================
Assigned Attack Probability : 0.01% (low attack probability)
Model Margin (Base Value)   : -9.2341 (Base: -0.2719)
Recorded Context            : Recorded attack type: not provided.

SUMMARY:
  The model assigned a 0.01% attack probability (low attack probability) and predicted Normal. The strongest contributions pushed toward the Normal class, particularly plant-wide duplicate-value ratio and recent inter-arrival timing pattern. Minor evidence toward Attack came from recent network-wide inter-arrival pattern, but was outweighed by normal indications.

KEY ATTACK-DIRECTED CONTRIBUTORS (+):
  1. recent network-wide inter-arrival pattern (rolling_global_td_10) [Raw: 5.199999999661383e-06]
     SHAP Impact: +0.0974 (weak)
  2. statistical z-score relative to baseline (z_score) [Raw: 0.2809518191867778]
     SHAP Impact: +0.0969 (weak)
  3. short-term value variability (rolling_std_3) [Raw: 0.0]
     SHAP Impact: +0.0432 (weak)
  4. current inter-arrival time (time_delta) [Raw: 0.338291]
     SHAP Impact: +0.0355 (weak)
  5. deviation from device historical mean (device_mean_deviation) [Raw: 1.66437204910293]
     SHAP Impact: +0.0277 (weak)

KEY NORMAL-DIRECTED CONTRIBUTORS (-):
  1. plant-wide duplicate-value ratio (plant_duplicate_ratio_19) [Raw: 0.8421052631578947]
     SHAP Impact: -4.1898 (very strong)
  2. recent inter-arrival timing pattern (rolling_time_delta_5) [Raw: 0.3245533999999999]
     SHAP Impact: -3.1309 (very strong)
  3. recent timing variability (rolling_time_delta_std_5) [Raw: 0.02496783879901418]
     SHAP Impact: -0.7790 (moderate)
  4. recent network-wide timing variability (rolling_global_td_std_10) [Raw: 3.0180216635834792e-05]
     SHAP Impact: -0.1607 (weak)
  5. MQTT topic identity (topic) [Raw: factory/line1/temperature]
     SHAP Impact: -0.1540 (weak)

OPERATOR GUIDANCE:
  Operator interpretation: Telemetry patterns fall within nominal operating boundaries. The model did not detect an anomalous pattern in this sample. Standard monitoring continues.

SCIENTIFIC & OPERATIONAL LIMITATIONS:
  • SHAP explains model decision behavior and feature attribution, not physical causality.
  • Confidence categories are qualitative communication labels, not calibrated statistical probability guarantees.
  • The model's explanation does not independently infer or verify the ground-truth attack category.
  • Operator recommendations are advisory; all operational actions must be verified against physical systems and plant safety protocols.
==============================================================================
```

---
