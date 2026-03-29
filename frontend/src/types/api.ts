export interface Probabilities {
  no_object: number;
  fod_detected: number;
}

export interface TopFeature {
  name: string;
  shap_value: number;
}

export interface PredictionResponse {
  prediction: 0 | 1;
  label: "No object" | "FOD detected";
  confidence: number;
  probabilities: Probabilities;
  latency_ms: number;
  model_version: string;
  top_features: TopFeature[];
}

export interface HistoryEntry extends PredictionResponse {
  id: string;
  created_at: string;
}

export interface HealthResponse {
  status: string;
  model_version: string;
  timestamp: string;
}
