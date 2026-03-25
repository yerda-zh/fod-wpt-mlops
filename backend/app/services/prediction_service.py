import io
import time

import numpy as np
import pandas as pd
from fastapi import HTTPException

from backend.app.core import model_loader

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
        raise HTTPException(status_code=422, detail=f"CSV parse error: {exc}") from exc

    try:
        t = df["Time"].to_numpy(dtype=np.float64)
        x = df["Ampl"].to_numpy(dtype=np.float64)
        result = model_loader.predict(t, x)
        latency_ms = (time.perf_counter() - t0) * 1000
        result["latency_ms"] = latency_ms
        result["model_version"] = MODEL_VERSION
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference error: {exc}") from exc
