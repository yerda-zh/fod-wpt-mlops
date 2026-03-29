from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.models.prediction import Prediction, get_db
from backend.app.schemas.prediction import HistoryResponse, Probabilities

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
