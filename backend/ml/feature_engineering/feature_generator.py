"""
Feature Generator

Generates additional machine learning features
for the LightX-IDS datasets.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class FeatureGenerator:
    """Generate engineered features."""

    def transform(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate additional ML features.

        Parameters
        ----------
        df : pandas.DataFrame

        Returns
        -------
        pandas.DataFrame
        """

        logger.info("Generating features...")

        df = df.copy()

        # -----------------------------------------
        # Sort Chronologically
        # -----------------------------------------

        df["timestamp"] = pd.to_datetime(
            df["timestamp"]
        )

        df.sort_values(
            "timestamp",
            inplace=True,
        )

        # -----------------------------------------
        # Value Difference
        # -----------------------------------------

        df["value_change"] = (
            df.groupby("device_id")["value"]
            .diff()
            .fillna(0)
        )

        # -----------------------------------------
        # Duplicate Value
        # -----------------------------------------

        df["is_duplicate_value"] = (
            df.groupby("device_id")["value"]
            .diff()
            .fillna(1)
            .eq(0)
            .astype(int)
        )

        # -----------------------------------------
        # Device Message Count
        # -----------------------------------------

        df["device_message_count"] = (
            df.groupby("device_id")
            .cumcount()
            + 1
        )

        # -----------------------------------------
        # Sensor Message Count
        # -----------------------------------------

        df["sensor_message_count"] = (
            df.groupby("sensor_type")
            .cumcount()
            + 1
        )

        # -----------------------------------------
        # Seconds Since Previous Message
        # -----------------------------------------

        df["time_delta"] = (
            df.groupby("device_id")["timestamp"]
            .diff()
            .dt.total_seconds()
            .fillna(0)
        )

        # -----------------------------------------
        # Rolling Mean
        # -----------------------------------------

        df["rolling_mean"] = (
            df.groupby("device_id")["value"]
            .rolling(
                window=5,
                min_periods=1,
            )
            .mean()
            .reset_index(
                level=0,
                drop=True,
            )
        )

        # -----------------------------------------
        # Rolling Standard Deviation
        # -----------------------------------------

        df["rolling_std"] = (
            df.groupby("device_id")["value"]
            .rolling(
                window=5,
                min_periods=1,
            )
            .std()
            .fillna(0)
            .reset_index(
                level=0,
                drop=True,
            )
        )

        # -----------------------------------------
        # Rolling Maximum
        # -----------------------------------------

        df["rolling_max"] = (
            df.groupby("device_id")["value"]
            .rolling(
                window=5,
                min_periods=1,
            )
            .max()
            .reset_index(
                level=0,
                drop=True,
            )
        )

        # -----------------------------------------
        # Rolling Minimum
        # -----------------------------------------

        df["rolling_min"] = (
            df.groupby("device_id")["value"]
            .rolling(
                window=5,
                min_periods=1,
            )
            .min()
            .reset_index(
                level=0,
                drop=True,
            )
        )

        # -----------------------------------------
        # Percentage Change
        # -----------------------------------------

        df["percentage_change"] = (
            df.groupby("device_id")["value"]
            .pct_change()
            .fillna(0)
        )

        # -----------------------------------------
        # Device-wise Z-Score
        # -----------------------------------------

        device_mean = (
            df.groupby("device_id")["value"]
            .transform("mean")
        )

        device_std = (
            df.groupby("device_id")["value"]
            .transform("std")
            .replace(0, 1)
            .fillna(1)
        )

        df["z_score"] = (
            (df["value"] - device_mean)
            / device_std
        )

        logger.info(
            "Feature generation completed."
        )

        return df