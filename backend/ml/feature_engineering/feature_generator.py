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

        df = df.copy()

        # ------------------------------------------------------
        # Timestamp
        # ------------------------------------------------------

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="raise",
        )

        # Stable chronological ordering.
        #
        # record_id is used as a deterministic tie-breaker when
        # multiple observations have the same timestamp.
        sort_columns = ["timestamp"]

        if "record_id" in df.columns:
            sort_columns.append("record_id")

        df.sort_values(
            sort_columns,
            inplace=True,
            kind="mergesort",
        )

        # ------------------------------------------------------
        # Value Difference
        # ------------------------------------------------------

        df["value_change"] = (
            df.groupby("device_id")["value"]
            .diff()
            .fillna(0)
        )

        # ------------------------------------------------------
        # Duplicate Value
        # ------------------------------------------------------

        df["is_duplicate_value"] = (
            df.groupby("device_id")["value"]
            .diff()
            .fillna(1)
            .eq(0)
            .astype(int)
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

        # ------------------------------------------------------
        # Seconds Since Previous Message
        # ------------------------------------------------------

        df["time_delta"] = (
            df.groupby("device_id")["timestamp"]
            .diff()
            .dt.total_seconds()
            .fillna(0)
        )

        # ------------------------------------------------------
        # Rolling Mean
        # ------------------------------------------------------

        df["rolling_mean"] = (
            df.groupby("device_id")["value"]
            .rolling(
                window=self.rolling_window,
                min_periods=1,
            )
            .mean()
            .reset_index(
                level=0,
                drop=True,
            )
        )

        # ------------------------------------------------------
        # Rolling Standard Deviation
        # ------------------------------------------------------

        df["rolling_std"] = (
            df.groupby("device_id")["value"]
            .rolling(
                window=self.rolling_window,
                min_periods=1,
            )
            .std()
            .fillna(0)
            .reset_index(
                level=0,
                drop=True,
            )
        )

        # ------------------------------------------------------
        # Rolling Maximum
        # ------------------------------------------------------

        df["rolling_max"] = (
            df.groupby("device_id")["value"]
            .rolling(
                window=self.rolling_window,
                min_periods=1,
            )
            .max()
            .reset_index(
                level=0,
                drop=True,
            )
        )

        # ------------------------------------------------------
        # Rolling Minimum
        # ------------------------------------------------------

        df["rolling_min"] = (
            df.groupby("device_id")["value"]
            .rolling(
                window=self.rolling_window,
                min_periods=1,
            )
            .min()
            .reset_index(
                level=0,
                drop=True,
            )
        )

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

        grouped = (
            training_df
            .groupby("device_id")["value"]
            .agg(
                mean="mean",
                std="std",
            )
        )

        self.device_statistics = {}

        for device_id, row in grouped.iterrows():

            mean = float(row["mean"])

            std = row["std"]

            if pd.isna(std) or std == 0:
                std = 1.0

            self.device_statistics[device_id] = {
                "mean": mean,
                "std": float(std),
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

        device_mean = (
            df["device_id"]
            .map(
                {
                    device_id: statistics["mean"]
                    for device_id, statistics
                    in self.device_statistics.items()
                }
            )
        )

        device_std = (
            df["device_id"]
            .map(
                {
                    device_id: statistics["std"]
                    for device_id, statistics
                    in self.device_statistics.items()
                }
            )
        )

        # ------------------------------------------------------
        # Unknown devices
        # ------------------------------------------------------
        #
        # If a device appears in validation/test but wasn't
        # present in training, fall back to global training
        # statistics.
        #

        if self.device_statistics:

            global_mean = float(
                np.mean(
                    [
                        statistics["mean"]
                        for statistics
                        in self.device_statistics.values()
                    ]
                )
            )

            global_std = float(
                np.mean(
                    [
                        statistics["std"]
                        for statistics
                        in self.device_statistics.values()
                    ]
                )
            )

            if not np.isfinite(global_std) or global_std == 0:
                global_std = 1.0

        else:

            global_mean = 0.0
            global_std = 1.0

        device_mean = device_mean.fillna(
            global_mean
        )

        device_std = (
            device_std
            .replace(
                [np.inf, -np.inf],
                np.nan,
            )
            .fillna(global_std)
            .replace(0, 1.0)
        )

        # ------------------------------------------------------
        # Device Mean Deviation
        # ------------------------------------------------------

        df["device_mean_deviation"] = (
            df["value"] - device_mean
        )

        # ------------------------------------------------------
        # Device Z-Score
        # ------------------------------------------------------

        df["z_score"] = (
            (df["value"] - device_mean)
            / device_std
        )

        # ------------------------------------------------------
        # Numerical safety
        # ------------------------------------------------------

        engineered_numeric_columns = [
            "value_change",
            "is_duplicate_value",
            "device_message_count",
            "sensor_message_count",
            "time_delta",
            "rolling_mean",
            "rolling_std",
            "rolling_max",
            "rolling_min",
            "percentage_change",
            "device_mean_deviation",
            "z_score",
        ]

        df[engineered_numeric_columns] = (
            df[engineered_numeric_columns]
            .replace(
                [np.inf, -np.inf],
                np.nan,
            )
        )

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