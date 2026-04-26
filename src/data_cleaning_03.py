# ========================== STAGE 03 DATA CLEANING ========================== #

import pandas as pd
from sqlalchemy import text
import yaml

import sys
import os
sys.path.append(os.path.abspath(".."))
from src.mysql_db_utils import get_mysql_engine

# FUNCTION TO LOAD THE DATA FROM MYSQL DATABASE TO A PANDAS DATAFRAME
def data_loaded_from_mysql():
    # ESTABLISH CONNECTION TO MYSQL DATABASE
    engine = get_mysql_engine()

    # READ THE ENTIRE DATA FROM MYSQL DATABASE TO THE NOTEBOOK
    query = text("SELECT * FROM energy_consumption_data;")
    energy_df = pd.read_sql(query, engine)
    return energy_df

# DATA CLEANING FUNCTION
def data_cleaning_pipeline() -> pd.DataFrame:

    df = data_loaded_from_mysql()
    # REMOVE DUPLICATES
    df = df.drop_duplicates().copy()
    # HANDLE NEGATIVE KWH READINGS
    df.loc[df['kwh'] < 0, 'kwh'] = pd.NA
    df['kwh'] = df['kwh'].fillna(df['kwh'].median())
    # HANDLE MISSING VALUES IN THE REGION COLUMN
    df['region'] = df['region'].fillna(df['region'].mode()[0])

    # HANDLE EXTREME OUTLIERS IN THE BILL AMOUNT COLUMN
    upper_cap_bill = df['bill_amount_eur'].quantile(0.995)
    df.loc[df['bill_amount_eur'] > upper_cap_bill, 'bill_amount_eur'] = upper_cap_bill

    return df

if __name__ == "__main__":
    cleaned_data = data_cleaning_pipeline()
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
    data_path = os.path.join(BASE_DIR, "data", "cleaned", "energy_cleaned_data.csv")

    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    cleaned_data.to_csv(data_path, index=False)
    print("Data cleaning completed and saved to CSV successfully!")



