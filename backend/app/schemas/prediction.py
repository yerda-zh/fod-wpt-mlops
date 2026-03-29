from pydantic import BaseModel, ConfigDict


class Probabilities(BaseModel):
    model_config = ConfigDict(frozen=True, protected_namespaces=())

    no_object: float
    fod_detected: float


class TopFeature(BaseModel):
    model_config = ConfigDict(frozen=True, protected_namespaces=())

    name: str
    shap_value: float


class PredictionResponse(BaseModel):
    model_config = ConfigDict(frozen=True, protected_namespaces=())

    prediction: int
    label: str
    confidence: float
    probabilities: Probabilities
    latency_ms: float
    model_version: str
    top_features: list[TopFeature]


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True, protected_namespaces=())

    status: str
    model_version: str
    timestamp: str


class HistoryResponse(PredictionResponse):
    model_config = ConfigDict(frozen=True, protected_namespaces=())
    id: str
    created_at: str
