"""
Check Normal Class
"""

from backend.ml.config import LIGHTX_100K
from backend.ml.preprocessing.loader import DatasetLoader


def main():

    loader = DatasetLoader()

    df = loader.load(
        LIGHTX_100K,
    )

    print("\n" + "=" * 70)
    print("NORMAL CLASS")
    print("=" * 70)

    normal = df[df["label"] == 0]

    print(normal.head(20))

    print("\nAttack Type Values\n")

    print(
        normal["attack_type"]
        .value_counts(dropna=False)
    )


if __name__ == "__main__":
    main()