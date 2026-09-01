import json
import logging
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, HTTPException, status

from api.predictor import models_loaded, predict_policy
from api.schemas import (
    DataQualitySummaryResponse,
    HealthResponse,
    PolicyInput,
    PurePremiumResponse,
    RiskScoreResponse,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DQ_RESULTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "output"
    / "dq_check_results.jsonl"
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)

logger = logging.getLogger(
    "kfz-insurance-api"
)


app = FastAPI(
    title="Kfz Insurance Risk API",
    description=(
        "API for Pure Premium prediction, "
        "risk segmentation and data-quality monitoring."
    ),
    version="1.0.0",
)


def load_latest_dq_summary() -> dict:
    if not DQ_RESULTS_PATH.exists():
        logger.error(
            "Data-quality result file not found."
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data-quality results are unavailable.",
        )

    records = []

    with DQ_RESULTS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            if not line.strip():
                continue

            try:
                records.append(
                    json.loads(line)
                )
            except json.JSONDecodeError:
                logger.warning(
                    "Invalid JSON line skipped "
                    "in DQ result file."
                )

    if not records:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No data-quality results available.",
        )

    records_with_run_id = [
        record
        for record in records
        if record.get("run_id")
    ]

    if records_with_run_id:
        latest_record = max(
            records_with_run_id,
            key=lambda record: record.get(
                "executed_at_utc",
                "",
            ),
        )

        latest_run_id = latest_record[
            "run_id"
        ]

        latest_records = [
            record
            for record in records_with_run_id
            if record.get("run_id")
            == latest_run_id
        ]

    else:
        latest_run_id = None

        latest_timestamp = max(
            record.get(
                "executed_at_utc",
                "",
            )
            for record in records
        )

        latest_records = [
            record
            for record in records
            if record.get(
                "executed_at_utc",
                "",
            )
            == latest_timestamp
        ]

    status_counts = Counter(
        record.get(
            "status",
            "UNKNOWN",
        )
        for record in latest_records
    )

    if status_counts["FAIL"] > 0:
        overall_status = "FAIL"
    elif status_counts["WARN"] > 0:
        overall_status = "WARN"
    else:
        overall_status = "PASS"

    executed_at_utc = max(
        record.get(
            "executed_at_utc",
            "",
        )
        for record in latest_records
    )

    checks = [
        {
            "check_name":
                record.get("check_name"),
            "dataset_name":
                record.get("dataset_name"),
            "status":
                record.get("status"),
            "failed_rows":
                record.get("failed_rows", 0),
            "warning_rows":
                record.get("warning_rows", 0),
            "total_rows":
                record.get("total_rows", 0),
            "details":
                record.get("details", {}),
        }
        for record in latest_records
    ]

    return {
        "run_id": latest_run_id,
        "executed_at_utc": executed_at_utc,
        "overall_status": overall_status,
        "checks_total": len(latest_records),
        "pass_count": status_counts["PASS"],
        "warn_count": status_counts["WARN"],
        "fail_count": status_counts["FAIL"],
        "checks": checks,
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["System"],
)
def health_check() -> HealthResponse:
    loaded = models_loaded()

    logger.info(
        "Health check requested."
    )

    return HealthResponse(
        status=(
            "ok"
            if loaded
            else "degraded"
        ),
        models_loaded=loaded,
    )


@app.post(
    "/risk-score",
    response_model=RiskScoreResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prediction"],
)
def risk_score(
    policy: PolicyInput,
) -> RiskScoreResponse:
    try:
        prediction = predict_policy(
            policy.model_dump()
        )

        logger.info(
            "Risk score generated: "
            "segment=%s, decile=%s",
            prediction["risk_segment"],
            prediction["risk_decile"],
        )

        return RiskScoreResponse(
            predicted_pure_premium_tweedie=(
                prediction[
                    "predicted_pure_premium_tweedie"
                ]
            ),
            expected_loss_tweedie=(
                prediction[
                    "expected_loss_tweedie"
                ]
            ),
            risk_segment=(
                prediction["risk_segment"]
            ),
            risk_decile=(
                prediction["risk_decile"]
            ),
            priority=(
                prediction["priority"]
            ),
            recommended_action=(
                prediction[
                    "recommended_action"
                ]
            ),
            decision_rule=(
                prediction["decision_rule"]
            ),
        )

    except Exception as exc:
        logger.exception(
            "Risk-score prediction failed."
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Risk-score prediction failed.",
        ) from exc


@app.post(
    "/pure-premium",
    response_model=PurePremiumResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prediction"],
)
def pure_premium(
    policy: PolicyInput,
) -> PurePremiumResponse:
    try:
        prediction = predict_policy(
            policy.model_dump()
        )

        logger.info(
            "Pure Premium prediction generated."
        )

        return PurePremiumResponse(
            predicted_claim_frequency=(
                prediction[
                    "predicted_claim_frequency"
                ]
            ),
            expected_claim_count=(
                prediction[
                    "expected_claim_count"
                ]
            ),
            predicted_severity=(
                prediction[
                    "predicted_severity"
                ]
            ),
            predicted_pure_premium_two_stage=(
                prediction[
                    "predicted_pure_premium_two_stage"
                ]
            ),
            expected_loss_two_stage=(
                prediction[
                    "expected_loss_two_stage"
                ]
            ),
            predicted_pure_premium_tweedie=(
                prediction[
                    "predicted_pure_premium_tweedie"
                ]
            ),
            expected_loss_tweedie=(
                prediction[
                    "expected_loss_tweedie"
                ]
            ),
        )

    except Exception as exc:
        logger.exception(
            "Pure Premium prediction failed."
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Pure Premium prediction failed.",
        ) from exc


@app.get(
    "/data-quality-summary",
    response_model=DataQualitySummaryResponse,
    status_code=status.HTTP_200_OK,
    tags=["Monitoring"],
)
def data_quality_summary(
) -> DataQualitySummaryResponse:
    summary = load_latest_dq_summary()

    logger.info(
        "Data-quality summary requested: "
        "overall_status=%s",
        summary["overall_status"],
    )

    return DataQualitySummaryResponse(
        status="ok",
        summary=summary,
    )