import pytest
from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


VALID_POLICY = {
    "Exposure": 0.8,
    "VehPower": 6,
    "VehAge": 5.0,
    "DrivAge": 40.0,
    "BonusMalus": 70.0,
    "VehBrand": "B1",
    "VehGas": "Diesel",
    "Region": "R93",
    "log_density": 6.2,
}


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "models_loaded": True,
    }


def test_predict_endpoint():
    response = client.post(
        "/predict",
        json=VALID_POLICY,
    )

    assert response.status_code == 200

    body = response.json()

    expected_fields = {
        "predicted_claim_frequency",
        "expected_claim_count",
        "predicted_severity",
        "predicted_pure_premium_two_stage",
        "expected_loss_two_stage",
        "predicted_pure_premium_tweedie",
        "expected_loss_tweedie",
        "risk_segment",
        "priority",
        "recommended_action",
        "decision_rule",
    }

    assert expected_fields.issubset(body.keys())

    assert body["predicted_claim_frequency"] == pytest.approx(
        0.1191826692,
        rel=1e-6,
    )

    assert body["predicted_pure_premium_tweedie"] == pytest.approx(
        370.5788741,
        rel=1e-6,
    )

    assert body["risk_segment"] == "Very High"
    assert body["priority"] == "Very High"


def test_predict_rejects_zero_exposure():
    invalid_policy = VALID_POLICY.copy()
    invalid_policy["Exposure"] = 0

    response = client.post(
        "/predict",
        json=invalid_policy,
    )

    assert response.status_code == 422


def test_predict_rejects_unknown_field():
    invalid_policy = VALID_POLICY.copy()
    invalid_policy["UnknownFeature"] = 123

    response = client.post(
        "/predict",
        json=invalid_policy,
    )

    assert response.status_code == 422