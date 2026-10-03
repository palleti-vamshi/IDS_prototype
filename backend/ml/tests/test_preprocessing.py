"""
Test the complete preprocessing pipeline.
"""

from backend.ml.config import LIGHTX_1K
from backend.ml.preprocessing.loader import DatasetLoader
from backend.ml.feature_engineering.feature_selector import FeatureSelector
from backend.ml.preprocessing.transformer import DatasetTransformer
from backend.ml.preprocessing.splitter import DatasetSplitter


def main():

    print("\n====================================")
    print("LIGHTX-IDS PREPROCESSING TEST")
    print("====================================\n")

    # -----------------------------
    # Load Dataset
    # -----------------------------

    loader = DatasetLoader()

    df = loader.load(LIGHTX_1K)

    loader.summary(df)

    print("\n✅ Dataset Loaded")

    # -----------------------------
    # Feature Engineering
    # -----------------------------

    from backend.ml.feature_engineering.feature_generator import FeatureGenerator

    generator = FeatureGenerator()
    df_features = generator.fit_transform(df)

    print("✅ Feature Generation Complete")

    # -----------------------------
    # Feature Selection
    # -----------------------------

    selector = FeatureSelector()

    X, y = selector.split(df_features)

    print("✅ Feature Selection Complete")

    # -----------------------------
    # Transformer
    # -----------------------------

    transformer = DatasetTransformer().build()

    print("✅ Transformer Built")

    # -----------------------------
    # Dataset Split
    # -----------------------------

    splitter = DatasetSplitter()

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = splitter.split(X, y)

    print("✅ Dataset Split Complete")

    # -----------------------------
    # Transform Verification
    # -----------------------------

    X_train_transformed = transformer.fit_transform(X_train)
    X_test_transformed = transformer.transform(X_test)

    print(f"Transformed train shape: {X_train_transformed.shape}")
    print(f"Transformed test shape : {X_test_transformed.shape}")
    print("✅ Preprocessing Transformation Complete")

    print("\n====================================")

    print(f"Training Samples   : {len(X_train)}")
    print(f"Validation Samples : {len(X_val)}")
    print(f"Testing Samples    : {len(X_test)}")

    print("====================================")

    print("\n🎉 PREPROCESSING PIPELINE PASSED")


if __name__ == "__main__":
    main()