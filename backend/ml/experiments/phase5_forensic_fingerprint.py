"""
LightX-IDS Phase 5 forensic fingerprint.
Read-only: does not modify dataset, Phase 4 files, models, or reports.
Purpose: produce reproducible fingerprints for the exact controlled-temporal
feature matrix and runtime before Phase 5 is frozen.
"""
from pathlib import Path
import sys, hashlib, json, platform
import numpy as np
import pandas as pd
import xgboost, sklearn

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ml.config import LIGHTX_100K, NUMERIC_COLUMNS, CATEGORICAL_COLUMNS
from backend.ml.feature_engineering.feature_generator import FeatureGenerator
from backend.ml.feature_engineering.feature_selector import FeatureSelector

TRAIN_END, VAL_END = 89000, 90000

def sha_bytes(b): return hashlib.sha256(b).hexdigest()

def frame_fingerprint(df):
    cols = list(df.columns)
    # Stable CSV representation for exact post-selection feature values.
    s = df.loc[:, cols].to_csv(index=False, lineterminator="\n")
    return sha_bytes(s.encode("utf-8"))

def main():
    print("="*90)
    print("LIGHTX-IDS PHASE 5 FORENSIC FINGERPRINT")
    print("="*90)
    print("Runtime:")
    print(" Python:", sys.version.replace("\n"," "))
    print(" Platform:", platform.platform())
    print(" XGBoost:", xgboost.__version__)
    print(" scikit-learn:", sklearn.__version__)
    print(" NumPy:", np.__version__)
    print(" Pandas:", pd.__version__)
    print(" Dataset:", LIGHTX_100K)

    df = pd.read_csv(LIGHTX_100K).sort_values("record_id").reset_index(drop=True)
    fg = FeatureGenerator()
    stream = fg.generate_causal_stream_features(df)

    train = stream.iloc[:TRAIN_END].copy()
    val = stream.iloc[TRAIN_END:VAL_END].copy()
    test = stream.iloc[VAL_END:].copy()

    y_train=train.pop("label"); y_val=val.pop("label"); y_test=test.pop("label")
    fg.fit(train)
    xf_train=fg.transform(train)
    xf_val=fg.transform(val)
    xf_test=fg.transform(test)

    sel=FeatureSelector()
    Xtr,_=sel.split(xf_train.assign(label=y_train.values))
    Xv,_=sel.split(xf_val.assign(label=y_val.values))
    Xt,_=sel.split(xf_test.assign(label=y_test.values))

    print("\nFeature columns:", len(Xtr.columns))
    print("Column order:")
    print("|".join(Xtr.columns))
    print("\nFeature fingerprints:")
    print(" TRAIN:", frame_fingerprint(Xtr))
    print(" VAL  :", frame_fingerprint(Xv))
    print(" TEST :", frame_fingerprint(Xt))

    print("\nSelected numeric columns:")
    print("|".join(c for c in NUMERIC_COLUMNS if c in Xtr.columns))
    print("\nSelected categorical columns:")
    print("|".join(c for c in CATEGORICAL_COLUMNS if c in Xtr.columns))

    print("\nKey feature summaries:")
    for c in ["time_delta","rolling_time_delta_5","rolling_time_delta_std_5",
              "rolling_global_td_10","rolling_global_td_std_10",
              "packet_rate_10","device_seq_gap","seq_gap_dev",
              "rolling_seq_std_5","plant_duplicate_ratio_19",
              "device_mean_deviation","z_score","rel_volatility","stability_anomaly"]:
        if c in Xtr:
            print(f"{c}: train_mean={pd.to_numeric(Xtr[c], errors='coerce').mean():.12g} "
                  f"train_std={pd.to_numeric(Xtr[c], errors='coerce').std():.12g} "
                  f"val_mean={pd.to_numeric(Xv[c], errors='coerce').mean():.12g} "
                  f"test_mean={pd.to_numeric(Xt[c], errors='coerce').mean():.12g}")

    print("\nDataset label fingerprints:")
    print(" train labels:", int(y_train.sum()), int((y_train==0).sum()))
    print(" val labels  :", int(y_val.sum()), int((y_val==0).sum()))
    print(" test labels :", int(y_test.sum()), int((y_test==0).sum()))
    print("\nDone. No files were modified.")

if __name__ == "__main__":
    main()
