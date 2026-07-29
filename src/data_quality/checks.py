"""Systematic data-quality checks for the freMTPL2 datasets."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DATA_DIR = PROJECT_ROOT / "data" / "output"
DQ_RESULTS_FILE = OUTPUT_DATA_DIR / "dq_check_results.jsonl"

FREQUENCY_FILE = RAW_DATA_DIR / "freMTPL2freq.pq"
SEVERITY_FILE = RAW_DATA_DIR / "freMTPL2sev.pq"


def build_check_result(
    check_name: str,
    dataset_name: str,
    passed: bool,
    failed_rows: int,
    total_rows: int,
    warning_rows: int = 0,
    warning_total_rows: int | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standardized result for a data-quality check."""

    failure_rate = (
        failed_rows / total_rows
        if total_rows > 0
        else 0.0
    )

    warning_denominator = (
        warning_total_rows
        if warning_total_rows is not None
        else total_rows
    )

    warning_rate = (
        warning_rows / warning_denominator
        if warning_denominator > 0
        else 0.0
    )

    if not passed or failed_rows > 0:
        status = "FAIL"
    elif warning_rows > 0:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "check_name": check_name,
        "dataset_name": dataset_name,
        "status": status,
        "failed_rows": failed_rows,
        "warning_rows": warning_rows,
        "total_rows": total_rows,
        "failure_rate": round(failure_rate, 6),
        "warning_rate": round(warning_rate, 6),
        "details": details or {},
    }

def save_check_results(
    results: list[dict[str, Any]],
) -> None:
    """Append data-quality check results to a JSONL file."""

    OUTPUT_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_id = str(uuid4())
    
    executed_at_utc = datetime.now(
        timezone.utc,
    ).isoformat()

    with DQ_RESULTS_FILE.open(
        "a",
        encoding="utf-8",
    ) as output_file:
        for result in results:
            if result["status"] == "FAIL":
                affected_rows = result["failed_rows"]
                affected_pct = result["failure_rate"]
            elif result["status"] == "WARN":
                affected_rows = result["warning_rows"]
                affected_pct = result["warning_rate"]
            else:
                affected_rows = 0
                affected_pct = 0.0
                
            severity = {
                "PASS": "INFO",
                "WARN": "WARNING",
                "FAIL": "ERROR",
            }[result["status"]]
            
            description = (
                f"Data-quality check '{result['check_name']}' "
                f"on '{result['dataset_name']}' completed with "
                f"status {result['status']}."
            )
                
            stored_result = {
                "run_id": run_id,
                "executed_at_utc": executed_at_utc,
                "table_name": result["dataset_name"],
                "affected_rows": affected_rows,
                "affected_pct": affected_pct,
                "severity": severity,
                "executed_at": executed_at_utc,
                "description": description,
                **result,
            }

            output_file.write(
                json.dumps(
                    stored_result,
                    ensure_ascii=False,
                )
                + "\n"
            )

def load_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the frequency and severity datasets from the raw-data directory."""

    if not FREQUENCY_FILE.exists():
        raise FileNotFoundError(
            f"Frequency dataset was not found: {FREQUENCY_FILE}"
        )

    if not SEVERITY_FILE.exists():
        raise FileNotFoundError(
            f"Severity dataset was not found: {SEVERITY_FILE}"
        )

    frequency_df = pd.read_parquet(FREQUENCY_FILE)
    severity_df = pd.read_parquet(SEVERITY_FILE)

    return frequency_df, severity_df


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: set[str],
    dataset_name: str,
) -> None:
    """Raise an error when required dataset columns are missing."""

    missing_columns = sorted(
        required_columns - set(df.columns)
    )

    if missing_columns:
        raise KeyError(
            f"Dataset '{dataset_name}' is missing required columns: "
            f"{missing_columns}"
        )
        
        
def check_missing_values(
    df: pd.DataFrame,
    dataset_name: str,
) -> dict[str, Any]:
    """Check whether the dataset contains missing values."""

    missing_by_column = df.isna().sum()

    missing_columns = {
        column: int(missing_count)
        for column, missing_count in missing_by_column.items()
        if missing_count > 0
    }

    failed_rows = int(df.isna().any(axis=1).sum())

    return build_check_result(
        check_name="missing_values",
        dataset_name=dataset_name,
        passed=failed_rows == 0,
        failed_rows=failed_rows,
        total_rows=len(df),
        details={"missing_by_column": missing_columns},
    )


def check_exposure_bounds(
    df: pd.DataFrame,
    dataset_name: str,
) -> dict[str, Any]:
    """Check whether exposure values are greater than 0 and at most 1."""

    validate_required_columns(
        df,
        {"Exposure"},
        dataset_name,
    )

    invalid_mask = (
        df["Exposure"].isna()
        | (df["Exposure"] <= 0)
        | (df["Exposure"] > 1)
    )

    failed_rows = int(invalid_mask.sum())

    details = {
        "minimum_exposure": float(df["Exposure"].min()),
        "maximum_exposure": float(df["Exposure"].max()),
        "non_positive_rows": int((df["Exposure"] <= 0).sum()),
        "above_one_rows": int((df["Exposure"] > 1).sum()),
    }

    return build_check_result(
        check_name="exposure_bounds",
        dataset_name=dataset_name,
        passed=failed_rows == 0,
        failed_rows=failed_rows,
        total_rows=len(df),
        details=details,
    )


def check_claim_number_bounds(
    df: pd.DataFrame,
    dataset_name: str = "frequency",
    high_claim_threshold: int = 4,
) -> dict[str, Any]:
    """Check claim numbers for negative, non-integer, and high values."""

    validate_required_columns(
        df,
        {"ClaimNb"},
        dataset_name,
    )

    claim_numbers = df["ClaimNb"]

    negative_mask = claim_numbers < 0
    non_integer_mask = claim_numbers.mod(1).ne(0)
    above_threshold_mask = claim_numbers > high_claim_threshold

    failed_mask = (
        negative_mask
        | non_integer_mask
    )

    warning_mask = (
        above_threshold_mask
        & ~failed_mask
    )

    failed_rows = int(failed_mask.sum())
    warning_rows = int(warning_mask.sum())

    return build_check_result(
        check_name="claim_number_bounds",
        dataset_name=dataset_name,
        passed=failed_rows == 0,
        failed_rows=failed_rows,
        warning_rows=warning_rows,
        total_rows=len(df),
        details={
            "minimum_claim_number": float(claim_numbers.min()),
            "maximum_claim_number": float(claim_numbers.max()),
            "negative_rows": int(negative_mask.sum()),
            "non_integer_rows": int(non_integer_mask.sum()),
            "high_claim_threshold": high_claim_threshold,
            "above_threshold_rows": int(above_threshold_mask.sum()),
        },
    )
  
    
def check_claim_amount_bounds(
    df: pd.DataFrame,
    dataset_name: str = "severity",
) -> dict[str, Any]:
    """Check claim amounts for zero or negative values."""
    
    validate_required_columns(
        df,
        {"IDpol", "ClaimAmount"},
        dataset_name,
    )

    policy_claim_totals = (
        df.groupby(
            "IDpol",
            as_index=False,
        )
        .agg(
            total_claim_amount=(
                "ClaimAmount",
                "sum",
            )
        )
    )    

    claim_amounts = df["ClaimAmount"]

    non_positive_mask = claim_amounts <= 0
    non_positive_total_mask = (
        policy_claim_totals["total_claim_amount"] <= 0
    )
    failed_rows = int(non_positive_mask.sum())

    return build_check_result(
        check_name="claim_amount_bounds",
        dataset_name=dataset_name,
        passed=failed_rows == 0,
        failed_rows=failed_rows,
        total_rows=len(df),
        details={
            "minimum_claim_amount": round(
                float(claim_amounts.min()),
                2,
            ),
            "maximum_claim_amount": round(
                float(claim_amounts.max()),
                2,
            ),
            "non_positive_rows": failed_rows,
            "p99_claim_amount": round(
                float(claim_amounts.quantile(0.99)),
                2,
            ),
            "p999_claim_amount": round(
                float(claim_amounts.quantile(0.999)),
                2,
            ),
            "minimum_total_claim_amount": round(
                float(
                    policy_claim_totals[
                        "total_claim_amount"
                    ].min()
                ),
                2,
            ),
            "non_positive_total_claim_policies": int(
                non_positive_total_mask.sum()
            ),
        },
    )


def check_frequency_severity_consistency(
    frequency_df: pd.DataFrame,
    severity_df: pd.DataFrame,
    dataset_name: str = "frequency_severity",
) -> dict[str, Any]:
    """Compare policy claim counts with available severity records."""

    validate_required_columns(
        frequency_df,
        {"IDpol", "ClaimNb"},
        "frequency",
    )

    validate_required_columns(
        severity_df,
        {"IDpol"},
        "severity",
    )

    severity_claim_counts = (
        severity_df
        .groupby("IDpol")
        .size()
        .rename("severity_claim_count")
        .reset_index()
    )

    claim_consistency = frequency_df[
        ["IDpol", "ClaimNb"]
    ].merge(
        severity_claim_counts,
        on="IDpol",
        how="left",
    )

    claim_consistency["severity_claim_count"] = (
        claim_consistency["severity_claim_count"]
        .fillna(0)
        .astype(int)
    )

    missing_severity_mask = (
        (claim_consistency["ClaimNb"] > 0)
        & (claim_consistency["severity_claim_count"] == 0)
    )

    unexpected_severity_mask = (
        (claim_consistency["ClaimNb"] == 0)
        & (claim_consistency["severity_claim_count"] > 0)
    )

    different_positive_counts_mask = (
        (claim_consistency["ClaimNb"] > 0)
        & (claim_consistency["severity_claim_count"] > 0)
        & (
            claim_consistency["ClaimNb"]
            != claim_consistency["severity_claim_count"]
        )
    )

    failed_mask = (
        missing_severity_mask
        | unexpected_severity_mask
        | different_positive_counts_mask
    )

    failed_rows = int(failed_mask.sum())
    
    claim_policy_mask = (
        claim_consistency["ClaimNb"] > 0
    )

    claim_free_policy_mask = (
        claim_consistency["ClaimNb"] == 0
    )

    claim_policies = int(
        claim_policy_mask.sum()
    )

    claim_free_policies = int(
        claim_free_policy_mask.sum()
    )

    claim_policies_with_any_severity = int(
        (
            claim_policy_mask
            & (
                claim_consistency["severity_claim_count"] > 0
            )
        ).sum()
    )

    fully_consistent_claim_policies = int(
        (
            claim_policy_mask
            & (
                claim_consistency["ClaimNb"]
                == claim_consistency["severity_claim_count"]
            )
        ).sum()
    )

    claim_policies_without_severity = int(
        missing_severity_mask.sum()
    )

    missing_severity_rate_among_claim_policies = (
        claim_policies_without_severity / claim_policies
        if claim_policies > 0
        else 0.0
    )

    claim_free_policy_rate = (
        claim_free_policies / len(frequency_df)
        if len(frequency_df) > 0
        else 0.0
    )

    return build_check_result(
        check_name="frequency_severity_consistency",
        dataset_name=dataset_name,
        passed=failed_rows == 0,
        failed_rows=failed_rows,
        total_rows=len(frequency_df),
        details={
            "claims_without_severity_rows": int(
                missing_severity_mask.sum()
            ),
            "severity_rows_without_claims": int(
                unexpected_severity_mask.sum()
            ),
            "different_positive_claim_counts": int(
                different_positive_counts_mask.sum()
            ),
            "claim_policies": claim_policies,
            "claim_free_policies": claim_free_policies,
            "claim_free_policy_rate": round(
                claim_free_policy_rate,
                6,
            ),
            "claim_policies_with_any_severity": (
                claim_policies_with_any_severity
            ),
            "fully_consistent_claim_policies": (
                fully_consistent_claim_policies
            ),
            "claim_policies_without_severity": (
                claim_policies_without_severity
            ),
            "missing_severity_rate_among_claim_policies": round(
                missing_severity_rate_among_claim_policies,
                6,
            ),
        },
    )


def check_orphan_severity_records(
    frequency_df: pd.DataFrame,
    severity_df: pd.DataFrame,
    dataset_name: str = "severity",
) -> dict[str, Any]:
    """Check for severity records without a matching frequency policy."""

    validate_required_columns(
        frequency_df,
        {"IDpol"},
        "frequency",
    )

    validate_required_columns(
        severity_df,
        {"IDpol", "ClaimAmount"},
        "severity",
    )

    orphan_mask = ~severity_df["IDpol"].isin(
        frequency_df["IDpol"]
    )

    orphan_rows = severity_df.loc[orphan_mask]
    failed_rows = int(orphan_mask.sum())

    return build_check_result(
        check_name="orphan_severity_records",
        dataset_name=dataset_name,
        passed=failed_rows == 0,
        failed_rows=failed_rows,
        total_rows=len(severity_df),
        details={
            "orphan_unique_policies": int(
                orphan_rows["IDpol"].nunique()
            ),
            "orphan_claim_amount_total": round(
                float(orphan_rows["ClaimAmount"].sum()),
                2,
            ),
        },
    )


def check_duplicate_records(
    frequency_df: pd.DataFrame,
    severity_df: pd.DataFrame,
    dataset_name: str = "frequency_severity",
) -> dict[str, Any]:
    """Check frequency duplicates and report potential severity duplicates."""
    
    validate_required_columns(
        frequency_df,
        {"IDpol"},
        "frequency",
    )

    validate_required_columns(
        severity_df,
        {"IDpol", "ClaimAmount"},
        "severity",
    )

    frequency_exact_duplicates = int(
        frequency_df.duplicated(keep="first").sum()
    )

    frequency_duplicate_id_mask = (
        frequency_df["IDpol"].duplicated(keep=False)
    )

    frequency_duplicate_id_rows = int(
        frequency_duplicate_id_mask.sum()
    )

    frequency_duplicate_unique_ids = int(
        frequency_df.loc[
            frequency_duplicate_id_mask,
            "IDpol",
        ].nunique()
    )

    severity_exact_duplicates = int(
        severity_df.duplicated(keep="first").sum()
    )

    severity_duplicate_groups = (
        severity_df
        .groupby(["IDpol", "ClaimAmount"])
        .size()
    )

    severity_duplicate_group_count = int(
        (severity_duplicate_groups > 1).sum()
    )

    warning_rows = severity_exact_duplicates
    failed_rows = frequency_duplicate_id_rows
    warning_rows = severity_exact_duplicates

    return build_check_result(
        check_name="duplicate_records",
        dataset_name=dataset_name,
        passed=failed_rows == 0,
        failed_rows=failed_rows,
        warning_rows=warning_rows,
        warning_total_rows=len(severity_df),
        total_rows=len(frequency_df),
        details={
            "frequency_exact_duplicate_rows": (
                frequency_exact_duplicates
            ),
            "frequency_duplicate_id_rows": (
                frequency_duplicate_id_rows
            ),
            "frequency_duplicate_unique_ids": (
                frequency_duplicate_unique_ids
            ),
            "severity_potential_duplicate_rows": (
                severity_exact_duplicates
            ),
            "severity_potential_duplicate_groups": (
                severity_duplicate_group_count
            ),
        },
    )


def check_join_cardinality(
    frequency_df: pd.DataFrame,
    severity_df: pd.DataFrame,
    dataset_name: str = "frequency_severity",
) -> dict[str, Any]:
    """Check whether the frequency-severity join follows one-to-many cardinality."""
    
    validate_required_columns(
        frequency_df,
        {"IDpol"},
        "frequency",
    )

    validate_required_columns(
        severity_df,
        {"IDpol", "ClaimAmount"},
        "severity",
    )    

    frequency_with_severity_mask = (
        frequency_df["IDpol"].isin(severity_df["IDpol"])
    )

    matched_severity_mask = (
        severity_df["IDpol"].isin(frequency_df["IDpol"])
    )

    frequency_with_severity_rows = int(
        frequency_with_severity_mask.sum()
    )

    frequency_without_severity_rows = int(
        (~frequency_with_severity_mask).sum()
    )

    matched_severity_rows = int(
        matched_severity_mask.sum()
    )

    expected_joined_rows = (
        frequency_without_severity_rows
        + matched_severity_rows
    )

    joined_df = frequency_df[["IDpol"]].merge(
        severity_df[["IDpol", "ClaimAmount"]],
        on="IDpol",
        how="left",
    )

    actual_joined_rows = len(joined_df)

    unexpected_extra_rows = (
        actual_joined_rows - expected_joined_rows
    )

    frequency_duplicate_id_rows = int(
        frequency_df["IDpol"]
        .duplicated(keep=False)
        .sum()
    )

    failed_rows = max(
        abs(unexpected_extra_rows),
        frequency_duplicate_id_rows,
    )

    return build_check_result(
        check_name="join_cardinality",
        dataset_name=dataset_name,
        passed=failed_rows == 0,
        failed_rows=failed_rows,
        total_rows=actual_joined_rows,
        details={
            "expected_relationship": "one_to_many",
            "frequency_rows_with_severity": (
                frequency_with_severity_rows
            ),
            "frequency_rows_without_severity": (
                frequency_without_severity_rows
            ),
            "matched_severity_rows": matched_severity_rows,
            "expected_joined_rows": expected_joined_rows,
            "actual_joined_rows": actual_joined_rows,
            "unexpected_extra_rows": unexpected_extra_rows,
            "frequency_duplicate_id_rows": (
                frequency_duplicate_id_rows
            ),
        },
    )
 
    
def run_all_checks(
    frequency_df: pd.DataFrame,
    severity_df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Run all data-quality checks and return their results."""

    return [
        check_missing_values(
            frequency_df,
            dataset_name="frequency",
        ),
        check_missing_values(
            severity_df,
            dataset_name="severity",
        ),
        check_exposure_bounds(
            frequency_df,
            dataset_name="frequency",
        ),
        check_claim_number_bounds(
            frequency_df,
            dataset_name="frequency",
        ),
        check_claim_amount_bounds(
            severity_df,
            dataset_name="severity",
        ),
        check_frequency_severity_consistency(
            frequency_df,
            severity_df,
            dataset_name="frequency_severity",
        ),
        check_orphan_severity_records(
            frequency_df,
            severity_df,
            dataset_name="severity",
        ),
        check_duplicate_records(
            frequency_df,
            severity_df,
            dataset_name="frequency_severity",
        ),
        check_join_cardinality(
            frequency_df,
            severity_df,
            dataset_name="frequency_severity",
        ),
    ]


if __name__ == "__main__":
    frequency_df, severity_df = load_datasets()

    results = run_all_checks(
        frequency_df,
        severity_df,
    )
    
    save_check_results(results)

    for result in results:
        print(result)
        