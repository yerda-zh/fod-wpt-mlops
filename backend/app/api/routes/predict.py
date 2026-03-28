from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile

from backend.app.core import model_loader
from backend.app.schemas.prediction import HealthResponse, PredictionResponse
from backend.app.services.prediction_service import MODEL_VERSION, run_prediction

router = APIRouter(prefix="", tags=["prediction"])


@router.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile) -> PredictionResponse:
    file_bytes = await file.read()
    result = run_prediction(file_bytes)
    return PredictionResponse(**result)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    model_loader._load_artifacts()
    return HealthResponse(
        status="ok",
        model_version=MODEL_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
