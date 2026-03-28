import io
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_MOCK_PREDICT_RESULT = {
    "prediction": 1,
    "label": "FOD detected",
    "confidence": 0.92,
    "probabilities": {"no_object": 0.08, "fod_detected": 0.92},
    "latency_ms": 15.0,
    "model_version": "v1",
}


@pytest.fixture(scope="module")
def client():
    with (
        patch(
            "backend.app.core.model_loader._load_artifacts",
            new_callable=MagicMock,
        ),
        patch(
            "backend.app.core.model_loader.predict",
            return_value=_MOCK_PREDICT_RESULT,
        ),
    ):
        with TestClient(app) as c:
            yield c


@pytest.fixture(scope="module")
def lecroy_csv_bytes():
    """85 kHz sine wave, 10 000 samples at 1 MHz — serialised as LeCroy CSV."""
    fs = 1_000_000
    n_samples = 10_000
    freq = 85_000
    t = np.arange(n_samples) / fs
    x = np.sin(2 * np.pi * freq * t)

    # prediction_service does skiprows=4 then reads the next line as the header,
    # so Time,Ampl must sit at row index 4 (the 5th row).
    lines = [
        "Waveform,,,",
        "Source,CH1,,",
        "SamplingRate,1000000,,",
        "Segment,1,,",
        "Time,Ampl",
    ]
    for ti, xi in zip(t, x):
        lines.append(f"{ti:.9f},{xi:.9f}")

    return "\n".join(lines).encode()


# ---------------------------------------------------------------------------
# /predict tests
# ---------------------------------------------------------------------------


def test_predict_returns_200(client, lecroy_csv_bytes):
    response = client.post(
        "/predict",
        files={"file": ("waveform.csv", io.BytesIO(lecroy_csv_bytes), "text/csv")},
    )
    assert response.status_code == 200


def test_predict_response_schema(client, lecroy_csv_bytes):
    response = client.post(
        "/predict",
        files={"file": ("waveform.csv", io.BytesIO(lecroy_csv_bytes), "text/csv")},
    )
    body = response.json()
    assert "prediction" in body
    assert "label" in body
    assert "confidence" in body
    assert "probabilities" in body
    assert "latency_ms" in body
    assert "model_version" in body


def test_predict_confidence_is_valid(client, lecroy_csv_bytes):
    response = client.post(
        "/predict",
        files={"file": ("waveform.csv", io.BytesIO(lecroy_csv_bytes), "text/csv")},
    )
    confidence = response.json()["confidence"]
    assert 0.0 <= confidence <= 1.0


def test_predict_probabilities_sum_to_one(client, lecroy_csv_bytes):
    response = client.post(
        "/predict",
        files={"file": ("waveform.csv", io.BytesIO(lecroy_csv_bytes), "text/csv")},
    )
    probs = response.json()["probabilities"]
    total = probs["no_object"] + probs["fod_detected"]
    assert abs(total - 1.0) < 1e-6


def test_predict_label_matches_prediction(client, lecroy_csv_bytes):
    response = client.post(
        "/predict",
        files={"file": ("waveform.csv", io.BytesIO(lecroy_csv_bytes), "text/csv")},
    )
    body = response.json()
    expected = {0: "No object", 1: "FOD detected"}
    assert body["label"] == expected[body["prediction"]]


def test_predict_invalid_file_returns_422(client):
    response = client.post(
        "/predict",
        files={"file": ("bad.csv", io.BytesIO(b"not,valid\ncsv,data\n"), "text/csv")},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# /health tests
# ---------------------------------------------------------------------------


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_schema(client):
    response = client.get("/health")
    body = response.json()
    assert "status" in body
    assert "model_version" in body
    assert "timestamp" in body
    assert body["status"] == "ok"
