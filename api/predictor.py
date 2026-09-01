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


ACTION_CONFIG = {
    "Low": {
        "priority": "Standard",
        "recommended_action": "Standard portfolio monitoring",
        "decision_rule": "Decision support only",
    },
    "Medium": {
        "priority": "Moderate",
        "recommended_action": (
            "Regular segment monitoring and comparison"
        ),
        "decision_rule": "Decision support only",
    },
    "High": {
        "priority": "High",
        "recommended_action": (
            "Enhanced underwriting and pricing review"
        ),
        "decision_rule": "Manual review supported by model",
    },
    "Very High": {
        "priority": "Very High",
        "recommended_action": (
            "Priority underwriting review and intensive "
            "portfolio monitoring"
        ),
        "decision_rule": (
            "Priority manual review supported by model"
        ),
    },
}


frequency_model = joblib.load(FREQUENCY_MODEL_PATH)
severity_model = joblib.load(SEVERITY_MODEL_PATH)
tweedie_model = joblib.load(TWEEDIE_MODEL_PATH)


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
        return "Low"

    if tweedie_pure_premium <= RISK_Q75:
        return "Medium"

    if tweedie_pure_premium <= RISK_Q90:
        return "High"

    return "Very High"


def predict_policy(
    policy_data: dict,
) -> dict:
    exposure = float(policy_data["Exposure"])

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

    action = ACTION_CONFIG[risk_segment]

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
        "priority":
            action["priority"],
        "recommended_action":
            action["recommended_action"],
        "decision_rule":
            action["decision_rule"],
    }