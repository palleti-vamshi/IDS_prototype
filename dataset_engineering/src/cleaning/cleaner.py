import pandas as pd
import sys
import numpy as np

# Columns where TON-IoT uses "-" to mean "not applicable" instead of a real NaN
PLACEHOLDER_NULL_COLS = [
    "dns_query", "dns_AA", "dns_RD", "dns_RA", "dns_rejected",
    "ssl_version", "ssl_cipher", "ssl_resumed", "ssl_established",
    "ssl_subject", "ssl_issuer", "http_trans_depth", "http_method",
    "http_uri", "http_version", "http_user_agent",
    "http_orig_mime_types", "http_resp_mime_types",
    "weird_name", "weird_addl", "weird_notice"
]

def clean(path, output_path, has_placeholder_nulls=False):
    df = pd.read_csv(path)
    before = len(df)

    # 1. Drop exact duplicate rows
    df = df.drop_duplicates()
    after_dedup = len(df)

    # 2. Replace "-" placeholder with real NaN, only where relevant
    if has_placeholder_nulls:
        cols_present = [c for c in PLACEHOLDER_NULL_COLS if c in df.columns]
        df[cols_present] = df[cols_present].replace("-", np.nan)

    # 3. Drop rows where label/type is missing or garbage
    df = df.dropna(subset=["label", "type"])
    df = df[df["type"].str.strip() != ""]

    after_clean = len(df)

    df.to_csv(output_path, index=False)

    print(f"Original rows: {before}")
    print(f"After removing duplicates: {after_dedup} (-{before - after_dedup})")
    print(f"After removing invalid labels: {after_clean} (-{after_dedup - after_clean})")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":

    clean(
        "datasets/raw/ton_iot/Train_Test_IoT_Modbus.csv",
        "datasets/processed/Train_Test_IoT_Modbus_clean.csv",
        True
    )

    clean(
        "datasets/raw/ton_iot/Train_Test_IoT_Thermostat.csv",
        "datasets/processed/Train_Test_IoT_Thermostat_clean.csv",
        True
    )

    clean(
        "datasets/raw/ton_iot/Train_Test_IoT_Weather.csv",
        "datasets/processed/Train_Test_IoT_Weather_clean.csv",
        True
    )

    clean(
        "datasets/raw/ton_iot/train_test_network.csv",
        "datasets/processed/train_test_network_clean.csv",
        True
    )
#if __name__ == "__main__":
    #path = sys.argv[1]
   # output_path = sys.argv[2]
   # has_placeholder = "--placeholder-nulls" in sys.argv
    #clean(path, output_path, has_placeholder)#