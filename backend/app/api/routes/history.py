from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.models.prediction import Prediction, get_db
from backend.app.schemas.prediction import Probabilities, PredictionResponse

router = APIRouter(prefix="", tags=["history"])


@router.get("/predictions", response_model=list[PredictionResponse])
def get_predictions(db: Session = Depends(get_db)) -> list[PredictionResponse]:
    rows = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(50).all()
    return [
        PredictionResponse(
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
