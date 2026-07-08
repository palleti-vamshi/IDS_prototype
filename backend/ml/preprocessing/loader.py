"""
Universal Dataset Loader

Loads and validates datasets for LightX-IDS and TON-IoT.
"""

from pathlib import Path
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class DatasetLoader:
    """Universal CSV dataset loader."""

    def load(
        self,
        dataset_path: Path,
        required_columns: list[str] | None = None,
    ) -> pd.DataFrame:
        """
        Load a CSV dataset.

        Parameters
        ----------
        dataset_path : Path
            Dataset path.

        required_columns : list[str], optional
            Required columns to validate.
        """

        logger.info(
            "Loading dataset: %s",
            dataset_path,
        )

        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {dataset_path}"
            )

        df = pd.read_csv(
            dataset_path,
            low_memory=False,
        )

        logger.info(
            f"Loaded {len(df):,} records."
        )

        if required_columns is not None:
            self.validate(
                df,
                required_columns,
            )

        return df

    def validate(
        self,
        df: pd.DataFrame,
        required_columns: list[str],
    ) -> None:
        """
        Validate dataset columns.
        """

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

        logger.info(
            "Dataset validation passed."
        )

    def summary(
        self,
        df: pd.DataFrame,
        target_column: str = "label",
    ) -> None:
        """
        Print dataset summary.
        """

        print("\n================================")
        print("DATASET SUMMARY")
        print("================================")

        print(f"Rows    : {len(df):,}")
        print(f"Columns : {len(df.columns)}")

        print("\nMissing Values")

        print(df.isnull().sum())

        if target_column in df.columns:

            print("\nTarget Distribution")

            print(
                df[target_column]
                .value_counts()
            )