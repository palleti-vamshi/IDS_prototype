"""
Real-Time Feature Adapter for LightX-IDS (Phase 7.2)

Transforms individual streaming industrial IoT telemetry packets into the
frozen 32-feature H3-32 schema required by the XGBoost intrusion detection model.

Mathematical Equivalence Guarantee:
Every feature generated incrementally matches the offline batch FeatureGenerator
down to floating-point precision (|error| < 1e-5), while executing in O(1) time
with zero future lookahead.
"""

from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from backend.preprocessing.schemas import ParsedSensorRecord
from backend.ml.explainability.shap_local_explainer import (
    ALL_32_FEATURES,
    ACTIVE_NUMERIC_COLUMNS,
    ACTIVE_CATEGORICAL_COLUMNS,
)
from backend.ml.realtime.state import (
    RealTimeStateTracker,
    calc_window_mean,
    calc_window_sample_std,
)

logger = logging.getLogger(__name__)


def parse_timestamp_to_datetime(ts_val: Any) -> datetime:
    """Parse raw timestamp value into a python datetime object."""
    if isinstance(ts_val, datetime):
        return ts_val
    if isinstance(ts_val, (pd.Timestamp, np.datetime64)):
        return pd.to_datetime(ts_val).to_pydatetime()
    try:
        return pd.to_datetime(str(ts_val)).to_pydatetime()
    except Exception as e:
        logger.warning("Failed to parse timestamp '%s', defaulting to current time: %s", ts_val, e)
        return datetime.now()


class RealTimeFeatureAdapter:
    """
    Real-Time Feature Adapter for LightX-IDS.

    Consumes raw telemetry observations (from MQTT messages, simulator packets,
    or streaming rows) and yields complete 32-feature H3-32 vectors in constant time.
    """

    def __init__(
        self,
        state_tracker: Optional[RealTimeStateTracker] = None,
        device_statistics: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> None:
        """
        Initialize the RealTimeFeatureAdapter.

        Args:
            state_tracker: Optional pre-configured RealTimeStateTracker instance.
            device_statistics: Optional precomputed training statistics mapping.
        """
        if state_tracker is not None:
            self.state_tracker = state_tracker
        else:
            self.state_tracker = RealTimeStateTracker(device_statistics=device_statistics)

    def reset(self) -> None:
        """Reset historical sliding windows and device states."""
        self.state_tracker.reset()

    def transform_packet(
        self,
        packet: Union[ParsedSensorRecord, Dict[str, Any], pd.Series],
    ) -> Dict[str, Any]:
        """
        Incrementally transform a single industrial telemetry observation into the
        32 H3-32 features.

        Args:
            packet: ParsedSensorRecord, dict, or pandas Series containing sensor telemetry.

        Returns:
            Dictionary mapping feature names to their computed values for the 32 H3-32 features.
        """
        # Step 1: Extract standard raw fields
        if isinstance(packet, ParsedSensorRecord):
            raw_ts = packet.timestamp
            topic = str(packet.topic)
            device_id = str(packet.device_id)
            sensor_code = str(packet.sensor_code) if packet.sensor_code is not None else ""
            sensor_type = str(packet.sensor_type)
            val = float(packet.value)
            unit = str(packet.unit)
            status = str(packet.status)
            source = "simulator"
            seq_num = None
        elif isinstance(packet, (dict, pd.Series)):
            raw_ts = packet.get("timestamp")
            topic = str(packet.get("topic", ""))
            device_id = str(packet.get("device_id", ""))
            sensor_code = str(packet.get("sensor_code", ""))
            sensor_type = str(packet.get("sensor_type", ""))
            val = float(packet.get("value", 0.0))
            unit = str(packet.get("unit", ""))
            status = str(packet.get("status", ""))
            source = str(packet.get("source", "simulator"))
            raw_seq = packet.get("sequence_number")
            seq_num = float(raw_seq) if raw_seq is not None and pd.notna(raw_seq) else None
        else:
            raise TypeError(f"Unsupported packet type: {type(packet)}")

        current_dt = parse_timestamp_to_datetime(raw_ts)

        # Retrieve mutable state containers
        dev_state = self.state_tracker.get_device_state(device_id)
        glob_state = self.state_tracker.global_state

        # ==========================================================
        # 1. Causal Sequence Features
        # ==========================================================
        if seq_num is not None:
            if dev_state.prev_sequence is not None:
                device_seq_gap = float(seq_num - dev_state.prev_sequence)
            else:
                device_seq_gap = 19.0
            dev_state.prev_sequence = seq_num
            seq_gap_dev = abs(device_seq_gap - 19.0)
            dev_state.seq_gap_hist.append(device_seq_gap)
            rolling_seq_std_5 = calc_window_sample_std(dev_state.seq_gap_hist)
        else:
            device_seq_gap = 19.0
            seq_gap_dev = 0.0
            rolling_seq_std_5 = 0.0

        # ==========================================================
        # 2. Causal Device Timing Features
        # ==========================================================
        if dev_state.prev_timestamp is not None:
            time_delta = float((current_dt - dev_state.prev_timestamp).total_seconds())
        else:
            time_delta = 0.0
        dev_state.prev_timestamp = current_dt

        dev_state.td_hist.append(time_delta)
        rolling_time_delta_5 = calc_window_mean(dev_state.td_hist)
        rolling_time_delta_std_5 = calc_window_sample_std(dev_state.td_hist)
        is_negative_time_delta = 1 if time_delta < 0 else 0

        # ==========================================================
        # 3. Causal Global Plant Timing Features
        # ==========================================================
        if glob_state.prev_timestamp is not None:
            global_time_delta = float((current_dt - glob_state.prev_timestamp).total_seconds())
        else:
            global_time_delta = 0.0
        glob_state.prev_timestamp = current_dt

        glob_state.global_td_hist.append(global_time_delta)
        rolling_global_td_10 = calc_window_mean(glob_state.global_td_hist)
        rolling_global_td_std_10 = calc_window_sample_std(glob_state.global_td_hist)
        packet_rate_10 = float(1.0 / (rolling_global_td_10 + 1e-4))

        # ==========================================================
        # 4. Causal Value Dynamics & Plant Duplicate Ratio
        # ==========================================================
        val_hist = dev_state.val_hist
        if len(val_hist) > 0:
            prev_val = val_hist[-1]
            value_change = float(val - prev_val)
            if prev_val != 0.0:
                pct_change = float((val - prev_val) / prev_val)
            else:
                pct_change = 0.0
            if not np.isfinite(pct_change):
                pct_change = 0.0
        else:
            value_change = 0.0
            pct_change = 0.0

        if dev_state.has_seen_packet:
            value_accel = float(value_change - dev_state.prev_value_change)
        else:
            value_accel = 0.0
        dev_state.prev_value_change = value_change

        is_duplicate_value = 1 if value_change == 0.0 else 0

        glob_state.plant_dup_hist.append(is_duplicate_value)
        plant_duplicate_ratio_19 = calc_window_mean(glob_state.plant_dup_hist)

        # Append current value to device sliding history window
        val_hist.append(val)
        dev_state.has_seen_packet = True

        # Multi-window rolling statistics for value
        w3 = list(val_hist)[-3:]
        rolling_mean_3 = calc_window_mean(w3)
        rolling_std_3 = calc_window_sample_std(w3)

        w5 = list(val_hist)[-5:]
        rolling_mean_5 = calc_window_mean(w5)
        rolling_std_5 = calc_window_sample_std(w5)

        rolling_std_10 = calc_window_sample_std(val_hist)

        # ==========================================================
        # 5. Device Baseline Deviations & Statistics
        # ==========================================================
        dev_stats = self.state_tracker.get_device_statistics(device_id)
        d_mean = dev_stats["mean"]
        d_std = dev_stats["std"]
        d_dup = dev_stats["dup_rate"]

        device_mean_deviation = float(val - d_mean)
        z_score = float((val - d_mean) / d_std)
        rel_volatility = float(rolling_std_5 / d_std)
        stability_anomaly = float(is_duplicate_value * (1.0 - d_dup))

        # ==========================================================
        # 6. Assemble 32-Feature Dictionary Contract
        # ==========================================================
        features = {
            # 25 Numeric Features
            "value": val,
            "value_accel": value_accel,
            "time_delta": time_delta,
            "rolling_time_delta_5": rolling_time_delta_5,
            "rolling_time_delta_std_5": rolling_time_delta_std_5,
            "is_negative_time_delta": is_negative_time_delta,
            "global_time_delta": global_time_delta,
            "rolling_global_td_10": rolling_global_td_10,
            "rolling_global_td_std_10": rolling_global_td_std_10,
            "packet_rate_10": packet_rate_10,
            "is_duplicate_value": is_duplicate_value,
            "device_seq_gap": device_seq_gap,
            "seq_gap_dev": seq_gap_dev,
            "rolling_seq_std_5": rolling_seq_std_5,
            "rolling_mean_3": rolling_mean_3,
            "rolling_std_3": rolling_std_3,
            "rolling_mean_5": rolling_mean_5,
            "rolling_std_5": rolling_std_5,
            "rolling_std_10": rolling_std_10,
            "plant_duplicate_ratio_19": plant_duplicate_ratio_19,
            "percentage_change": pct_change,
            "device_mean_deviation": device_mean_deviation,
            "z_score": z_score,
            "rel_volatility": rel_volatility,
            "stability_anomaly": stability_anomaly,
            # 7 Categorical Features
            "topic": topic,
            "device_id": device_id,
            "sensor_code": sensor_code,
            "sensor_type": sensor_type,
            "unit": unit,
            "status": status,
            "source": source,
        }

        return features

    def transform_to_dataframe(
        self,
        packet: Union[ParsedSensorRecord, Dict[str, Any], pd.Series],
    ) -> pd.DataFrame:
        """
        Transform a telemetry observation and return a 1-row DataFrame aligned
        with ALL_32_FEATURES column ordering ready for XGBoost pipeline ingestion.
        """
        feat_dict = self.transform_packet(packet)
        # Enforce exact column ordering from ALL_32_FEATURES
        ordered_dict = {col: [feat_dict[col]] for col in ALL_32_FEATURES}
        return pd.DataFrame(ordered_dict)
