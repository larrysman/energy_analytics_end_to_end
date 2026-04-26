# ==================== STAGE 07 SENSITIVITY ANALYSIS ==================== #

import numpy as np
import pandas as pd
import os

from torchinfo import summary


# LOAD DATA FROM DATA/CLEANED FOLDER
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
data_path = os.path.join(BASE_DIR, "data", "engineered", "energy_engineered_daily_aggregated_data.csv")
daily_df = pd.read_csv(data_path)
daily_df.head()


def sensitivity_analysis_pipeline(daily_df: pd.DataFrame):

    # PREPARE THE BASELINE FINANCIAL IMPACT MODEL RESULTS
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

    # HIGH-OUTAGE DAYS: COMPLAINT RATES BY TARIFF PLAN
    high_outage = complaint_summary[complaint_summary['high_outage_day'] == 1].copy()
    fixed_rate = high_outage.loc[high_outage['tariff_plan'] == 'fixed', 'complaint_rate'].iloc[0]
    variable_rate = high_outage.loc[high_outage['tariff_plan'] == 'variable', 'complaint_rate'].iloc[0]

    # NUMBER OF VARIABLE-TARIFF CUSTOMER-DAYS ON HIGH-OUTAGE DAYS
    var_high = NORTH_DAILY[
        (NORTH_DAILY['tariff_plan'] == 'variable') &
        (NORTH_DAILY['high_outage_day'] == 1)
    ]

    n_var_high_days = len(var_high)
    expected_complaints_if_fixed = n_var_high_days * fixed_rate
    actual_complaints_variable = var_high['any_complaint'].sum()

    incremental_complaints = actual_complaints_variable - expected_complaints_if_fixed

    # SCALE TO ANNUAL - SIMPLE PROPORTIONAL SCALING
    days_observed = NORTH_DAILY['date'].nunique()
    annual_factor = 365 / days_observed

    # CUSTOMER IN THE RISK SEGMENT: VARIABLE TARRIF, HIGH-OUTAGE DAYS WITH COMPLAINTS
    risk_segment = NORTH_DAILY[
        (NORTH_DAILY['tariff_plan'] == 'variable') &
        (NORTH_DAILY['high_outage_day'] == 1) &
        (NORTH_DAILY['any_complaint'] == 1)
    ]

    n_unique_risk_customers = risk_segment['customer_id'].nunique()

    # DEFINE SENSITIVITY SCENARIOS - VARYING THE COST PER COMPLAINT
    # €10 -> €30
    cost_per_complaint_range = np.arange(10, 31, 5)
    # 2% -> 8%
    delta_churn_range = np.arange(0.02, 0.081, 0.02)
    # €80 -> €160    
    margin_range = np.arange(80, 161, 20)

    # COMPUTE SENSITIVITY GRID
    results = []

    for cost_per_complaint in cost_per_complaint_range:
        for delta_p_churn in delta_churn_range:
            for margin_annual in margin_range:
                
                # Complaint-handling cost
                incremental_cost_period = incremental_complaints * cost_per_complaint
                incremental_cost_annual = incremental_cost_period * annual_factor
                
                # Churn impact
                extra_churned_customers = n_unique_risk_customers * delta_p_churn
                lost_margin_annual = extra_churned_customers * margin_annual
                
                # Total impact
                total_impact = round(incremental_cost_annual + lost_margin_annual,2)
                
                results.append({
                    'cost_per_complaint': cost_per_complaint,
                    'delta_churn': delta_p_churn,
                    'annual_margin': margin_annual,
                    'complaint_cost_annual': incremental_cost_annual,
                    'lost_margin_annual': lost_margin_annual,
                    'total_annual_impact': total_impact
                })

    sensitivity_df = pd.DataFrame(results)

    # SUMMARIZE THE SENSITVITY ANALYSIS RESULTS
    summary = {
    'min_impact_eur': sensitivity_df['total_annual_impact'].min(),
    'median_impact_eur': sensitivity_df['total_annual_impact'].median(),
    'max_impact_eur': sensitivity_df['total_annual_impact'].max()
}

    print(pd.DataFrame([summary]).T.rename(columns={0: 'value (€)'}))

    # IDENTIFY THE MOST SENSITIVE PARAMETERS
    impact_by_variable = sensitivity_df.groupby('cost_per_complaint')['total_annual_impact'].mean()
    impact_by_churn = sensitivity_df.groupby('delta_churn')['total_annual_impact'].mean()
    impact_by_margin = sensitivity_df.groupby('annual_margin')['total_annual_impact'].mean()

    print(f"Impact by variable cost = {impact_by_variable}")
    print("==============================================")
    print(f"Impact by churn rate = {impact_by_churn}")
    print("==============================================")
    print(f"Impact by margin = {impact_by_margin}")

    # SENSITIVITY TABLE
    pivot = sensitivity_df.pivot_table(
    index='cost_per_complaint',
    columns='delta_churn',
    values='total_annual_impact',
    aggfunc='mean'
)

    return pivot.round(0)


if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
    data_path = os.path.join(BASE_DIR, "data", "engineered", "energy_engineered_daily_aggregated_data.csv")
    daily_df = pd.read_csv(data_path)
    sensitivity_analysis_pipeline(daily_df)
    print("Sensitivity analysis completed successfully!")