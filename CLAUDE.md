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
Week 7-8: AWS deployment + Evidently drift detection

## Completed
- feature_extractor.py — 49 features, FEATURE_ORDER, compute_feature_vector()
- model_loader.py — lazy loading, full inference pipeline + SHAP top 5 features
- schemas/prediction.py — PredictionResponse, HealthResponse, HistoryResponse
- services/prediction_service.py — LeCroy CSV parsing, latency, DB logging
- api/routes/predict.py — POST /predict, GET /health, GET /metrics
- api/routes/history.py — GET /predictions with HistoryResponse
- models/prediction.py — SQLAlchemy Prediction model, SQLite backend
- main.py — FastAPI app, lifespan, CORS, Prometheus, both routers
- tests — 16 tests passing
- Dockerfile — multi-stage build ~300MB
- docker-compose.yml — api, db, redis, prometheus, grafana
- .github/workflows/cicd.yml — test → build → deploy placeholder
- frontend — React + TypeScript + Tailwind dashboard
  - PredictPage: drag-drop upload, confidence bar, SHAP chart
  - HistoryPage: prediction table with timestamps and filter
  - MonitoringPage: Grafana iframe embed

## Commands
- Activate venv: source .venv/bin/activate
- Run API: uvicorn backend.app.main:app --reload
- Run tests: pytest backend/tests/
- MLflow UI: mlflow ui --port 5000
