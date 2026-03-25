from pydantic import BaseModel, ConfigDict


class Probabilities(BaseModel):
    model_config = ConfigDict(frozen=True, protected_namespaces=())

    no_object: float
    fod_detected: float


class PredictionResponse(BaseModel):
    model_config = ConfigDict(frozen=True, protected_namespaces=())

    prediction: int
    label: str
    confidence: float
    probabilities: Probabilities
    latency_ms: float
    model_version: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True, protected_namespaces=())

    status: str
    model_version: str
    timestamp: str
