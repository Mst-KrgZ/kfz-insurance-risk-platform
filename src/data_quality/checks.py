"""Systematic data-quality checks for the freMTPL2 datasets."""

from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

FREQUENCY_FILE = RAW_DATA_DIR / "freMTPL2freq.pq"
SEVERITY_FILE = RAW_DATA_DIR / "freMTPL2sev.pq"


def build_check_result(
    check_name: str,
    dataset_name: str,
    passed: bool,
    failed_rows: int,
    total_rows: int,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standardized result for a data-quality check."""

    failure_rate = failed_rows / total_rows if total_rows > 0 else 0.0

    return {
        "check_name": check_name,
        "dataset_name": dataset_name,
        "status": "PASS" if passed else "FAIL",
        "failed_rows": failed_rows,
        "total_rows": total_rows,
        "failure_rate": round(failure_rate, 6),
        "details": details or {},
    }

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

    if "Exposure" not in df.columns:
        raise KeyError("Required column was not found: Exposure")

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
) -> dict:
    claim_numbers = df["ClaimNb"]

    negative_mask = claim_numbers < 0
    non_integer_mask = claim_numbers.mod(1).ne(0)
    above_threshold_mask = claim_numbers > high_claim_threshold

    failed_mask = (
        negative_mask
        | non_integer_mask
        | above_threshold_mask
    )

    return build_check_result(
        check_name="claim_number_bounds",
        dataset_name=dataset_name,
        passed=not failed_mask.any(),
        failed_rows=int(failed_mask.sum()),
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
) -> dict:
    claim_amounts = df["ClaimAmount"]

    non_positive_mask = claim_amounts <= 0
    failed_rows = int(non_positive_mask.sum())

    return build_check_result(
        check_name="claim_amount_bounds",
        dataset_name=dataset_name,
        passed=failed_rows == 0,
        failed_rows=failed_rows,
        total_rows=len(df),
        details={
            "minimum_claim_amount": float(claim_amounts.min()),
            "maximum_claim_amount": float(claim_amounts.max()),
            "non_positive_rows": failed_rows,
            "p99_claim_amount": float(
                claim_amounts.quantile(0.99)
            ),
            "p999_claim_amount": float(
                claim_amounts.quantile(0.999)
            ),
        },
    )

if __name__ == "__main__":
    frequency_df, severity_df = load_datasets()

    frequency_missing_result = check_missing_values(
        frequency_df,
        dataset_name="frequency",
    )

    severity_missing_result = check_missing_values(
        severity_df,
        dataset_name="severity",
    )

    exposure_result = check_exposure_bounds(
        frequency_df,
        dataset_name="frequency",
    )

    claim_number_result = check_claim_number_bounds(
        frequency_df,
        dataset_name="frequency",
    )
    
    claim_amount_result = check_claim_amount_bounds(
    severity_df,
    dataset_name="severity",
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

    mismatch_mask = (
        claim_consistency["ClaimNb"]
        != claim_consistency["severity_claim_count"]
    )

    print("\nFrequency-Severity Consistency:")
    print("Mismatched policies:", int(mismatch_mask.sum()))

    print("\nFirst 10 Mismatches:")
    print(
        claim_consistency
        .loc[mismatch_mask]
        .head(10)
        .to_string(index=False)
    )

    results = [
        frequency_missing_result,
        severity_missing_result,
        exposure_result,
        claim_number_result,
        claim_amount_result,
    ]

    for result in results:
        print(result)