from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


RiskSegment = Literal[
    "LOW",
    "STANDARD",
    "ELEVATED",
    "HIGH",
]

Priority = Literal[
    "Standard",
    "Moderate",
    "High",
    "Very High",
]


class PolicyInput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
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
        },
    )

    Exposure: float = Field(
        gt=0,
        allow_inf_nan=False,
        description="Policy exposure.",
    )

    VehPower: int = Field(
        ge=0,
        description="Vehicle power category.",
    )

    VehAge: float = Field(
        ge=0,
        allow_inf_nan=False,
        description="Vehicle age.",
    )

    DrivAge: float = Field(
        ge=0,
        allow_inf_nan=False,
        description="Driver age.",
    )

    BonusMalus: float = Field(
        ge=0,
        allow_inf_nan=False,
        description="Bonus-Malus value.",
    )

    VehBrand: str = Field(
        min_length=1,
        description="Vehicle brand category.",
    )

    VehGas: str = Field(
        min_length=1,
        description="Fuel category.",
    )

    Region: str = Field(
        min_length=1,
        description="Region category.",
    )

    log_density: float = Field(
        allow_inf_nan=False,
        description="Log-transformed population density.",
    )


class RiskScoreResponse(BaseModel):
    predicted_pure_premium_tweedie: float
    expected_loss_tweedie: float

    risk_segment: RiskSegment

    risk_decile: int = Field(
        ge=1,
        le=10,
    )

    priority: Priority

    recommended_action: str
    decision_rule: str


class PurePremiumResponse(BaseModel):
    predicted_claim_frequency: float
    expected_claim_count: float

    predicted_severity: float

    predicted_pure_premium_two_stage: float
    expected_loss_two_stage: float

    predicted_pure_premium_tweedie: float
    expected_loss_tweedie: float


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool


class DataQualitySummaryResponse(BaseModel):
    status: str
    summary: dict[str, Any]