"""
LightX-IDS Result Manager

Stores, ranks and exports benchmark results.
"""

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from backend.ml.config import REPORT_DIR

logger = logging.getLogger(__name__)


class ResultManager:
    """
    Stores benchmark results and exports them
    as CSV and JSON.
    """

    # ---------------------------------------------------------
    # Preferred benchmark columns
    # ---------------------------------------------------------

    RESULT_COLUMNS = [
        # Identification
        "model",
        "dataset",
        "benchmark",

        # Dataset information
        "dataset_size",
        "train_size",
        "validation_size",
        "test_size",
        "feature_count",

        # Configuration
        "random_state",
        "split_protocol",
        "threshold_metric",

        # Threshold
        "best_threshold",
        "validation_threshold_score",

        # Core classification metrics
        "accuracy",
        "precision",
        "recall",
        "f1_score",

        # Probability-based metrics
        "roc_auc",
        "pr_auc",

        # IDS error metrics
        "fpr",
        "fnr",

        # Confusion matrix components
        "tn",
        "fp",
        "fn",
        "tp",

        # Performance
        "training_time",
        "prediction_time",
        "model_size_mb",
    ]

    def __init__(self):

        REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.results: list[dict[str, Any]] = []

    # ---------------------------------------------------------
    # Add Result
    # ---------------------------------------------------------

    def add(
        self,
        result: dict,
    ) -> None:
        """
        Add one benchmark result.
        """

        if not isinstance(
            result,
            dict,
        ):
            raise TypeError(
                "Benchmark result must be a dictionary."
            )

        self.results.append(
            dict(result)
        )

    # ---------------------------------------------------------
    # DataFrame
    # ---------------------------------------------------------

    def dataframe(
        self,
    ) -> pd.DataFrame:
        """
        Return benchmark results as a DataFrame.

        Known benchmark fields are kept in a stable order.
        Additional fields are preserved after the known fields.
        """

        if not self.results:

            return pd.DataFrame()

        df = pd.DataFrame(
            self.results
        )

        # -----------------------------------------------------
        # Stable column ordering
        # -----------------------------------------------------

        ordered_columns = [
            column
            for column in self.RESULT_COLUMNS
            if column in df.columns
        ]

        additional_columns = [
            column
            for column in df.columns
            if column not in ordered_columns
        ]

        df = df[
            ordered_columns
            + additional_columns
        ]

        # -----------------------------------------------------
        # Ranking
        # -----------------------------------------------------

        if "accuracy" in df.columns:

            df = df.sort_values(
                by=[
                    "accuracy",
                    "f1_score"
                    if "f1_score" in df.columns
                    else "accuracy",
                ],
                ascending=[
                    False,
                    False,
                ],
                kind="mergesort",
            )

            df.insert(
                0,
                "rank",
                range(
                    1,
                    len(df) + 1,
                ),
            )

        return df.reset_index(
            drop=True
        )

    # ---------------------------------------------------------
    # Best Model
    # ---------------------------------------------------------

    def best_model(
        self,
    ) -> dict | None:
        """
        Return the model with the highest accuracy.

        This method is retained for backward compatibility
        with the existing benchmark workflow.
        """

        if not self.results:

            return None

        return max(
            self.results,
            key=lambda x: (
                x.get(
                    "accuracy",
                    float("-inf"),
                ),
                x.get(
                    "f1_score",
                    float("-inf"),
                ),
            ),
        )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    def save(
        self,
        filename: str,
    ) -> tuple[Path, Path]:
        """
        Save benchmark results.

        Returns
        -------
        tuple[Path, Path]
            (csv_path, json_path)
        """

        df = self.dataframe()

        csv_path = (
            REPORT_DIR
            / f"{filename}.csv"
        )

        json_path = (
            REPORT_DIR
            / f"{filename}.json"
        )

        # -----------------------------------------------------
        # CSV
        # -----------------------------------------------------

        df.to_csv(
            csv_path,
            index=False,
        )

        # -----------------------------------------------------
        # JSON
        # -----------------------------------------------------

        with open(
            json_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.results,
                file,
                indent=4,
                default=str,
            )

        logger.info(
            "Results exported successfully:"
        )

        logger.info(
            "CSV: %s",
            csv_path,
        )

        logger.info(
            "JSON: %s",
            json_path,
        )

        return (
            csv_path,
            json_path,
        )

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(
        self,
    ) -> None:
        """
        Clear stored benchmark results.
        """

        self.results.clear()

    # ---------------------------------------------------------
    # Length
    # ---------------------------------------------------------

    def __len__(
        self,
    ) -> int:

        return len(
            self.results
        )