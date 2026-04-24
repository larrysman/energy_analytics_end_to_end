## `Outages, Tariffs and Customer Trust - An End-to-End Energy Analytics Case Study`

 **We have seen a rise in billing complaints and customer dissatisfaction in some regions and in this project, a raw data export from the data warehouse representing real-time business transaction dataset. No further instructions are provided and you are required to tell us what matters and what we should do, create a scenario that impact energy decision-making.**

 ### 📌 `Project Overview`

 This project simulates a real‑world energy analytics case study similar to what top `energy, utilities, and data‑driven` companies use in this evolving data-driven energy business.

The simulated energy dataset are messy raw export from an energy provider’s data warehouse with no instructions, no guidance, and the goal is to produce energy-driven business insights.

The goal of this project is to demonstrate:

- Business thinking

- Analytical judgement

- Communication clarity

- Technical execution (Python + SQL)

And the project walks through the following:

- Synthetic dataset creation

- Exploratory inspection ("Read before you Touch")

- Data cleaning using Python and SQL

- Feature engineering

- Insight generation

- Financial impact estimation

- Sensitivity analysis

- Business recommendations


### 🧠 `Business Problem`
A retail energy supplier has seen a rise in billing complaints and customer dissatisfaction, especially in certain regions. They want to understand:

- What drives complaints?

- Are outages related?

- Do tariff types influence customer behaviour?

- What is the financial impact?

- What actions should the business take?


##### **Business-Oriented Schema Design**

This schema guides the creation of the project data warehouse:

- Table: energy_usage_raw

- customer_id: customer identifier

- region: geographic region ('North', 'South', 'East', 'West')

- meter_id: meter identifier

- timestamp_utc: reading timestamp

- kwh: energy consumed in that interval

- tariff_plan: 'fixed' or 'variable'

- is_smart_meter: 0/1

- outage_minutes_last_24h: minutes of outage in last 24 hours

- bill_amount_eur: billed amount for that billing period (synthetic)

- complaint_flag: 0/1 whether customer raised a billing complaint

*Injected messiness to the energy dataset and they include:*

- Missing region

- Negative or zero kwh

- Duplicate rows

- Outliers in kwh and bill_amount_eur

