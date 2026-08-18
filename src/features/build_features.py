"""Create analytical features for the insurance risk platform."""

import pandas as pd
import numpy as np


def add_observed_claim_frequency(
    policy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Add annualized observed claim frequency."""

    featured_df = policy_df.copy()

    featured_df["observed_claim_frequency"] = (
        featured_df["ClaimNb"]
        / featured_df["Exposure"]
    )

    return featured_df


def add_observed_severity(
    policy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Add observed average claim severity."""

    featured_df = policy_df.copy()

    valid_severity_mask = (
        (featured_df["ClaimNb"] > 0)
        & (featured_df["total_claim_amount"].notna())
    )

    featured_df["observed_severity"] = np.nan

    featured_df.loc[
        valid_severity_mask,
        "observed_severity",
    ] = (
        featured_df.loc[
            valid_severity_mask,
            "total_claim_amount",
        ]
        / featured_df.loc[
            valid_severity_mask,
            "ClaimNb",
        ]
    )

    return featured_df


def add_observed_pure_premium(
    policy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Add annualized observed pure premium."""

    featured_df = policy_df.copy()

    featured_df["observed_pure_premium"] = (
        featured_df["total_claim_amount"]
        / featured_df["Exposure"]
    )

    return featured_df

def add_driver_age_group(
    policy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Add interpretable driver age groups."""

    featured_df = policy_df.copy()

    featured_df["driver_age_group"] = pd.cut(
        featured_df["DrivAge"],
        bins=[
            17,
            24,
            34,
            44,
            54,
            64,
            74,
            float("inf"),
        ],
        labels=[
            "18-24",
            "25-34",
            "35-44",
            "45-54",
            "55-64",
            "65-74",
            "75+",
        ],
        include_lowest=True,
    )

    return featured_df


def add_vehicle_age_group(
    policy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Add interpretable vehicle age groups."""

    featured_df = policy_df.copy()

    featured_df["vehicle_age_group"] = pd.cut(
        featured_df["VehAge"],
        bins=[
            -1,
            2,
            5,
            10,
            15,
            20,
            float("inf"),
        ],
        labels=[
            "0-2",
            "3-5",
            "6-10",
            "11-15",
            "16-20",
            "21+",
        ],
    )

    return featured_df


def add_bonus_malus_segment(
    policy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Add interpretable BonusMalus segments."""

    featured_df = policy_df.copy()

    featured_df["bonus_malus_segment"] = pd.cut(
        featured_df["BonusMalus"],
        bins=[
            49,
            50,
            64,
            79,
            99,
            float("inf"),
        ],
        labels=[
            "50",
            "51-64",
            "65-79",
            "80-99",
            "100+",
        ],
    )

    return featured_df


def add_log_density(
    policy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Add log-transformed population density."""

    featured_df = policy_df.copy()

    featured_df["log_density"] = np.log1p(
        featured_df["Density"]
    )

    return featured_df


def build_policy_features(
    policy_df: pd.DataFrame,
) -> pd.DataFrame:
    """Build all analytical policy-level features."""

    featured_df = add_observed_claim_frequency(policy_df)
    featured_df = add_observed_severity(featured_df)
    featured_df = add_observed_pure_premium(featured_df)
    featured_df = add_driver_age_group(featured_df)
    featured_df = add_vehicle_age_group(featured_df)
    featured_df = add_bonus_malus_segment(featured_df)
    featured_df = add_log_density(featured_df)

    return featured_df


