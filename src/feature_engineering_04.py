# ==================== STAGE 04 FEATURE ENGINEERING ==================== #

import numpy as np
import pandas as pd
import os


# LOAD DATA FROM DATA/CLEANED FOLDER
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_input_path = os.path.join(BASE_DIR, "data", "cleaned", "energy_cleaned_data.csv")

# ENGINEERED TIME FEATURES FUNCTION
def engineered_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])
    df["date"] = df["timestamp_utc"].dt.date
    df["hour"] = df["timestamp_utc"].dt.hour
    df["year"] = df["timestamp_utc"].dt.year
    df["month"] = df["timestamp_utc"].dt.month
    df["day_name"] = df["timestamp_utc"].dt.day_name()
    df["is_peak_hour"] = df["hour"].apply(lambda x: 1 if x in [17, 18, 19, 20, 21, 22] else 0)
    df.drop(columns=['timestamp_utc'], inplace=True)
    return df

# DAILY AGGREGATION FUNCTION
def aggregate_to_daily(df: pd.DataFrame) -> pd.DataFrame:

    df = engineered_time_features(df)
    daily = (
        df
        .groupby(['customer_id', 'region', 'tariff_plan', 'is_smart_meter', 'date', 'day_name'])
        .agg(
            daily_kwh=('kwh', 'sum'),
            daily_outage_minutes=('outage_minutes_last_24h', 'max'),
            daily_bill_eur=('bill_amount_eur', 'sum'),
            any_complaint=('complaint_flag', 'max')
        )
        .reset_index()
    )
    daily['high_outage_day'] = (daily['daily_outage_minutes'] >= 15).astype(int)
    return daily

if __name__ == "__main__":
    df = pd.read_csv(data_input_path)
    normal_data_engineered = engineered_time_features(df)
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
    normal_datadata_path = os.path.join(BASE_DIR, "data", "engineered", "energy_engineered_data.csv")
    os.makedirs(os.path.dirname(normal_datadata_path), exist_ok=True)
    normal_data_engineered.to_csv(normal_datadata_path, index=False)

    daily_aggregated_data = aggregate_to_daily(normal_data_engineered)
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
    daily_data_path = os.path.join(BASE_DIR, "data", "engineered", "energy_engineered_daily_aggregated_data.csv")
    os.makedirs(os.path.dirname(daily_data_path), exist_ok=True)
    daily_aggregated_data.to_csv(daily_data_path, index=False)

    print("Feature engineering completed and saved to CSV successfully!")