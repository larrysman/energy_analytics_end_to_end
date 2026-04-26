# ===================== STAGE 06 FINANCIAL IMPACT MODEL ===================== #

import numpy as np
import pandas as pd
import os

# LOAD DATA FROM DATA/CLEANED FOLDER
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_path = os.path.join(BASE_DIR, "data", "engineered", "energy_engineered_daily_aggregated_data.csv")
daily_df = pd.read_csv(data_path)
daily_df.head()

def financial_impact_model(daily_df: pd.DataFrame) -> pd.DataFrame:
    NORTH_DAILY = daily_df[daily_df["region"] == "North"].copy()

    complaint_summary = (
    NORTH_DAILY
    .groupby(['region', 'tariff_plan', 'high_outage_day'])
    .agg(
        no_of_days=('customer_id', 'count'),
        complaint_days=('any_complaint', 'sum')
    )
).reset_index()

    complaint_summary['complaint_rate'] = round(
        complaint_summary['complaint_days'] / complaint_summary['no_of_days'],
        2
    )

    high_outage = complaint_summary[complaint_summary['high_outage_day'] == 1].copy()

    fixed_rate = high_outage.loc[high_outage['tariff_plan'] == 'fixed', 'complaint_rate'].iloc[0]
    variable_rate = high_outage.loc[high_outage['tariff_plan'] == 'variable', 'complaint_rate'].iloc[0]

    rate_uplift = variable_rate - fixed_rate
    uplift_factor = variable_rate / fixed_rate

    # NUMBER OF VARIABLE-TARIFF CUSTOMER-DAYS ON HIGH-OUTAGE DAYS
    var_high = NORTH_DAILY[
        (NORTH_DAILY['tariff_plan'] == 'variable') &
        (NORTH_DAILY['high_outage_day'] == 1)
    ]

    n_var_high_days = len(var_high)
    expected_complaints_if_fixed = n_var_high_days * fixed_rate
    actual_complaints_variable = var_high['any_complaint'].sum()

    incremental_complaints = actual_complaints_variable - expected_complaints_if_fixed

    cost_per_complaint = 15.0

    # INCREMENTAL COST OVER THE OBSERVED PERIOD
    incremental_cost_period = incremental_complaints * cost_per_complaint

    # SCALE TO ANNUAL - SIMPLE PROPORTIONAL SCALING
    days_observed = NORTH_DAILY['date'].nunique()
    annual_factor = 365 / days_observed

    incremental_cost_annual = incremental_cost_period * annual_factor

    # CUSTOMER IN THE RISK SEGMENT: VARIABLE TARRIF, HIGH-OUTAGE DAYS WITH COMPLAINTS
    risk_segment = NORTH_DAILY[
        (NORTH_DAILY['tariff_plan'] == 'variable') &
        (NORTH_DAILY['high_outage_day'] == 1) &
        (NORTH_DAILY['any_complaint'] == 1)
    ]

    n_unique_risk_customers = risk_segment['customer_id'].nunique()
    
    p_churn_base = 0.10 
    delta_p_churn = 0.05  
    avr_gross_margin_annual = 120.0    

    # Expected extra churned customers in this segment
    extra_churned_customers = n_unique_risk_customers * delta_p_churn

    # Lost margin from extra churn
    lost_margin_annual = extra_churned_customers * avr_gross_margin_annual

    impact_summary = {
    'days_observed': days_observed,
    'incremental_complaints_period': float(incremental_complaints),
    'incremental_complaint_cost_period_eur': float(incremental_cost_period),
    'incremental_complaint_cost_annual_eur': float(incremental_cost_annual),
    'risk_segment_customers': int(n_unique_risk_customers),
    'extra_churned_customers_est': float(extra_churned_customers),
    'lost_margin_annual_eur': float(lost_margin_annual),
    'total_annual_impact_eur': float(incremental_cost_annual + lost_margin_annual)
}

    return pd.DataFrame([impact_summary]).T.rename(columns={0: 'value (EUR)'})


if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
    data_path = os.path.join(BASE_DIR, "data", "engineered", "energy_engineered_daily_aggregated_data.csv")
    daily_df = pd.read_csv(data_path)
    financial_impact_model(daily_df)
    print("Financial impact model executed successfully!")