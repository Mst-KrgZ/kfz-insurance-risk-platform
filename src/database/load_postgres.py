"""Load project datasets into PostgreSQL."""

from getpass import getpass
from io import StringIO
from pathlib import Path

import pandas as pd
import psycopg
import json


DB_NAME = "kfz_insurance"
DB_USER = "kfz_app"
DB_HOST = "localhost"
DB_PORT = 5432

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FREQUENCY_FILE = PROJECT_ROOT / "data" / "raw" / "freMTPL2freq.pq"
SEVERITY_FILE = PROJECT_ROOT / "data" / "raw" / "freMTPL2sev.pq"

CURATED_POLICY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "policy_curated.pq"
)

PIPELINE_RUNS_FILE = (
    PROJECT_ROOT
    / "data"
    / "output"
    / "pipeline_runs.jsonl"
)

DQ_CHECK_RESULTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "output"
    / "dq_check_results.jsonl"
)

def test_connection(
    connection: psycopg.Connection,
) -> None:
    """Test the PostgreSQL connection."""

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_database(), current_user;"
        )
        result = cursor.fetchone()

    if result is None:
        raise RuntimeError(
            "PostgreSQL connection test returned no result."
        )

    print("Database:", result[0])
    print("User:", result[1])


def load_stg_policy(
    connection: psycopg.Connection,
) -> int:
    """Load the raw frequency dataset into stg_policy."""

    frequency_df = pd.read_parquet(FREQUENCY_FILE).copy()

    # These columns are stored as float in the source file,
    # but were verified to contain only whole numbers.
    frequency_df["IDpol"] = frequency_df["IDpol"].astype("int64")
    frequency_df["Density"] = frequency_df["Density"].astype("int64")

    buffer = StringIO()

    frequency_df.to_csv(
        buffer,
        index=False,
        header=False,
    )

    buffer.seek(0)

    with connection.cursor() as cursor:
        cursor.execute(
            "TRUNCATE TABLE stg_policy;"
        )

        with cursor.copy(
            """
            COPY stg_policy (
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
                region
            )
            FROM STDIN
            WITH (FORMAT CSV)
            """
        ) as copy:
            copy.write(buffer.getvalue())

    return len(frequency_df)

def load_stg_claim(
    connection: psycopg.Connection,
) -> int:
    """Load the raw severity dataset into stg_claim."""

    severity_df = pd.read_parquet(SEVERITY_FILE).copy()

    severity_df["IDpol"] = severity_df["IDpol"].astype("int64")

    buffer = StringIO()

    severity_df.to_csv(
        buffer,
        index=False,
        header=False,
    )

    buffer.seek(0)

    with connection.cursor() as cursor:
        cursor.execute(
            "TRUNCATE TABLE stg_claim;"
        )

        with cursor.copy(
            """
            COPY stg_claim (
                idpol,
                claim_amount
            )
            FROM STDIN
            WITH (FORMAT CSV)
            """
        ) as copy:
            copy.write(buffer.getvalue())

    return len(severity_df)

def load_fact_policy_exposure(
    connection: psycopg.Connection,
) -> int:
    """Load the curated policy dataset into fact_policy_exposure."""

    policy_df = pd.read_parquet(
        CURATED_POLICY_FILE
    ).copy()

    policy_df["IDpol"] = policy_df["IDpol"].astype("int64")
    policy_df["Density"] = policy_df["Density"].astype("int64")

    policy_df["claim_record_count"] = (
        policy_df["claim_record_count"].astype("Int64")
    )

    buffer = StringIO()

    policy_df.to_csv(
        buffer,
        index=False,
        header=False,
        na_rep="\\N",
    )

    buffer.seek(0)

    with connection.cursor() as cursor:
        cursor.execute(
            "TRUNCATE TABLE fact_policy_exposure;"
        )

        with cursor.copy(
            """
            COPY fact_policy_exposure (
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
                exposure_capped,
                high_claim_count,
                total_claim_amount,
                claim_record_count,
                claim_count_mismatch,
                missing_severity,
                observed_claim_frequency,
                observed_severity,
                observed_pure_premium,
                driver_age_group,
                vehicle_age_group,
                bonus_malus_segment,
                log_density
            )
            FROM STDIN
            WITH (
                FORMAT CSV,
                NULL '\\N'
            )
            """
        ) as copy:
            copy.write(buffer.getvalue())

    return len(policy_df)

def load_fact_claim(
    connection: psycopg.Connection,
) -> int:
    """Load matched claim-level records into fact_claim."""

    frequency_df = pd.read_parquet(
        FREQUENCY_FILE,
        columns=["IDpol"],
    )

    severity_df = pd.read_parquet(
        SEVERITY_FILE
    ).copy()

    matched_claims_df = severity_df[
        severity_df["IDpol"].isin(
            frequency_df["IDpol"]
        )
    ].copy()

    matched_claims_df["IDpol"] = (
        matched_claims_df["IDpol"].astype("int64")
    )

    buffer = StringIO()

    matched_claims_df.to_csv(
        buffer,
        index=False,
        header=False,
    )

    buffer.seek(0)

    with connection.cursor() as cursor:
        cursor.execute(
            "TRUNCATE TABLE fact_claim RESTART IDENTITY;"
        )

        with cursor.copy(
            """
            COPY fact_claim (
                idpol,
                claim_amount
            )
            FROM STDIN
            WITH (FORMAT CSV)
            """
        ) as copy:
            copy.write(buffer.getvalue())

    return len(matched_claims_df)


def load_pipeline_runs(
    connection: psycopg.Connection,
) -> int:
    """Load ingestion pipeline run history into PostgreSQL."""

    with PIPELINE_RUNS_FILE.open(
        encoding="utf-8"
    ) as file:
        records = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    pipeline_df = pd.DataFrame(records)

    pipeline_df["validations"] = (
        pipeline_df["validations"]
        .apply(json.dumps)
    )

    buffer = StringIO()

    pipeline_df.to_csv(
        buffer,
        index=False,
        header=False,
    )

    buffer.seek(0)

    with connection.cursor() as cursor:
        cursor.execute(
            "TRUNCATE TABLE pipeline_runs RESTART IDENTITY;"
        )

        with cursor.copy(
            """
            COPY pipeline_runs (
                run_utc,
                pipeline_status,
                data_source,
                frequency_row_count,
                severity_row_count,
                validations
            )
            FROM STDIN
            WITH (FORMAT CSV)
            """
        ) as copy:
            copy.write(buffer.getvalue())

    return len(pipeline_df)

def load_dq_check_results(
    connection: psycopg.Connection,
) -> int:
    """Load data-quality check history into PostgreSQL."""

    with DQ_CHECK_RESULTS_FILE.open(
        encoding="utf-8"
    ) as file:
        records = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    normalized_records = []

    for record in records:
        normalized_records.append(
            {
                "run_id": record.get("run_id"),
                "executed_at": (
                    record.get("executed_at")
                    or record.get("executed_at_utc")
                ),
                "check_name": record["check_name"],
                "dataset_name": record["dataset_name"],
                "table_name": record.get("table_name"),
                "status": record["status"],
                "severity": record.get("severity"),
                "failed_rows": record["failed_rows"],
                "warning_rows": record["warning_rows"],
                "total_rows": record["total_rows"],
                "failure_rate": record["failure_rate"],
                "warning_rate": record["warning_rate"],
                "affected_rows": record.get("affected_rows"),
                "affected_pct": record.get("affected_pct"),
                "description": record.get("description"),
                "details": json.dumps(record["details"]),
            }
        )

    dq_df = pd.DataFrame(normalized_records)
    
    dq_df["affected_rows"] = (
    dq_df["affected_rows"].astype("Int64")
)

    buffer = StringIO()

    dq_df.to_csv(
        buffer,
        index=False,
        header=False,
        na_rep="\\N",
    )

    buffer.seek(0)

    with connection.cursor() as cursor:
        cursor.execute(
            "TRUNCATE TABLE dq_check_results RESTART IDENTITY;"
        )

        with cursor.copy(
            """
            COPY dq_check_results (
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
            )
            FROM STDIN
            WITH (
                FORMAT CSV,
                NULL '\\N'
            )
            """
        ) as copy:
            copy.write(buffer.getvalue())

    return len(dq_df)


if __name__ == "__main__":
    password = getpass("PostgreSQL password: ")

    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=password,
        host=DB_HOST,
        port=DB_PORT,
    ) as connection:
        test_connection(connection)

        loaded_policy_rows = load_stg_policy(connection)
        loaded_claim_rows = load_stg_claim(connection)
        loaded_fact_policy_rows = load_fact_policy_exposure(
            connection
        )
        loaded_fact_claim_rows = load_fact_claim(
            connection
        )
        loaded_pipeline_run_rows = load_pipeline_runs(
            connection
        )
        loaded_dq_check_rows = load_dq_check_results(
            connection
        )

        print(
            "Loaded stg_policy rows:",
            loaded_policy_rows,
        )
        print(
            "Loaded stg_claim rows:",
            loaded_claim_rows,
        )
        print(
            "Loaded fact_policy_exposure rows:",
            loaded_fact_policy_rows,
        )
        print(
            "Loaded fact_claim rows:",
            loaded_fact_claim_rows,
        )
        print(
            "Loaded pipeline_runs rows:",
            loaded_pipeline_run_rows,
        )
        print(
            "Loaded dq_check_results rows:",
            loaded_dq_check_rows,
        )