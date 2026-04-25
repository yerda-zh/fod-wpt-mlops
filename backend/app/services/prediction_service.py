import io
import logging
import time

import numpy as np
import pandas as pd
from fastapi import HTTPException
from datetime import datetime, timezone
from backend.app.core import model_loader
from backend.app.models.prediction import Prediction, SessionLocal

logger = logging.getLogger(__name__)

MODEL_VERSION = "v1"


def run_prediction(file_bytes: bytes) -> dict:
    t0 = time.perf_counter()
    try:
        df = pd.read_csv(
            io.BytesIO(file_bytes),
            skiprows=4,
            usecols=["Time", "Ampl"],
        )
    except Exception as exc:
        logger.error("CSV parse error: %s", exc)
        raise HTTPException(status_code=422, detail="Invalid CSV file.") from exc

    try:
        t = df["Time"].to_numpy(dtype=np.float64)
        x = df["Ampl"].to_numpy(dtype=np.float64)
        result = model_loader.predict(t, x)
        latency_ms = (time.perf_counter() - t0) * 1000
        result["latency_ms"] = latency_ms
        result["model_version"] = MODEL_VERSION

        db = SessionLocal()
        try:
            db.add(
                Prediction(
                    prediction=result["prediction"],
                    label=result["label"],
                    confidence=result["confidence"],
                    no_object_prob=result["probabilities"]["no_object"],
                    fod_detected_prob=result["probabilities"]["fod_detected"],
                    latency_ms=result["latency_ms"],
                    model_version=result["model_version"],
                    created_at=datetime.now(timezone.utc),
                )
            )
            db.commit()
        finally:
            db.close()

        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Inference error: %s", exc)
        raise HTTPException(status_code=500, detail="Inference failed.") from exc
