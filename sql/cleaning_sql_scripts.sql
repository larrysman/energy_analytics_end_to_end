# ==============  DATA CLEANING ===================== #

CREATE TABLE energy_usage_dedup AS
SELECT DISTINCT *
FROM energy_usage_raw;

CREATE TABLE energy_usage_step1 AS
SELECT
    customer_id,
    region,
    meter_id,
    timestamp_utc,
    CASE WHEN kwh < 0 THEN NULL ELSE kwh END AS kwh,
    tariff_plan,
    is_smart_meter,
    outage_minutes_last_24h,
    bill_amount_eur,
    complaint_flag
FROM energy_usage_dedup;

CREATE TABLE energy_usage_clean AS
SELECT
    customer_id,
    COALESCE(region, 'Unknown') AS region,
    meter_id,
    timestamp_utc,
    kwh,
    tariff_plan,
    is_smart_meter,
    outage_minutes_last_24h,
    bill_amount_eur,
    complaint_flag
FROM energy_usage_step1;
