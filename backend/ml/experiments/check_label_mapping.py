"""
Check Label Mapping
"""

from backend.ml.config import LIGHTX_100K
from backend.ml.preprocessing.loader import DatasetLoader


def main():

    loader = DatasetLoader()

    df = loader.load(
        LIGHTX_100K,
    )

    print("\n" + "=" * 70)
    print("LABEL MAPPING")
    print("=" * 70)

    print(
        df.groupby("label")["attack_type"]
        .value_counts()
    )


if __name__ == "__main__":
    main()