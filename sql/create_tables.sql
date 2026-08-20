CREATE TABLE IF NOT EXISTS stg_policy (
    idpol BIGINT,
    claim_nb SMALLINT,
    exposure DOUBLE PRECISION,
    area VARCHAR(1),
    veh_power SMALLINT,
    veh_age SMALLINT,
    driv_age SMALLINT,
    bonus_malus SMALLINT,
    veh_brand VARCHAR(3),
    veh_gas VARCHAR(7),
    density INTEGER,
    region VARCHAR(3)
);


CREATE TABLE IF NOT EXISTS stg_claim (
    idpol BIGINT,
    claim_amount NUMERIC(12,2)
);


CREATE TABLE IF NOT EXISTS fact_policy_exposure (
    idpol BIGINT PRIMARY KEY,
    claim_nb SMALLINT,
    exposure DOUBLE PRECISION,
    area VARCHAR(1),
    veh_power SMALLINT,
    veh_age SMALLINT,
    driv_age SMALLINT,
    bonus_malus SMALLINT,
    veh_brand VARCHAR(3),
    veh_gas VARCHAR(7),
    density INTEGER,
    region VARCHAR(3),

    exposure_capped BOOLEAN,
    high_claim_count BOOLEAN,

    total_claim_amount NUMERIC(12,2),
    claim_record_count SMALLINT,
    claim_count_mismatch BOOLEAN,
    missing_severity BOOLEAN,

    observed_claim_frequency DOUBLE PRECISION,
    observed_severity DOUBLE PRECISION,
    observed_pure_premium DOUBLE PRECISION,

    driver_age_group VARCHAR(5),
    vehicle_age_group VARCHAR(5),
    bonus_malus_segment VARCHAR(5),
    log_density DOUBLE PRECISION
);


CREATE TABLE IF NOT EXISTS fact_claim (
    claim_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    idpol BIGINT NOT NULL,
    claim_amount NUMERIC(12,2) NOT NULL
);


CREATE TABLE IF NOT EXISTS pipeline_runs (
    pipeline_run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_utc TIMESTAMPTZ NOT NULL,
    pipeline_status VARCHAR(20) NOT NULL,
    data_source VARCHAR(50) NOT NULL,
    frequency_row_count INTEGER,
    severity_row_count INTEGER,
    validations JSONB NOT NULL
);


CREATE TABLE IF NOT EXISTS dq_check_results (
    dq_result_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    run_id UUID,
    executed_at TIMESTAMPTZ NOT NULL,

    check_name VARCHAR(100) NOT NULL,
    dataset_name VARCHAR(50) NOT NULL,
    table_name VARCHAR(50),

    status VARCHAR(10) NOT NULL,
    severity VARCHAR(10),

    failed_rows INTEGER NOT NULL,
    warning_rows INTEGER NOT NULL,
    total_rows INTEGER NOT NULL,

    failure_rate DOUBLE PRECISION NOT NULL,
    warning_rate DOUBLE PRECISION NOT NULL,

    affected_rows INTEGER,
    affected_pct DOUBLE PRECISION,

    description TEXT,
    details JSONB NOT NULL
);


CREATE TABLE IF NOT EXISTS policy_frequency_predictions (
    idpol BIGINT NOT NULL,
    claim_nb INTEGER NOT NULL,
    exposure DOUBLE PRECISION NOT NULL,
    predicted_claim_frequency DOUBLE PRECISION NOT NULL,
    predicted_claim_count DOUBLE PRECISION NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    scored_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (idpol, model_name)
);