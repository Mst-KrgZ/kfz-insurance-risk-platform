"""Build curated datasets for the insurance risk platform."""

from pathlib import Path

import pandas as pd

from src.features.build_features import build_policy_features


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

FREQUENCY_FILE = RAW_DATA_DIR / "freMTPL2freq.pq"
SEVERITY_FILE = RAW_DATA_DIR / "freMTPL2sev.pq"

CURATED_POLICY_FILE = PROCESSED_DATA_DIR / "policy_curated.pq"


def aggregate_severity(
    severity_df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate severity records to one row per policy."""

    aggregated_df = (
        severity_df
        .groupby(
            "IDpol",
            as_index=False,
        )
        .agg(
            total_claim_amount=(
                "ClaimAmount",
                "sum",
            ),
            claim_record_count=(
                "ClaimAmount",
                "size",
            ),
        )
    )

    return aggregated_df


def split_orphan_severity(
    aggregated_severity_df: pd.DataFrame,
    frequency_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split matched and orphan severity policies."""

    orphan_mask = ~aggregated_severity_df["IDpol"].isin(
        frequency_df["IDpol"]
    )

    matched_df = aggregated_severity_df.loc[
        ~orphan_mask
    ].copy()

    orphan_df = aggregated_severity_df.loc[
        orphan_mask
    ].copy()

    return matched_df, orphan_df


def clean_exposure(
    frequency_df: pd.DataFrame,
) -> pd.DataFrame:
    """Cap exposure values above 1.0 and add a flag."""

    cleaned_df = frequency_df.copy()

    cleaned_df["exposure_capped"] = (
        cleaned_df["Exposure"] > 1
    )

    cleaned_df.loc[
        cleaned_df["Exposure"] > 1,
        "Exposure",
    ] = 1.0

    return cleaned_df


def add_high_claim_count_flag(
    frequency_df: pd.DataFrame,
    threshold: int = 4,
) -> pd.DataFrame:
    """Flag unusually high claim counts without removing them."""

    flagged_df = frequency_df.copy()

    flagged_df["high_claim_count"] = (
        flagged_df["ClaimNb"] > threshold
    )

    return flagged_df


def merge_frequency_with_severity(
    frequency_df: pd.DataFrame,
    aggregated_severity_df: pd.DataFrame,
) -> pd.DataFrame:
    """Merge policy data with aggregated severity data."""

    merged_df = frequency_df.merge(
        aggregated_severity_df,
        on="IDpol",
        how="left",
        validate="one_to_one",
    )

    return merged_df


def fill_claim_free_severity(
    merged_df: pd.DataFrame,
) -> pd.DataFrame:
    """Fill severity values with zero only for claim-free policies."""

    filled_df = merged_df.copy()

    claim_free_mask = (
        (filled_df["ClaimNb"] == 0)
        & (filled_df["total_claim_amount"].isna())
    )

    filled_df.loc[
        claim_free_mask,
        "total_claim_amount",
    ] = 0.0

    filled_df.loc[
        claim_free_mask,
        "claim_record_count",
    ] = 0

    return filled_df


def add_missing_severity_flag(
    merged_df: pd.DataFrame,
) -> pd.DataFrame:
    """Flag policies with claims but missing severity information."""

    flagged_df = merged_df.copy()

    flagged_df["missing_severity"] = (
        (flagged_df["ClaimNb"] > 0)
        & (flagged_df["total_claim_amount"].isna())
    )

    return flagged_df


def build_curated_policy(
    frequency_df: pd.DataFrame,
    matched_severity_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build the curated policy-level dataset."""

    curated_df = clean_exposure(frequency_df)
    curated_df = add_high_claim_count_flag(curated_df)

    curated_df = merge_frequency_with_severity(
        curated_df,
        matched_severity_df,
    )

    curated_df = fill_claim_free_severity(curated_df)
    curated_df = add_claim_count_mismatch_flag(curated_df)
    curated_df = add_missing_severity_flag(curated_df)

    return curated_df


def add_claim_count_mismatch_flag(
    policy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Flag policies whose claim count differs from severity records."""

    curated_df = policy_df.copy()

    curated_df["claim_count_mismatch"] = (
        curated_df["claim_record_count"].notna()
        & (
            curated_df["ClaimNb"]
            != curated_df["claim_record_count"]
        )
    )

    return curated_df


def save_curated_policy(
    curated_df: pd.DataFrame,
) -> None:
    """Save the curated policy dataset as Parquet."""

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    curated_df.to_parquet(
        CURATED_POLICY_FILE,
        index=False,
    )


def run_curated_pipeline() -> pd.DataFrame:
    """Run the complete raw-to-curated policy pipeline."""

    frequency_df = pd.read_parquet(FREQUENCY_FILE)
    severity_df = pd.read_parquet(SEVERITY_FILE)

    aggregated_severity_df = aggregate_severity(
        severity_df
    )

    matched_severity_df, orphan_severity_df = (
        split_orphan_severity(
            aggregated_severity_df,
            frequency_df,
        )
    )

    curated_df = build_curated_policy(
        frequency_df,
        matched_severity_df,
    )

    curated_df = build_policy_features(
        curated_df
    )

    save_curated_policy(curated_df)

    print(
        f"Curated dataset saved: "
        f"{CURATED_POLICY_FILE}"
    )
    print(
        f"Policies: {len(curated_df):,}"
    )
    print(
        f"Columns: {curated_df.shape[1]}"
    )
    print(
        f"Orphan severity policies excluded: "
        f"{len(orphan_severity_df):,}"
    )

    return curated_df


if __name__ == "__main__":
    run_curated_pipeline()