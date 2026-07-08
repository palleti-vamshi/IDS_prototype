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
        # Sort chronologically
        # -----------------------------------------

        df["timestamp"] = pd.to_datetime(df["timestamp"])

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

        logger.info("Feature generation completed.")

        return df