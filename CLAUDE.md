# FOD-WPT MLOps Project

## Project overview
Foreign object detection system for wireless power transfer (WPT) using ML.
Deploys a Random Forest classifier (F1: 0.9783, ROC AUC: 0.9966) that analyzes
transmitter coil current waveforms to detect metallic objects on charging pads.

## Stack
- Backend: FastAPI + Python 3.11
- Frontend: React + TypeScript + Tailwind CSS
- ML: scikit-learn Random Forest, XGBoost, SHAP for explainability
- MLOps: MLflow (model registry), Evidently AI (drift detection)
- Monitoring: Prometheus + Grafana
- Infra: Docker, GitHub Actions CI/CD, AWS EC2 + S3 + ECR

## Key ML details
- Input: 49 extracted features from transmitter coil current waveforms
  (time-domain, spectral, wavelet)
- After feature selection: 10 features (Pearson correlation + RFE)
- Classes: no object, object detected
- Training data: 3,680 samples (70/30 stratified split, z-score normalized)

## Current build phase
Week 5-6: React frontend dashboard

## Completed
- feature_extractor.py — 49 features, FEATURE_ORDER, compute_feature_vector()
- model_loader.py — lazy loading, full inference pipeline (49→scale→10→RF)
- schemas/prediction.py — PredictionResponse, HealthResponse, Probabilities
- services/prediction_service.py — LeCroy CSV parsing, latency tracking
- api/routes/predict.py — POST /predict, GET /health, GET /metrics
- main.py — FastAPI app, lifespan, CORS, Prometheus instrumentation
- tests/unit/test_feature_extractor.py — 8 tests, all passing
- tests/integration/test_predict_endpoint.py — 8 tests, mocked for CI
- Dockerfile — multi-stage build, ~300MB runtime image
- docker-compose.yml — api, db, redis, prometheus, grafana
- .github/workflows/cicd.yml — test → build → deploy placeholder

## Commands
- Activate venv: source .venv/bin/activate
- Run API: uvicorn backend.app.main:app --reload
- Run tests: pytest backend/tests/
- MLflow UI: mlflow ui --port 5000
