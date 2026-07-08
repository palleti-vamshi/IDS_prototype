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

    def __init__(self):

        REPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.results: list[dict[str, Any]] = []

    def add(
        self,
        result: dict,
    ) -> None:
        """
        Add one benchmark result.
        """

        self.results.append(result)

    def dataframe(
        self,
    ) -> pd.DataFrame:
        """
        Return results as a DataFrame.
        """

        if not self.results:
            return pd.DataFrame()

        df = pd.DataFrame(self.results)

        if "accuracy" in df.columns:

            df = df.sort_values(
                by="accuracy",
                ascending=False,
            )

            df.insert(
                0,
                "rank",
                range(1, len(df) + 1),
            )

        return df.reset_index(drop=True)

    def best_model(
        self,
    ) -> dict | None:
        """
        Return the highest accuracy model.
        """

        if not self.results:
            return None

        return max(
            self.results,
            key=lambda x: x["accuracy"],
        )

    def save(
        self,
        filename: str,
    ) -> tuple[Path, Path]:
        """
        Save benchmark results.

        Returns
        -------
        tuple
            (csv_path, json_path)
        """

        df = self.dataframe()

        csv_path = REPORT_DIR / f"{filename}.csv"
        json_path = REPORT_DIR / f"{filename}.json"

        df.to_csv(
            csv_path,
            index=False,
        )

        with open(
            json_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.results,
                file,
                indent=4,
            )

        logger.info(
            "Results exported successfully."
        )

        return csv_path, json_path

    def clear(
        self,
    ) -> None:
        """
        Clear stored benchmark results.
        """

        self.results.clear()

    def __len__(
        self,
    ) -> int:

        return len(self.results)