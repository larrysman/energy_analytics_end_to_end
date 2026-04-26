# ================= GENERATING AND LOADING DATA ================= #

import numpy as np
import pandas as pd

def generate_and_load_data(
        no_of_customers: int=100,
        no_of_days: int=60,
        readings_per_day: int=24,
        random_state: int=10
) -> pd.DataFrame:
    np.random.seed(random_state)

    n_rows = no_of_customers * no_of_days * readings_per_day

    # BASE LEVEL CUSTOMER INFORMATION
    customer_ids = np.arange(201, no_of_customers + 201)
    regions = ['North', 'South', 'East', 'West']
    tariff_plans = ['fixed', 'variable']

    # CREATE CUSTOMER ENERGY DATAFRAME
    customer_df = pd.DataFrame({
        'customer_id': customer_ids,
        'region': np.random.choice(regions, size=no_of_customers, p=[0.25, 0.35, 0.2, 0.2]),
        'tariff_plan': np.random.choice(tariff_plans, size=no_of_customers, p=[0.6, 0.4]),
        'is_smart_meter': np.random.choice([0, 1], size=no_of_customers, p=[0.3, 0.7])
    })

    # EXPAND THE DATETIME RANGE FOR THE CUSTOMER ENERGY DATASET FOR TIME SERIES
    date_range = pd.date_range('2026-01-01', periods=no_of_days * readings_per_day, freq='h')
    full_index = pd.MultiIndex.from_product(
        [customer_ids, date_range],
        names=['customer_id', 'timestamp_utc']
    )

    date_df = full_index.to_frame(index=False)

    cust_df = date_df.merge(customer_df, on='customer_id', how='left')

    # SKEWED DISTRIBUTION TO REFLECT REALISTIC ENERGY USAGE PATTERNS - POSITIVELY SKEWED
    base_kwh = np.random.gamma(shape=2.0, scale=0.7, size=len(cust_df))

    # ADD DAILY AND HOURLY PATERNS TO THE BASE KWH
    hour_of_day = cust_df['timestamp_utc'].dt.hour

    # ADD PEAK USAGE IN THE EVENING HOURS (6 PM TO 10 PM)
    cust_df['kwh'] = base_kwh * (1 + 0.3 * ((hour_of_day >= 18) & (hour_of_day <= 22)))

    # ADD REGIONAL DIFFERENCES
    region_factor = cust_df['region'].map({
        'North': 1.1,
        'South': 0.9,
        'East': 1.0,
        'West': 1.05
    })
    cust_df['kwh'] *= region_factor

    # OUTAGE MINUTES IN LAST 24 HOURS BASED ON REGION WITH NORTH AND EAST HAVING MORE OUTAGES
    cust_df['outage_minutes_last_24h'] = np.random.poisson(
        lam=cust_df['region'].map({'North': 15, 'South': 5, 'East': 10, 'West': 7})
    )


    # AGGREGATE TO MONTHLY-ISH BILL AMOUNT - APPROXIMATE PER READING -> ASSUME PRICE PER KWH DEPENDS ON TARIFF AND REGION
    price_per_kwh = (
        cust_df['tariff_plan'].map({'fixed': 0.18, 'variable': 0.16}) *
        cust_df['region'].map({'North': 1.05, 'South': 0.95, 'East': 1.0, 'West': 1.02})
    )
    cust_df['bill_amount_eur'] = cust_df['kwh'] * price_per_kwh


    # SIMULATE COMPLAINTS - BASED ON OUTAGES, TARIFF PLAN, AND REGION -> HIGHER PROBABILITY OF COMPLAINTS FOR VARIABLE TARIFF, HIGH OUTAGES, AND NORTH REGION
    base_prob = 0.02
    cust_df['complaint_prob'] = base_prob + 0.03 * (cust_df['tariff_plan'] == 'variable') + 0.02 * (cust_df['region'] == 'North') + 0.0005 * cust_df['outage_minutes_last_24h']

    cust_df['complaint_prob'] = cust_df['complaint_prob'].clip(0, 0.5)
    cust_df['complaint_flag'] = np.random.binomial(1, cust_df['complaint_prob'])

    # METER_ID - UNIQUE IDENTIFIER FOR THE METER, SIMULATED AS 'MID' + CUSTOMER_ID
    cust_df['meter_id'] = 'MID' + cust_df['customer_id'].astype(str)


    # REORDER COLUMNS FOR BETTER READABILITY
    cust_df = cust_df[[
        'customer_id', 'region', 'meter_id', 'timestamp_utc', 'kwh',
        'tariff_plan', 'is_smart_meter', 'outage_minutes_last_24h',
        'bill_amount_eur', 'complaint_flag'
    ]]

    # FINAL DATASET WITH MESSINESS INJECTED
    df = cust_df.copy()

    # RANDOMLY DROP SOME REGIONS TO SIMULATE MISSING DATA
    mask_missing_region = np.random.rand(len(df)) < 0.02
    df.loc[mask_missing_region, 'region'] = np.nan

    # NEGATIVE KWH VALUES ATTRIBUTED TO SENSOR ERRORS
    mask_negative_kwh = np.random.rand(len(df)) < 0.005
    df.loc[mask_negative_kwh, 'kwh'] *= -1

    # DUPLICATE SOME ROWS TO SIMULATE DUPLICATION
    duplicates = df.sample(frac=0.01, random_state=42)
    df_messy = pd.concat([df, duplicates], ignore_index=True)

    # CREATE OUTLIER BILLS - SOME BILLS ARE 10 TIMES HIGHER THAN EXPECTED
    mask_outlier_bill = np.random.rand(len(df_messy)) < 0.003
    df_messy.loc[mask_outlier_bill, 'bill_amount_eur'] *= 10

    # FINAL MESSY DATASET READY FOR ANALYSIS
    energy_data = df_messy.copy()
    print(energy_data.shape)
    return energy_data


if __name__ == "__main__":
    energy_data = generate_and_load_data()
    print(energy_data.shape)