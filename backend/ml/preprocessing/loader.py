"""
Dataset Loader
Loads and validates datasets for LightX-IDS.
"""

from pathlib import Path
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class DatasetLoader:
    """Loads CSV datasets."""

    REQUIRED_COLUMNS = [
        "timestamp",
        "topic",
        "device_id",
        "sensor_type",
        "value",
        "unit",
        "status",
        "attack_type",
        "label",
        "source",
        "sequence_number",
    ]

    def load(self, dataset_path: Path) -> pd.DataFrame:
        """
        Load a CSV dataset.

        Args:
            dataset_path: Path to dataset

        Returns:
            Pandas DataFrame
        """

        logger.info(f"Loading dataset: {dataset_path}")

        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {dataset_path}"
            )

        df = pd.read_csv(dataset_path)

        logger.info(
            f"Loaded {len(df):,} records."
        )

        self.validate(df)

        return df

    def validate(self, df: pd.DataFrame) -> None:
        """
        Validate dataset columns.
        """

        missing = []

        for column in self.REQUIRED_COLUMNS:

            if column not in df.columns:
                missing.append(column)

        if missing:

            raise ValueError(
                f"Missing columns: {missing}"
            )

        logger.info("Dataset validation passed.")

    def summary(self, df: pd.DataFrame) -> None:
        """
        Print dataset summary.
        """

        print("\n==============================")
        print("DATASET SUMMARY")
        print("==============================")

        print(f"Records : {len(df):,}")
        print(f"Columns : {len(df.columns)}")

        print("\nColumns:")

        for column in df.columns:
            print(f" - {column}")

        print("\nMissing Values:")
        print(df.isnull().sum())

        print("\nAttack Distribution:")
        print(
            df["attack_type"]
            .fillna("Normal")
            .value_counts()
        )

        print("\nLabel Distribution:")
        print(
            df["label"].value_counts()
        )