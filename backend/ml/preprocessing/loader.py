"""
Universal Dataset Loader

Loads and validates datasets for LightX-IDS and TON-IoT.
"""

from pathlib import Path
import logging

import pandas as pd


logger = logging.getLogger(__name__)


class DatasetLoader:
    """
    Universal CSV dataset loader.
    """

    # ========================================================
    # LOAD
    # ========================================================

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

        Returns
        -------
        pandas.DataFrame
            Loaded dataset.
        """

        dataset_path = Path(
            dataset_path
        )

        logger.info(
            "Loading dataset: %s",
            dataset_path,
        )

        # ----------------------------------------------------
        # File existence
        # ----------------------------------------------------

        if not dataset_path.exists():

            raise FileNotFoundError(
                f"Dataset not found: {dataset_path}"
            )

        if not dataset_path.is_file():

            raise ValueError(
                f"Dataset path is not a file: "
                f"{dataset_path}"
            )

        # ----------------------------------------------------
        # Read CSV
        # ----------------------------------------------------

        try:

            df = pd.read_csv(
                dataset_path,
                low_memory=False,
            )

        except Exception as error:

            logger.exception(
                "Failed to read dataset: %s",
                dataset_path,
            )

            raise RuntimeError(
                f"Unable to read dataset: "
                f"{dataset_path}"
            ) from error

        logger.info(
            "Loaded %s records.",
            f"{len(df):,}",
        )

        # ----------------------------------------------------
        # Empty dataset
        # ----------------------------------------------------

        if df.empty:

            raise ValueError(
                f"Dataset is empty: {dataset_path}"
            )

        # ----------------------------------------------------
        # Duplicate column names
        # ----------------------------------------------------

        duplicate_columns = (
            df.columns[
                df.columns.duplicated()
            ]
            .tolist()
        )

        if duplicate_columns:

            raise ValueError(
                "Dataset contains duplicate "
                f"column names: {duplicate_columns}"
            )

        # ====================================================
        # REQUIRED COLUMN VALIDATION
        # ====================================================

        if required_columns is not None:

            self.validate(
                df,
                required_columns,
            )

        return df

    # ========================================================
    # VALIDATE
    # ========================================================

    def validate(
        self,
        df: pd.DataFrame,
        required_columns: list[str],
    ) -> None:
        """
        Validate required dataset columns and core
        LightX-IDS data integrity.
        """

        if not isinstance(
            df,
            pd.DataFrame,
        ):

            raise TypeError(
                "Dataset must be a pandas DataFrame."
            )

        # ----------------------------------------------------
        # Required columns
        # ----------------------------------------------------

        missing = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing:

            raise ValueError(
                f"Missing required columns: {missing}"
            )

        # ----------------------------------------------------
        # Completely missing required columns
        # ----------------------------------------------------

        empty_columns = [
            column
            for column in required_columns
            if df[column].isna().all()
        ]

        if empty_columns:

            raise ValueError(
                "Required columns contain only null values: "
                f"{empty_columns}"
            )

        # ----------------------------------------------------
        # LightX-IDS target validation
        # ----------------------------------------------------

        if "label" in df.columns:

            if df["label"].isna().any():

                raise ValueError(
                    "LightX-IDS label column contains "
                    "null values."
                )

            labels = set(
                df["label"]
                .unique()
                .tolist()
            )

            if not labels.issubset(
                {0, 1}
            ):

                raise ValueError(
                    "LightX-IDS label column must contain "
                    "only binary values 0 and 1. "
                    f"Found: {sorted(labels)}"
                )

        logger.info(
            "Dataset validation passed."
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    def summary(
        self,
        df: pd.DataFrame,
        target_column: str = "label",
    ) -> None:
        """
        Print dataset summary.
        """

        print(
            "\n================================"
        )

        print(
            "DATASET SUMMARY"
        )

        print(
            "================================"
        )

        print(
            f"Rows    : {len(df):,}"
        )

        print(
            f"Columns : {len(df.columns)}"
        )

        print(
            "\nMissing Values"
        )

        print(
            df.isnull().sum()
        )

        if target_column in df.columns:

            print(
                "\nTarget Distribution"
            )

            print(
                df[target_column]
                .value_counts()
                .sort_index()
            )