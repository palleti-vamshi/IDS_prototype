"""
TON-IoT Feature Generator

Generates additional engineered features for the
TON-IoT dataset to improve machine learning performance.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TONFeatureGenerator:
    """
    Generates engineered features for TON-IoT.
    """

    def transform(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        logger.info(
            "Generating TON-IoT features..."
        )

        df = df.copy()

        # --------------------------------------------------
        # Missing Sensor Values
        # --------------------------------------------------

        sensor_cols = [
            "sensor_reading_1",
            "sensor_reading_2",
            "sensor_reading_3",
            "sensor_reading_4",
        ]

        df["sensor_missing_count"] = (
            df[sensor_cols]
            .isna()
            .sum(axis=1)
        )

        # --------------------------------------------------
        # Sensor Statistics
        # --------------------------------------------------

        df["sensor_mean"] = (
            df[sensor_cols]
            .mean(axis=1)
        )

        df["sensor_max"] = (
            df[sensor_cols]
            .max(axis=1)
        )

        df["sensor_min"] = (
            df[sensor_cols]
            .min(axis=1)
        )

        df["sensor_std"] = (
            df[sensor_cols]
            .std(axis=1)
            .fillna(0)
        )

        df["sensor_range"] = (
            df["sensor_max"]
            - df["sensor_min"]
        )

        # --------------------------------------------------
        # Byte Features
        # --------------------------------------------------

        df["total_bytes"] = (
            df["src_bytes"].fillna(0)
            + df["dst_bytes"].fillna(0)
        )

        df["byte_difference"] = (
            df["src_bytes"].fillna(0)
            - df["dst_bytes"].fillna(0)
        )

        df["byte_ratio"] = (
            df["src_bytes"].fillna(0)
            / (
                df["dst_bytes"].fillna(0)
                + 1
            )
        )

        # --------------------------------------------------
        # Port Features
        # --------------------------------------------------

        df["same_port"] = (
            (
                df["source_port"]
                ==
                df["destination_port"]
            )
            .fillna(False)
            .astype(int)
        )

        df["port_difference"] = (
            (
                df["source_port"].fillna(0)
                -
                df["destination_port"].fillna(0)
            )
            .abs()
        )

        # --------------------------------------------------
        # Duration Feature
        # --------------------------------------------------

        df["has_duration"] = (
            df["duration"]
            .fillna(0)
            .gt(0)
            .astype(int)
        )

        # --------------------------------------------------
        # Sensor Ratios
        # --------------------------------------------------

        df["sensor_ratio_12"] = (
            df["sensor_reading_1"].fillna(0)
            /
            (
                df["sensor_reading_2"].fillna(0)
                + 1
            )
        )

        df["sensor_ratio_34"] = (
            df["sensor_reading_3"].fillna(0)
            /
            (
                df["sensor_reading_4"].fillna(0)
                + 1
            )
        )

        # --------------------------------------------------
        # Infinite Values
        # --------------------------------------------------

        df.replace(
            [np.inf, -np.inf],
            0,
            inplace=True,
        )

        logger.info(
            "TON-IoT feature generation completed."
        )

        return df