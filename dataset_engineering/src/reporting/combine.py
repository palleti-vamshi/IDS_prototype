import pandas as pd

files = [
    "datasets/standardized/modbus_final.csv",
    "datasets/standardized/thermostat_final.csv",
    "datasets/standardized/weather_final.csv",
    "datasets/standardized/network_final.csv"
]

dfs = [pd.read_csv(f) for f in files]
combined = pd.concat(dfs, ignore_index=True, sort=False)
combined.to_csv("datasets/standardized/lightx_combined.csv", index=False)

print(f"Combined shape: {combined.shape}")
print(f"Columns: {combined.columns.tolist()}")
print(combined["attack_type"].value_counts())