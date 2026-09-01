from bisect import bisect_left
from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"


FREQUENCY_MODEL_PATH = (
    MODELS_DIR
    / "frequency_poisson_quantile_spline_full_v2.joblib"
)

SEVERITY_MODEL_PATH = (
    MODELS_DIR
    / "severity_gamma_spline_scaled_full_v2.joblib"
)

TWEEDIE_MODEL_PATH = (
    MODELS_DIR
    / "tweedie_direct_pure_premium_full_v1.joblib"
)


# Locked segmentation thresholds from the full-portfolio
# Tweedie Pure Premium distribution.
RISK_Q50 = 119.348996
RISK_Q75 = 187.904073
RISK_Q90 = 328.242187


# Locked decile thresholds from the full-portfolio
# Tweedie Pure Premium distribution.
RISK_DECILE_THRESHOLDS = (
    64.796231,
    79.664977,
    92.068111,
    104.717346,
    119.348996,
    138.353633,
    166.781609,
    217.215693,
    328.242187,
)


ACTION_CONFIG = {
    "LOW": {
        "priority": "Standard",
        "recommended_action": "Standard process",
        "decision_rule": "Decision support only",
    },
    "STANDARD": {
        "priority": "Moderate",
        "recommended_action": "Standard process",
        "decision_rule": "Decision support only",
    },
    "ELEVATED": {
        "priority": "High",
        "recommended_action": (
            "Additional review recommended"
        ),
        "decision_rule": (
            "Model-supported additional review"
        ),
    },
    "HIGH": {
        "priority": "Very High",
        "recommended_action": (
            "Manual underwriting review recommended"
        ),
        "decision_rule": (
            "Manual review supported by model"
        ),
    },
}


frequency_model = joblib.load(
    FREQUENCY_MODEL_PATH
)

severity_model = joblib.load(
    SEVERITY_MODEL_PATH
)

tweedie_model = joblib.load(
    TWEEDIE_MODEL_PATH
)


def models_loaded() -> bool:
    return all(
        model is not None
        for model in (
            frequency_model,
            severity_model,
            tweedie_model,
        )
    )


def assign_risk_segment(
    tweedie_pure_premium: float,
) -> str:
    if tweedie_pure_premium <= RISK_Q50:
        return "LOW"

    if tweedie_pure_premium <= RISK_Q75:
        return "STANDARD"

    if tweedie_pure_premium <= RISK_Q90:
        return "ELEVATED"

    return "HIGH"


def assign_risk_decile(
    tweedie_pure_premium: float,
) -> int:
    return (
        bisect_left(
            RISK_DECILE_THRESHOLDS,
            tweedie_pure_premium,
        )
        + 1
    )


def predict_policy(
    policy_data: dict,
) -> dict:
    exposure = float(
        policy_data["Exposure"]
    )

    feature_columns = [
        "VehPower",
        "VehBrand",
        "VehGas",
        "Region",
        "DrivAge",
        "VehAge",
        "BonusMalus",
        "log_density",
    ]

    features = pd.DataFrame(
        [
            {
                column: policy_data[column]
                for column in feature_columns
            }
        ]
    )

    predicted_frequency = float(
        frequency_model.predict(features)[0]
    )

    predicted_severity = float(
        severity_model.predict(features)[0]
    )

    predicted_pp_two_stage = (
        predicted_frequency
        * predicted_severity
    )

    predicted_pp_tweedie = float(
        tweedie_model.predict(features)[0]
    )

    expected_claim_count = (
        predicted_frequency
        * exposure
    )

    expected_loss_two_stage = (
        predicted_pp_two_stage
        * exposure
    )

    expected_loss_tweedie = (
        predicted_pp_tweedie
        * exposure
    )

    risk_segment = assign_risk_segment(
        predicted_pp_tweedie
    )

    risk_decile = assign_risk_decile(
        predicted_pp_tweedie
    )

    action = ACTION_CONFIG[
        risk_segment
    ]

    return {
        "predicted_claim_frequency":
            predicted_frequency,
        "expected_claim_count":
            expected_claim_count,
        "predicted_severity":
            predicted_severity,
        "predicted_pure_premium_two_stage":
            predicted_pp_two_stage,
        "expected_loss_two_stage":
            expected_loss_two_stage,
        "predicted_pure_premium_tweedie":
            predicted_pp_tweedie,
        "expected_loss_tweedie":
            expected_loss_tweedie,
        "risk_segment":
            risk_segment,
        "risk_decile":
            risk_decile,
        "priority":
            action["priority"],
        "recommended_action":
            action["recommended_action"],
        "decision_rule":
            action["decision_rule"],
    }