CREATE OR REPLACE VIEW vw_policy_risk_base AS
SELECT
    idpol,
    claim_nb,
    exposure,

    area,
    veh_power,
    veh_age,
    driv_age,
    bonus_malus,
    veh_brand,
    veh_gas,
    density,
    region,

    driver_age_group,
    vehicle_age_group,
    bonus_malus_segment,
    log_density,

    total_claim_amount,
    claim_record_count,
    observed_claim_frequency,
    observed_severity,
    observed_pure_premium,

    exposure_capped,
    high_claim_count,
    claim_count_mismatch,
    missing_severity,

    CASE
        WHEN claim_nb > 0 THEN TRUE
        ELSE FALSE
    END AS has_claim

FROM fact_policy_exposure;

CREATE OR REPLACE VIEW vw_claim_analysis AS
SELECT
    fc.claim_id,
    fc.idpol,
    fc.claim_amount,

    p.exposure,
    p.area,
    p.veh_power,
    p.veh_age,
    p.driv_age,
    p.bonus_malus,
    p.veh_brand,
    p.veh_gas,
    p.density,
    p.region,

    p.driver_age_group,
    p.vehicle_age_group,
    p.bonus_malus_segment,
    p.log_density,

    p.claim_nb,
    p.high_claim_count,
    p.claim_count_mismatch

FROM fact_claim AS fc
INNER JOIN fact_policy_exposure AS p
    ON fc.idpol = p.idpol;


CREATE OR REPLACE VIEW vw_dq_summary AS
WITH ranked_checks AS (
    SELECT
        dq_result_id,
        run_id,
        executed_at,
        check_name,
        dataset_name,
        table_name,
        status,
        severity,
        failed_rows,
        warning_rows,
        total_rows,
        failure_rate,
        warning_rate,
        affected_rows,
        affected_pct,
        description,
        details,

        ROW_NUMBER() OVER (
            PARTITION BY check_name, dataset_name
            ORDER BY executed_at DESC
        ) AS row_num

    FROM dq_check_results
)

SELECT
    dq_result_id,
    run_id,
    executed_at,
    check_name,
    dataset_name,
    table_name,
    status,
    severity,
    failed_rows,
    warning_rows,
    total_rows,
    failure_rate,
    warning_rate,
    affected_rows,
    affected_pct,
    description,
    details

FROM ranked_checks
WHERE row_num = 1;

CREATE OR REPLACE VIEW vw_frequency_prediction_analysis AS
SELECT
    p.idpol,
    pr.model_name,
    pr.scored_at,

    p.claim_nb,
    p.exposure,

    p.area,
    p.veh_power,
    p.veh_age,
    p.driv_age,
    p.bonus_malus,
    p.veh_brand,
    p.veh_gas,
    p.density,
    p.region,

    p.driver_age_group,
    p.vehicle_age_group,
    p.bonus_malus_segment,

    p.observed_claim_frequency,

    pr.predicted_claim_frequency,
    pr.predicted_claim_count,

    p.claim_nb - pr.predicted_claim_count
        AS claim_count_residual

FROM vw_policy_risk_base AS p
INNER JOIN policy_frequency_predictions AS pr
    ON p.idpol = pr.idpol;


CREATE OR REPLACE VIEW vw_model_prediction_analysis AS
WITH latest_run AS (
    SELECT
        prediction_run_id
    FROM model_predictions
    GROUP BY prediction_run_id
    ORDER BY MAX(scored_at) DESC
    LIMIT 1
)

SELECT
    p.idpol,

    pr.prediction_run_id,
    pr.frequency_model_version,
    pr.severity_model_version,
    pr.scored_at,

    p.claim_nb,
    p.exposure,

    p.area,
    p.veh_power,
    p.veh_age,
    p.driv_age,
    p.bonus_malus,
    p.veh_brand,
    p.veh_gas,
    p.density,
    p.region,

    p.driver_age_group,
    p.vehicle_age_group,
    p.bonus_malus_segment,
    p.log_density,

    p.total_claim_amount,
    p.observed_claim_frequency,
    p.observed_severity,
    p.observed_pure_premium,

    p.exposure_capped,
    p.high_claim_count,
    p.claim_count_mismatch,
    p.missing_severity,

    pr.predicted_frequency,
    pr.predicted_severity,
    pr.predicted_pure_premium,

    pr.exposure_used,
    pr.expected_claim_count,
    pr.expected_claim_amount,

    p.claim_nb - pr.expected_claim_count
        AS claim_count_residual,

    CASE
        WHEN p.total_claim_amount IS NOT NULL
        THEN p.total_claim_amount - pr.expected_claim_amount
        ELSE NULL
    END AS claim_amount_residual,

    CASE
        WHEN p.total_claim_amount IS NOT NULL
        THEN TRUE
        ELSE FALSE
    END AS has_observed_claim_amount

FROM vw_policy_risk_base AS p

INNER JOIN model_predictions AS pr
    ON p.idpol = pr.idpol

INNER JOIN latest_run AS lr
    ON pr.prediction_run_id = lr.prediction_run_id;

    