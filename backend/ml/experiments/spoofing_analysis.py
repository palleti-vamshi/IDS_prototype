"""
LightX-IDS Spoofing Attack Analysis

Compares Spoofing attacks with Normal traffic
to discover distinguishing characteristics.
"""

import pandas as pd

from backend.ml.config import LIGHTX_100K
from backend.ml.preprocessing.loader import DatasetLoader
from backend.ml.feature_engineering.feature_generator import (
    FeatureGenerator,
)


def print_statistics(name, df):

    print("\n" + "=" * 80)
    print(name)
    print("=" * 80)

    features = [
        "value",
        "value_change",
        "time_delta",
        "rolling_mean",
        "rolling_std",
        "rolling_max",
        "rolling_min",
        "percentage_change",
        "z_score",
    ]

    print(
        df[features]
        .describe()
        .round(3)
    )


def main():

    print("\n" + "=" * 80)
    print("LIGHTX-IDS SPOOFING ANALYSIS")
    print("=" * 80)

    loader = DatasetLoader()

    df = loader.load(
        LIGHTX_100K,
    )

    df = FeatureGenerator().transform(
        df,
    )

    normal = df[
        df["label"] == 0
    ]

    spoofing = df[
        df["attack_type"] == "Spoofing Attack"
    ]

    print()

    print(
        f"Normal Samples   : {len(normal)}"
    )

    print(
        f"Spoofing Samples : {len(spoofing)}"
    )

    print_statistics(
        "NORMAL TRAFFIC",
        normal,
    )

    print_statistics(
        "SPOOFING ATTACK",
        spoofing,
    )


if __name__ == "__main__":
    main()