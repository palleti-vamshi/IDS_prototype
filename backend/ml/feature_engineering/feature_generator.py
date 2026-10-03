"""
Feature Generator

Generates additional machine learning features
for the LightX-IDS datasets.

The generator separates:

1. Causal / chronological feature generation
2. Training-only statistical feature fitting

This prevents validation and test observations from
influencing training-derived statistical features.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureGenerator:
    """
    Generate engineered features for LightX-IDS.

    Causal features such as rolling statistics, value changes,
    and time deltas are calculated from the chronological
    stream.

    Device-level statistical features such as mean and standard
    deviation are learned during ``fit()`` and applied during
    ``transform()``.

    This prevents validation/test information from leaking into
    training-derived statistics.
    """

    def __init__(
        self,
        rolling_window: int = 5,
    ) -> None:

        if rolling_window < 1:
            raise ValueError(
                "rolling_window must be at least 1."
            )

        self.rolling_window = rolling_window

        self.device_statistics: dict[str, dict[str, float]] = {}

        self.is_fitted = False

    # ==========================================================
    # INTERNAL VALIDATION
    # ==========================================================

    @staticmethod
    def _validate_input(
        df: pd.DataFrame,
    ) -> None:
        """Validate columns required for feature generation."""

        required_columns = {
            "timestamp",
            "device_id",
            "sensor_type",
            "value",
        }

        missing_columns = sorted(
            required_columns.difference(df.columns)
        )

        if missing_columns:
            raise ValueError(
                "Missing columns required for feature generation: "
                f"{missing_columns}"
            )

    # ==========================================================
    # CAUSAL FEATURES
    # ==========================================================

    def generate_causal_stream_features(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate causal chronological features on the complete
        industrial telemetry stream.

        This method operates exclusively forward in time (using only
        past and current observations). It uses no target information
        and no future observations.
        """
        return self._generate_causal_features(df)

    def _generate_causal_features(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate chronological/stream-derived features.

        These features describe the current observation relative
        to previous observations in the device/sensor stream.

        No target information is used.
        """
        causal_cols = {
            "value_change",
            "abs_value_change",
            "value_accel",
            "time_delta",
            "rolling_time_delta_5",
            "rolling_time_delta_std_5",
            "is_negative_time_delta",
            "global_time_delta",
            "rolling_global_td_10",
            "rolling_global_td_std_10",
            "packet_rate_10",
            "is_duplicate_value",
            "device_seq_gap",
            "seq_gap_dev",
            "rolling_seq_std_5",
            "rolling_mean_3",
            "rolling_std_3",
            "rolling_mean_5",
            "rolling_std_5",
            "rolling_mean_10",
            "rolling_std_10",
            "rolling_range_5",
            "plant_duplicate_ratio_19",
            "percentage_change",
        }

        if causal_cols.issubset(df.columns):
            return df

        df = df.copy()

        # ------------------------------------------------------
        # Timestamp & Value Conversion
        # ------------------------------------------------------
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="raise",
        )
        df["value"] = pd.to_numeric(
            df["value"],
            errors="raise",
        )

        # Stable chronological ordering along arrival order.
        sort_columns = []
        if "record_id" in df.columns:
            sort_columns.append("record_id")
        else:
            sort_columns.append("timestamp")

        df.sort_values(
            sort_columns,
            inplace=True,
            kind="mergesort",
        )

        # ------------------------------------------------------
        # Causal Sequence Features
        # ------------------------------------------------------
        if "sequence_number" in df.columns:
            df["device_seq_gap"] = (
                df.groupby("device_id")["sequence_number"]
                .diff()
                .fillna(19.0)
            )
            df["seq_gap_dev"] = (df["device_seq_gap"] - 19.0).abs()
            df["rolling_seq_std_5"] = (
                df.groupby("device_id")["device_seq_gap"]
                .rolling(window=self.rolling_window, min_periods=1)
                .std()
                .fillna(0)
                .reset_index(level=0, drop=True)
            )
        else:
            df["device_seq_gap"] = 19.0
            df["seq_gap_dev"] = 0.0
            df["rolling_seq_std_5"] = 0.0

        # ------------------------------------------------------
        # Causal Timing Features
        # ------------------------------------------------------
        df["time_delta"] = (
            df.groupby("device_id")["timestamp"]
            .diff()
            .dt.total_seconds()
            .fillna(0)
        )
        df["rolling_time_delta_5"] = (
            df.groupby("device_id")["time_delta"]
            .rolling(window=self.rolling_window, min_periods=1)
            .mean()
            .fillna(0)
            .reset_index(level=0, drop=True)
        )
        df["rolling_time_delta_std_5"] = (
            df.groupby("device_id")["time_delta"]
            .rolling(window=self.rolling_window, min_periods=1)
            .std()
            .fillna(0)
            .reset_index(level=0, drop=True)
        )
        df["is_negative_time_delta"] = (df["time_delta"] < 0).astype(int)

        df["global_time_delta"] = (
            df["timestamp"]
            .diff()
            .dt.total_seconds()
            .fillna(0)
        )
        df["rolling_global_td_10"] = (
            df["global_time_delta"]
            .rolling(window=10, min_periods=1)
            .mean()
            .fillna(0)
        )
        df["rolling_global_td_std_10"] = (
            df["global_time_delta"]
            .rolling(window=10, min_periods=1)
            .std()
            .fillna(0)
        )
        df["packet_rate_10"] = 1.0 / (df["rolling_global_td_10"] + 1e-4)

        # ------------------------------------------------------
        # Causal Value Dynamics
        # ------------------------------------------------------
        df["value_change"] = (
            df.groupby("device_id")["value"]
            .diff()
            .fillna(0)
        )
        df["abs_value_change"] = df["value_change"].abs()
        df["value_accel"] = (
            df.groupby("device_id")["value_change"]
            .diff()
            .fillna(0)
        )
        df["is_duplicate_value"] = (
            df["value_change"].eq(0).astype(int)
        )

        # Plant-wide duplicate ratio over 1 plant cycle (19 sensors)
        df["plant_duplicate_ratio_19"] = (
            df["is_duplicate_value"]
            .rolling(window=19, min_periods=1)
            .mean()
            .fillna(0)
        )

        # ------------------------------------------------------
        # Multi-Window Rolling Statistics
        # ------------------------------------------------------
        for w in [3, 5, 10]:
            df[f"rolling_mean_{w}"] = (
                df.groupby("device_id")["value"]
                .rolling(window=w, min_periods=1)
                .mean()
                .reset_index(level=0, drop=True)
            )
            df[f"rolling_std_{w}"] = (
                df.groupby("device_id")["value"]
                .rolling(window=w, min_periods=1)
                .std()
                .fillna(0)
                .reset_index(level=0, drop=True)
            )

        df["rolling_mean"] = df["rolling_mean_5"]
        df["rolling_std"] = df["rolling_std_5"]
        df["rolling_max"] = (
            df.groupby("device_id")["value"]
            .rolling(window=self.rolling_window, min_periods=1)
            .max()
            .reset_index(level=0, drop=True)
        )
        df["rolling_min"] = (
            df.groupby("device_id")["value"]
            .rolling(window=self.rolling_window, min_periods=1)
            .min()
            .reset_index(level=0, drop=True)
        )
        df["rolling_range_5"] = df["rolling_max"] - df["rolling_min"]

        # ------------------------------------------------------
        # Percentage Change
        # ------------------------------------------------------
        df["percentage_change"] = (
            df.groupby("device_id")["value"]
            .pct_change()
            .replace(
                [np.inf, -np.inf],
                np.nan,
            )
            .fillna(0)
        )

        # ------------------------------------------------------
        # Device Message Count
        # ------------------------------------------------------
        df["device_message_count"] = (
            df.groupby("device_id")
            .cumcount()
            + 1
        )

        # ------------------------------------------------------
        # Sensor Message Count
        # ------------------------------------------------------
        df["sensor_message_count"] = (
            df.groupby("sensor_type")
            .cumcount()
            + 1
        )

        return df

    # ==========================================================
    # TRAINING STATISTICS
    # ==========================================================

    def fit(
        self,
        df: pd.DataFrame,
    ) -> "FeatureGenerator":
        """
        Learn device-level statistics from training data only.

        Parameters
        ----------
        df : pandas.DataFrame
            Training dataframe.

        Returns
        -------
        FeatureGenerator
            Fitted generator.
        """
        self._validate_input(df)

        training_df = df.copy()

        training_df["value"] = pd.to_numeric(
            training_df["value"],
            errors="raise",
        )

        grouped = training_df.groupby("device_id")
        means = grouped["value"].mean()
        stds = grouped["value"].std().fillna(1.0).replace(0, 1.0)

        # Historical duplicate rate in training set
        if "is_duplicate_value" in training_df.columns:
            dup_rates = grouped["is_duplicate_value"].mean().fillna(0.5)
        else:
            val_diffs = grouped["value"].diff().fillna(1)
            dup_rates = (val_diffs == 0).groupby(training_df["device_id"]).mean().fillna(0.5)

        self.device_statistics = {}

        for device_id in means.index:
            std_val = float(stds[device_id])
            if not np.isfinite(std_val) or std_val == 0:
                std_val = 1.0

            self.device_statistics[device_id] = {
                "mean": float(means[device_id]),
                "std": std_val,
                "dup_rate": float(dup_rates.get(device_id, 0.5)),
            }

        self.is_fitted = True

        logger.info(
            "Fitted device statistics for %d devices "
            "using training data only.",
            len(self.device_statistics),
        )

        return self

    # ==========================================================
    # APPLY FEATURES
    # ==========================================================

    def transform(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate engineered features.

        For fitted generators, device-level statistical features
        use statistics learned during ``fit()``.

        Parameters
        ----------
        df : pandas.DataFrame

        Returns
        -------
        pandas.DataFrame
        """
        self._validate_input(df)

        logger.info(
            "Generating LightX-IDS features..."
        )

        df = df.copy()

        # ------------------------------------------------------
        # Causal / chronological features
        # ------------------------------------------------------
        df = self._generate_causal_features(df)

        # ------------------------------------------------------
        # Device-level statistical features
        # ------------------------------------------------------
        if not self.is_fitted:
            raise RuntimeError(
                "FeatureGenerator must be fitted on training "
                "data before transform() is called."
            )

        if self.device_statistics:
            global_mean = float(
                np.mean([s["mean"] for s in self.device_statistics.values()])
            )
            global_std = float(
                np.mean([s["std"] for s in self.device_statistics.values()])
            )
            if not np.isfinite(global_std) or global_std == 0:
                global_std = 1.0
        else:
            global_mean = 0.0
            global_std = 1.0

        device_mean = (
            df["device_id"]
            .map({d: s["mean"] for d, s in self.device_statistics.items()})
            .fillna(global_mean)
        )

        device_std = (
            df["device_id"]
            .map({d: s["std"] for d, s in self.device_statistics.items()})
            .replace([np.inf, -np.inf], np.nan)
            .fillna(global_std)
            .replace(0, 1.0)
        )

        device_dup_rate = (
            df["device_id"]
            .map({d: s.get("dup_rate", 0.5) for d, s in self.device_statistics.items()})
            .fillna(0.5)
        )

        # ------------------------------------------------------
        # Device Deviations & Baselines
        # ------------------------------------------------------
        df["device_mean_deviation"] = df["value"] - device_mean
        df["z_score"] = (df["value"] - device_mean) / device_std
        df["rel_volatility"] = df["rolling_std_5"] / device_std
        df["stability_anomaly"] = df["is_duplicate_value"] * (1.0 - device_dup_rate)

        # ------------------------------------------------------
        # Numerical safety
        # ------------------------------------------------------
        engineered_numeric_columns = [
            "value_change",
            "abs_value_change",
            "value_accel",
            "time_delta",
            "rolling_time_delta_5",
            "rolling_time_delta_std_5",
            "is_negative_time_delta",
            "global_time_delta",
            "rolling_global_td_10",
            "rolling_global_td_std_10",
            "packet_rate_10",
            "is_duplicate_value",
            "device_seq_gap",
            "seq_gap_dev",
            "rolling_seq_std_5",
            "rolling_mean_3",
            "rolling_std_3",
            "rolling_mean_5",
            "rolling_std_5",
            "rolling_mean_10",
            "rolling_std_10",
            "rolling_mean",
            "rolling_std",
            "rolling_max",
            "rolling_min",
            "rolling_range_5",
            "plant_duplicate_ratio_19",
            "percentage_change",
            "device_mean_deviation",
            "z_score",
            "rel_volatility",
            "stability_anomaly",
        ]

        df[engineered_numeric_columns] = (
            df[engineered_numeric_columns]
            .replace(
                [np.inf, -np.inf],
                np.nan,
            )
            .fillna(0)
        )

        logger.info(
            "Feature generation completed."
        )

        return df

        logger.info(
            "Feature generation completed."
        )

        return df

    # ==========================================================
    # FIT + TRANSFORM
    # ==========================================================

    def fit_transform(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Fit the generator and transform the same dataframe.

        This method is intended ONLY for the training split.

        Validation and test data must use transform() after
        fitting on training data.
        """

        self.fit(df)

        return self.transform(df)