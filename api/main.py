from fastapi import FastAPI

from api.predictor import models_loaded, predict_policy
from api.schemas import (
    HealthResponse,
    PolicyInput,
    PredictionResponse,
)


app = FastAPI(
    title="Kfz Insurance Risk API",
    description=(
        "API for claim-frequency, severity, Pure Premium "
        "and risk-segment predictions."
    ),
    version="1.0.0",
)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        models_loaded=models_loaded(),
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Prediction"],
)
def predict(
    policy: PolicyInput,
) -> PredictionResponse:
    prediction = predict_policy(
        policy.model_dump()
    )

    return PredictionResponse(
        **prediction
    )