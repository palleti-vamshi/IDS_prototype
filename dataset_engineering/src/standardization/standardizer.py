import pandas as pd
import sys

MAPPINGS = {
    "modbus": {
        "date": "date_raw", "time": "timestamp",
        "FC1_Read_Input_Register": "sensor_reading_1",
        "FC2_Read_Discrete_Value": "sensor_reading_2",
        "FC3_Read_Holding_Register": "sensor_reading_3",
        "FC4_Read_Coil": "sensor_reading_4",
        "label": "label", "type": "attack_type"
    },
    "thermostat": {
        "date": "date_raw", "time": "timestamp",
        "current_temperature": "sensor_reading_1",
        "thermostat_status": "sensor_reading_2",
        "label": "label", "type": "attack_type"
    },
    "weather": {
        "date": "date_raw", "time": "timestamp",
        "temperature": "sensor_reading_1",
        "pressure": "sensor_reading_2",
        "humidity": "sensor_reading_3",
        "label": "label", "type": "attack_type"
    },
    "network": {
        "src_ip": "source_ip", "dst_ip": "destination_ip",
        "src_port": "source_port", "dst_port": "destination_port",
        "proto": "protocol", "service": "service",
        "duration": "duration", "src_bytes": "src_bytes",
        "dst_bytes": "dst_bytes",
        "label": "label", "type": "attack_type"
    }
}

def standardize(path, output_path, dataset_key):
    df = pd.read_csv(path)
    mapping = MAPPINGS[dataset_key]
    df = df.rename(columns=mapping)

    # Keep only the columns we actually mapped (drops unmapped extras like http_*, ssl_*)
    keep_cols = list(mapping.values())
    keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[keep_cols]

    df.to_csv(output_path, index=False)
    print(f"Standardized {dataset_key}: {df.shape[0]} rows, {df.shape[1]} columns -> {output_path}")
    print(f"Columns: {df.columns.tolist()}")

if __name__ == "__main__":

    standardize(
        "datasets/processed/Train_Test_IoT_Modbus_clean.csv",
        "datasets/standardized/modbus_final.csv",
        "modbus"
    )

    standardize(
        "datasets/processed/Train_Test_IoT_Thermostat_clean.csv",
        "datasets/standardized/thermostat_final.csv",
        "thermostat"
    )

    standardize(
        "datasets/processed/Train_Test_IoT_Weather_clean.csv",
        "datasets/standardized/weather_final.csv",
        "weather"
    )

    standardize(
        "datasets/processed/train_test_network_clean.csv",
        "datasets/standardized/network_final.csv",
        "network"
    )