"""
Check Dataset Class Distribution
"""

from backend.ml.config import LIGHTX_100K
from backend.ml.preprocessing.loader import DatasetLoader


def main():

    loader = DatasetLoader()

    df = loader.load(
        LIGHTX_100K,
    )

    print("\n" + "=" * 60)
    print("DATASET CLASS DISTRIBUTION")
    print("=" * 60)

    print(df["label"].value_counts())

    print("\nPercentage:\n")

    print(
        (
            df["label"]
            .value_counts(normalize=True)
            * 100
        ).round(2)
    )


if __name__ == "__main__":
    main()