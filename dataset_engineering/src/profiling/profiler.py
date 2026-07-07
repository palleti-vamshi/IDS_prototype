import pandas as pd
import sys

def profile(path, label_col="label", type_col="type"):
    df = pd.read_csv(path)
    print("=== SHAPE ===")
    print(df.shape)
    print("\n=== DTYPES ===")
    print(df.dtypes)
    print("\n=== NULLS ===")
    print(df.isnull().sum())
    print("\n=== DUPLICATES ===")
    print(df.duplicated().sum())
    print("\n=== DESCRIBE (numeric) ===")
    print(df.describe())
    if label_col in df.columns:
        print(f"\n=== {label_col} VALUE COUNTS ===")
        print(df[label_col].value_counts())
    if type_col in df.columns:
        print(f"\n=== {type_col} VALUE COUNTS ===")
        print(df[type_col].value_counts())

if __name__ == "__main__":
    path = sys.argv[1]
    profile(path)