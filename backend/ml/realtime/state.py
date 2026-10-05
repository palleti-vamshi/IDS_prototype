"""
Real-Time State Tracker for LightX-IDS (Phase 7.2)

Maintains causal historical sliding windows for industrial telemetry streams
across individual devices and global plant-wide communication channels.

Key Guarantees:
- Causal Isolation: Only records up to time t are maintained; zero future lookahead.
- Constant-Time Updates: Bounded deques ensure O(1) time and memory overhead.
- Cold-Start Safety: Gracefully handles early packet arrivals with robust default statistics.
- Immutability of Baselines: Training device statistics are frozen and read-only.
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
import math
from typing import Any, Dict, List, Optional, Union
import numpy as np


# Authoritative training-set statistics for the 19 industrial IoT sensors
# Computed exclusively on the 80,000-record training split of lightx_ids_dataset_100k.csv
FROZEN_DEVICE_STATISTICS: Dict[str, Dict[str, float]] = {
    "cmp_001_current_sensor": {
        "mean": 12.450311385785595,
        "std": 2.1438085048327844,
        "dup_rate": 0.8169717138103162,
    },
    "cmp_001_pressure_sensor": {
        "mean": 167.9933578722394,
        "std": 11.287690128497497,
        "dup_rate": 0.7245309902635954,
    },
    "cmp_001_temperature_sensor": {
        "mean": 43.33562795089707,
        "std": 5.9240479521381975,
        "dup_rate": 0.6442398489140698,
    },
    "cnv_001_current_sensor": {
        "mean": 9.907413383958234,
        "std": 2.203685743990846,
        "dup_rate": 0.8030374940673944,
    },
    "cnv_001_proximity_sensor": {
        "mean": 254.93051073985683,
        "std": 141.83745587020192,
        "dup_rate": 0.037231503579952266,
    },
    "cnv_001_rpm_sensor": {
        "mean": 1438.5624658846061,
        "std": 111.61974705539804,
        "dup_rate": 0.7965046684223127,
    },
    "mtr_001_current_sensor": {
        "mean": 12.273757170172084,
        "std": 3.9410888639725195,
        "dup_rate": 0.6814053537284895,
    },
    "mtr_001_rpm_sensor": {
        "mean": 1442.1159358036346,
        "std": 88.63832146140518,
        "dup_rate": 0.8151994335614822,
    },
    "mtr_001_temperature_sensor": {
        "mean": 42.02664299242424,
        "std": 4.369608210930756,
        "dup_rate": 0.5660511363636364,
    },
    "mtr_001_vibration_sensor": {
        "mean": 0.5935867262885385,
        "std": 1.9410607513584082,
        "dup_rate": 0.8578489056248529,
    },
    "mtr_001_voltage_sensor": {
        "mean": 231.5835149469624,
        "std": 8.742470554936068,
        "dup_rate": 0.03784956605593057,
    },
    "pmp_001_current_sensor": {
        "mean": 10.4469216152019,
        "std": 2.1096998772103626,
        "dup_rate": 0.8266033254156769,
    },
    "pmp_001_flow_sensor": {
        "mean": 65.22821163514485,
        "std": 17.219728534446375,
        "dup_rate": 0.7009815657170217,
    },
    "pmp_001_pressure_sensor": {
        "mean": 57.59215337853636,
        "std": 30.848053098214756,
        "dup_rate": 0.7589431844750993,
    },
    "tnk_001_humidity_sensor": {
        "mean": 55.267806850618456,
        "std": 8.931496947880198,
        "dup_rate": 0.03829686013320647,
    },
    "tnk_001_level_sensor": {
        "mean": 96.87810312204351,
        "std": 12.479886320430305,
        "dup_rate": 0.7365184484389783,
    },
    "tnk_001_pressure_sensor": {
        "mean": 102.1271265189421,
        "std": 3.401832881790174,
        "dup_rate": 0.8377412437455325,
    },
    "tnk_001_temperature_sensor": {
        "mean": 26.104047562425684,
        "std": 2.3431596353449105,
        "dup_rate": 0.6917954815695601,
    },
    "vlv_001_pressure_sensor": {
        "mean": 147.86032662721894,
        "std": 68.32396099889758,
        "dup_rate": 0.578698224852071,
    },
}


def calc_window_mean(values: Union[deque, List[float]]) -> float:
    """Compute arithmetic mean of a sliding window."""
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def calc_window_sample_std(values: Union[deque, List[float]]) -> float:
    """
    Compute sample standard deviation (ddof=1) of a sliding window.
    Matches pandas Series.rolling(..., min_periods=1).std().fillna(0).
    """
    n = len(values)
    if n < 2:
        return 0.0
    mean_val = sum(values) / n
    variance = sum((x - mean_val) ** 2 for x in values) / (n - 1)
    return float(math.sqrt(max(0.0, variance)))


@dataclass
class DeviceHistoryState:
    """Sliding history state for a single device/sensor."""
    device_id: str
    val_hist: deque = field(default_factory=lambda: deque(maxlen=10))
    prev_timestamp: Optional[datetime] = None
    td_hist: deque = field(default_factory=lambda: deque(maxlen=5))
    prev_sequence: Optional[float] = None
    seq_gap_hist: deque = field(default_factory=lambda: deque(maxlen=5))
    prev_value_change: float = 0.0
    has_seen_packet: bool = False

    def reset(self) -> None:
        """Clear all historical state for this device."""
        self.val_hist.clear()
        self.prev_timestamp = None
        self.td_hist.clear()
        self.prev_sequence = None
        self.seq_gap_hist.clear()
        self.prev_value_change = 0.0
        self.has_seen_packet = False


@dataclass
class GlobalHistoryState:
    """Sliding history state across all devices in the industrial plant."""
    prev_timestamp: Optional[datetime] = None
    global_td_hist: deque = field(default_factory=lambda: deque(maxlen=10))
    plant_dup_hist: deque = field(default_factory=lambda: deque(maxlen=19))

    def reset(self) -> None:
        """Clear plant-wide historical state."""
        self.prev_timestamp = None
        self.global_td_hist.clear()
        self.plant_dup_hist.clear()


class RealTimeStateTracker:
    """
    Tracks and updates the rolling causal state for real-time feature adapter.
    """

    def __init__(
        self,
        device_statistics: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> None:
        """
        Initialize the RealTimeStateTracker.

        Args:
            device_statistics: Optional precomputed training statistics mapping
                               device_id -> {'mean': float, 'std': float, 'dup_rate': float}.
                               Defaults to FROZEN_DEVICE_STATISTICS.
        """
        if device_statistics is None:
            self.device_statistics = dict(FROZEN_DEVICE_STATISTICS)
        else:
            self.device_statistics = dict(device_statistics)

        # Compute global fallback baseline statistics for unseen devices
        if self.device_statistics:
            self.global_mean = float(
                np.mean([s["mean"] for s in self.device_statistics.values()])
            )
            g_std = float(
                np.mean([s["std"] for s in self.device_statistics.values()])
            )
            self.global_std = g_std if np.isfinite(g_std) and g_std > 0 else 1.0
        else:
            self.global_mean = 0.0
            self.global_std = 1.0

        self.device_states: Dict[str, DeviceHistoryState] = {}
        self.global_state = GlobalHistoryState()

    def get_device_state(self, device_id: str) -> DeviceHistoryState:
        """Retrieve or create the history state container for a given device."""
        if device_id not in self.device_states:
            self.device_states[device_id] = DeviceHistoryState(device_id=device_id)
        return self.device_states[device_id]

    def get_device_statistics(self, device_id: str) -> Dict[str, float]:
        """
        Retrieve frozen baseline statistics for a device, falling back to global mean/std.
        """
        if device_id in self.device_statistics:
            stats = self.device_statistics[device_id]
            std_val = stats.get("std", self.global_std)
            if not np.isfinite(std_val) or std_val == 0:
                std_val = 1.0
            return {
                "mean": float(stats.get("mean", self.global_mean)),
                "std": float(std_val),
                "dup_rate": float(stats.get("dup_rate", 0.5)),
            }
        return {
            "mean": self.global_mean,
            "std": self.global_std,
            "dup_rate": 0.5,
        }

    def reset(self) -> None:
        """Reset all device states and global stream history."""
        for state in self.device_states.values():
            state.reset()
        self.device_states.clear()
        self.global_state.reset()
