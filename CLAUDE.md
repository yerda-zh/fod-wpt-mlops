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
Week 1-2: FastAPI backend + feature extractor

## Completed
- feature_extractor.py — 49 features, FEATURE_ORDER, compute_feature_vector()
- model_loader.py — lazy loading, full inference pipeline
- schemas/prediction.py — PredictionResponse, HealthResponse, Probabilities
- services/prediction_service.py — LeCroy CSV parsing, latency tracking

## Commands
- Activate venv: source .venv/bin/activate
- Run API: uvicorn backend.app.main:app --reload
- Run tests: pytest backend/tests/
- MLflow UI: mlflow ui --port 5000
