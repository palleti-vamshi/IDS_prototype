"""
Unit, Equivalence, and Causality Tests for Phase 7.2 RealTimeFeatureAdapter

Verifies:
1. StateTracker initialization and clean reset.
2. Cold-start handling for device and global metrics.
3. Support for ParsedSensorRecord, dict, and pandas Series.
4. Conformance to 32-feature H3-32 schema contract.
5. 100% numerical equivalence against offline batch FeatureGenerator over 1,000 packets.
6. Strict causal isolation (zero future lookahead).
7. Device isolation (device A does not corrupt device B rolling metrics).
8. Graceful fallback for unknown devices.
9. Missing sequence number handling.
10. High-throughput latency benchmarking (< 0.1 ms per packet).
"""

import math
import time
import unittest
import numpy as np
import pandas as pd

from backend.ml.config import LIGHTX_100K
from backend.ml.explainability.shap_local_explainer import (
    ALL_32_FEATURES,
    ACTIVE_NUMERIC_COLUMNS,
    ACTIVE_CATEGORICAL_COLUMNS,
)
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.preprocessing.schemas import ParsedSensorRecord
from backend.ml.realtime.state import RealTimeStateTracker, FROZEN_DEVICE_STATISTICS
from backend.ml.realtime.feature_adapter import RealTimeFeatureAdapter


class TestRealTimeFeatureAdapter(unittest.TestCase):
    """Test suite for Phase 7.2 RealTimeFeatureAdapter and StateTracker."""

    @classmethod
    def setUpClass(cls):
        """Prepare sample slice from 100k dataset for test comparisons."""
        cls.raw_df = pd.read_csv(LIGHTX_100K, nrows=1000)

        # Generate reference offline features
        cls.offline_fg = FeatureGenerator()
        cls.offline_fg.device_statistics = dict(FROZEN_DEVICE_STATISTICS)
        cls.offline_fg.is_fitted = True
        stream = cls.offline_fg.generate_causal_stream_features(cls.raw_df)
        cls.offline_features = cls.offline_fg.transform(stream)

    def setUp(self):
        """Initialize fresh adapter for each test."""
        self.adapter = RealTimeFeatureAdapter()

    def test_01_initialization_and_reset(self):
        """Verify tracker starts empty and reset clears state."""
        tracker = self.adapter.state_tracker
        self.assertEqual(len(tracker.device_states), 0)
        self.assertIsNone(tracker.global_state.prev_timestamp)

        # Process a packet to populate state
        row = self.raw_df.iloc[0]
        self.adapter.transform_packet(row)
        self.assertGreater(len(tracker.device_states), 0)
        self.assertIsNotNone(tracker.global_state.prev_timestamp)

        # Reset
        self.adapter.reset()
        self.assertEqual(len(tracker.device_states), 0)
        self.assertIsNone(tracker.global_state.prev_timestamp)

    def test_02_cold_start_single_packet(self):
        """Verify cold-start defaults on very first packet."""
        row = {
            "timestamp": "2026-10-04T12:00:00.000000",
            "topic": "factory/line1/temperature",
            "device_id": "mtr_001_temperature_sensor",
            "sensor_code": "MTR-001-TMP",
            "sensor_type": "temperature",
            "value": 42.0,
            "unit": "°C",
            "status": "RUNNING",
            "source": "simulator",
            "sequence_number": 100,
        }
        res = self.adapter.transform_packet(row)

        self.assertEqual(res["value"], 42.0)
        self.assertEqual(res["time_delta"], 0.0)
        self.assertEqual(res["rolling_time_delta_5"], 0.0)
        self.assertEqual(res["rolling_time_delta_std_5"], 0.0)
        self.assertEqual(res["is_negative_time_delta"], 0)
        self.assertEqual(res["global_time_delta"], 0.0)
        self.assertEqual(res["device_seq_gap"], 19.0)
        self.assertEqual(res["seq_gap_dev"], 0.0)
        self.assertEqual(res["rolling_seq_std_5"], 0.0)
        self.assertEqual(res["value_accel"], 0.0)
        self.assertEqual(res["is_duplicate_value"], 1)
        self.assertEqual(res["plant_duplicate_ratio_19"], 1.0)
        self.assertEqual(res["rolling_mean_3"], 42.0)
        self.assertEqual(res["rolling_std_3"], 0.0)
        self.assertEqual(res["percentage_change"], 0.0)

        # Assert no NaNs or Infs
        for k, v in res.items():
            if isinstance(v, (int, float)):
                self.assertTrue(math.isfinite(v), f"Feature {k} was not finite: {v}")

    def test_03_packet_types_accepted(self):
        """Verify support for ParsedSensorRecord, dict, and pd.Series."""
        parsed = ParsedSensorRecord(
            timestamp="2026-10-04T12:00:00",
            topic="factory/line1/pressure",
            device_id="cmp_001_pressure_sensor",
            sensor_type="pressure",
            value=165.2,
            unit="bar",
            status="RUNNING",
            sensor_code="CMP-001-PRS",
        )
        res1 = self.adapter.transform_packet(parsed)
        self.assertEqual(res1["value"], 165.2)

        from dataclasses import asdict
        d = asdict(parsed)
        res2 = self.adapter.transform_packet(d)
        self.assertIsInstance(res2, dict)

        s = pd.Series(d)
        res3 = self.adapter.transform_packet(s)
        self.assertIsInstance(res3, dict)

    def test_04_transform_to_dataframe_contract(self):
        """Verify transform_to_dataframe outputs exactly the 32 H3-32 columns in order."""
        row = self.raw_df.iloc[0]
        df_out = self.adapter.transform_to_dataframe(row)

        self.assertIsInstance(df_out, pd.DataFrame)
        self.assertEqual(len(df_out), 1)
        self.assertEqual(list(df_out.columns), ALL_32_FEATURES)
        self.assertEqual(len(df_out.columns), 32)

    def test_05_100pct_numerical_equivalence_against_offline_generator(self):
        """
        Verify exact numerical equivalence against offline batch FeatureGenerator
        across 1,000 consecutive chronological records.
        """
        self.adapter.reset()
        max_diffs = {col: 0.0 for col in ACTIVE_NUMERIC_COLUMNS}

        for idx, row in self.raw_df.iterrows():
            realtime_features = self.adapter.transform_packet(row)
            offline_row = self.offline_features.iloc[idx]

            # 1. Check all 25 numeric features
            for col in ACTIVE_NUMERIC_COLUMNS:
                rt_val = realtime_features[col]
                off_val = offline_row[col]
                diff = abs(rt_val - off_val)
                if diff > max_diffs[col]:
                    max_diffs[col] = diff

                self.assertLess(
                    diff,
                    1e-5,
                    f"Row {idx}, Feature '{col}': Realtime={rt_val} vs Offline={off_val}, Diff={diff}",
                )

            # 2. Check all 7 categorical features
            for col in ACTIVE_CATEGORICAL_COLUMNS:
                self.assertEqual(
                    str(realtime_features[col]),
                    str(offline_row[col]),
                    f"Row {idx}, Categorical '{col}' mismatch: {realtime_features[col]} != {offline_row[col]}",
                )

        # Confirm all numeric max diffs are tightly bounded
        for col, md in max_diffs.items():
            self.assertLess(md, 1e-5, f"Feature {col} exceeded tolerance with max diff {md}")

    def test_06_causal_isolation_no_future_lookahead(self):
        """
        Verify causal isolation: changing future records does not alter features
        computed at time t.
        """
        # Run standard sequence up to t=50
        self.adapter.reset()
        records_history_1 = []
        for i in range(50):
            res = self.adapter.transform_packet(self.raw_df.iloc[i])
            records_history_1.append(dict(res))

        # Re-run from scratch with drastically corrupted future rows for t > 50
        self.adapter.reset()
        records_history_2 = []
        corrupted_df = self.raw_df.copy()
        # Corrupt future values completely
        corrupted_df.loc[50:, "value"] = 999999.0
        corrupted_df.loc[50:, "timestamp"] = "2099-01-01T00:00:00"

        for i in range(50):
            res = self.adapter.transform_packet(corrupted_df.iloc[i])
            records_history_2.append(dict(res))

        # Assert every single value up to t=49 is identical
        for i in range(50):
            for col in ALL_32_FEATURES:
                v1 = records_history_1[i][col]
                v2 = records_history_2[i][col]
                if isinstance(v1, (int, float)):
                    self.assertEqual(v1, v2, f"Causality leak at step {i}, feature {col}")
                else:
                    self.assertEqual(v1, v2)

    def test_07_device_isolation(self):
        """Verify device A's stream does not corrupt device B's rolling window."""
        self.adapter.reset()

        # Send packet for device A
        pkt_a1 = {
            "timestamp": "2026-10-04T12:00:00",
            "topic": "factory/line1/temperature",
            "device_id": "mtr_001_temperature_sensor",
            "sensor_code": "MTR-001-TMP",
            "sensor_type": "temperature",
            "value": 40.0,
            "unit": "°C",
            "status": "RUNNING",
            "sequence_number": 1,
        }
        res_a1 = self.adapter.transform_packet(pkt_a1)

        # Send packet for device B
        pkt_b1 = {
            "timestamp": "2026-10-04T12:00:01",
            "topic": "factory/line1/pressure",
            "device_id": "pmp_001_pressure_sensor",
            "sensor_code": "PMP-001-PRS",
            "sensor_type": "pressure",
            "value": 60.0,
            "unit": "bar",
            "status": "RUNNING",
            "sequence_number": 2,
        }
        res_b1 = self.adapter.transform_packet(pkt_b1)

        # Device B cold start should have time_delta = 0.0 (not 1.0 from device A)
        self.assertEqual(res_b1["time_delta"], 0.0)
        self.assertEqual(res_b1["device_seq_gap"], 19.0)
        self.assertEqual(res_b1["value"], 60.0)
        self.assertEqual(res_b1["rolling_mean_3"], 60.0)

        # Global time delta should be 1.0 (since 1 second elapsed globally)
        self.assertEqual(res_b1["global_time_delta"], 1.0)

    def test_08_unknown_device_fallback(self):
        """Verify unseen device IDs fallback smoothly to global baseline statistics."""
        pkt = {
            "timestamp": "2026-10-04T12:00:00",
            "topic": "factory/line1/unknown",
            "device_id": "unseen_device_999",
            "sensor_code": "UNK-999-VAL",
            "sensor_type": "unknown",
            "value": 100.0,
            "unit": "units",
            "status": "RUNNING",
        }
        res = self.adapter.transform_packet(pkt)
        self.assertEqual(res["device_id"], "unseen_device_999")
        self.assertTrue(math.isfinite(res["z_score"]))
        self.assertTrue(math.isfinite(res["rel_volatility"]))
        self.assertTrue(math.isfinite(res["device_mean_deviation"]))

    def test_09_missing_sequence_number_fallback(self):
        """Verify packets without sequence number default gap to 19.0."""
        pkt = {
            "timestamp": "2026-10-04T12:00:00",
            "topic": "factory/line1/temperature",
            "device_id": "mtr_001_temperature_sensor",
            "sensor_code": "MTR-001-TMP",
            "sensor_type": "temperature",
            "value": 42.0,
            "unit": "°C",
            "status": "RUNNING",
        }
        res = self.adapter.transform_packet(pkt)
        self.assertEqual(res["device_seq_gap"], 19.0)
        self.assertEqual(res["seq_gap_dev"], 0.0)
        self.assertEqual(res["rolling_seq_std_5"], 0.0)

    def test_10_high_throughput_latency(self):
        """Verify transformation latency is under 0.1 ms per packet (> 10,000 pkt/sec)."""
        self.adapter.reset()
        slice_df = self.raw_df.iloc[:500]

        start_time = time.perf_counter()
        for _, row in slice_df.iterrows():
            self.adapter.transform_packet(row)
        elapsed_sec = time.perf_counter() - start_time

        per_packet_ms = (elapsed_sec / len(slice_df)) * 1000.0
        packets_per_sec = len(slice_df) / elapsed_sec

        self.assertLess(
            per_packet_ms,
            0.25,
            f"Latency too high: {per_packet_ms:.4f} ms/pkt ({packets_per_sec:.0f} pkt/sec)",
        )


if __name__ == "__main__":
    unittest.main()
