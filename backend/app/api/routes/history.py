from datetime import date, datetime, timedelta
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.models.prediction import Prediction, get_db
from backend.app.schemas.prediction import HistoryResponse, Probabilities

S3_BUCKET = "fod-wpt-mlops-artifacts"

router = APIRouter(prefix="", tags=["history"])


@router.get("/predictions", response_model=list[HistoryResponse])
def get_predictions(db: Session = Depends(get_db)) -> list[HistoryResponse]:
    rows = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(50).all()
    return [
        HistoryResponse(
            id=r.id,
            created_at=r.created_at.isoformat() + "Z" if r.created_at else "",
            prediction=r.prediction,
            label=r.label,
            confidence=r.confidence,
            probabilities=Probabilities(
                no_object=r.no_object_prob,
                fod_detected=r.fod_detected_prob,
            ),
            latency_ms=r.latency_ms,
            model_version=r.model_version,
            top_features=[],
        )
        for r in rows
    ]


@router.get("/drift/latest")
def get_drift_latest(db: Session = Depends(get_db)) -> dict:
    today = date.today()
    today_str = today.isoformat()

    # Count today's predictions (UTC midnight to midnight)
    day_start = datetime(today.year, today.month, today.day)
    day_end = day_start + timedelta(days=1)

    predictions_count: int = (
        db.query(Prediction)
        .filter(Prediction.created_at >= day_start, Prediction.created_at < day_end)
        .count()
    )

    # Check if today's report exists in S3
    s3_key = f"drift-reports/{today_str}.html"
    report_available = False
    report_url: Optional[str] = None

    try:
        s3 = boto3.client("s3")
        s3.head_object(Bucket=S3_BUCKET, Key=s3_key)
        report_available = True
        # Generate presigned URL valid for 1 hour
        report_url = s3.generate_presigned_url(
            "get_object", Params={"Bucket": S3_BUCKET, "Key": s3_key}, ExpiresIn=3600
        )
    except ClientError:
        pass

    return {
        "date": today_str,
        "report_available": report_available,
        "drift_detected": None,
        "report_url": report_url,
        "predictions_count": predictions_count,
    }
