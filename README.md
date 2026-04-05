# FOD-WPT MLOps — Foreign Object Detection for Wireless Power Transfer

End-to-end MLOps system that deploys a Random Forest classifier detecting metallic foreign objects on wireless charging pads, achieving F1: 0.9783 and ROC AUC: 0.9966.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20ECR%20%7C%20S3-FF9900?logo=amazon-aws&logoColor=white)

**Live demo:** http://107.22.94.101

> **Screenshots:** Predict page with SHAP chart, History table, Monitoring dashboard
> *(add after taking screenshots)*

---

## Problem statement

Small conductive objects — keys, coins, wrenches — left on wireless charging pads induce eddy currents that cause localised overheating, potentially damaging devices or creating fire hazards. Commercial WPT systems typically rely on dedicated sensor hardware (coils, cameras, or capacitive plates) to detect foreign object debris (FOD).

This system takes a different approach: it analyses the transmitter coil current waveform, which is already measured for power control purposes, and detects FOD signatures from that signal alone. **No additional hardware is required.** A 49-feature vector is extracted from each waveform, reduced to 10 discriminative features via Pearson correlation and Recursive Feature Elimination, and classified by a Random Forest model in real time.

**Dataset:** 3,680 transmitter coil current waveforms captured via Teledyne LeCroy HDO8108R oscilloscope — 1,680 with foreign objects (wrench, bolt, coin, aluminium can) across a 5×5 grid with 20 orientations per cell, and 2,000 baseline samples.

---

## ML results

| Model | F1 | ROC AUC | Kappa | Brier |
|---|---|---|---|---|
| **Random Forest** ✓ | **0.9783** | **0.9966** | **0.9562** | 0.0253 |
| XGBoost | 0.9728 | 0.9961 | 0.9453 | 0.0208 |
| MLP | 0.9728 | 0.9960 | 0.9453 | 0.0210 |
| SVM | 0.9193 | 0.9665 | 0.8373 | 0.0621 |

Training set: 3,680 samples, 70/30 stratified split, z-score normalised.

---

## System architecture

```
LeCroy CSV (waveform)
        │
        ▼
┌───────────────────┐
│   FastAPI backend │
│                   │
│  Feature extractor│  ──▶  49 features (time-domain, spectral, wavelet)
│  StandardScaler   │  ──▶  z-score normalised
│  Feature selector │  ──▶  10 features (Pearson + RFE)
│  Random Forest    │  ──▶  prediction + class probabilities
│  SHAP explainer   │  ──▶  top 5 feature attributions
│  SQLite logger    │  ──▶  prediction history
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  React dashboard  │
│                   │
│  • Predict page   │  drag-drop upload, confidence bar, SHAP chart
│  • History page   │  prediction table with timestamps
│  • Monitoring page│  live Grafana iframe, drift status card
└───────────────────┘
```

---

## Tech stack

| Layer | Technology |
|---|---|
| ML | scikit-learn, XGBoost, SHAP, Evidently AI |
| API | FastAPI, Pydantic v2, SQLAlchemy, SQLite |
| Frontend | React 18, TypeScript, Tailwind CSS, TanStack Query, Recharts |
| Infrastructure | Docker, Docker Compose, GitHub Actions, AWS EC2 / ECR / S3 |
| Monitoring | Prometheus, Grafana |
| IaC | Terraform |

---

## Key features

- **Real-time FOD detection** — upload a waveform CSV and get a prediction in milliseconds
- **SHAP explainability** — every prediction includes the top 5 contributing features with SHAP values
- **Prediction history** — all inferences logged to SQLite, browsable via the History page
- **Live Grafana dashboard** — request rate, latency, and system metrics streamed from Prometheus
- **Nightly Evidently drift detection** — prediction distribution compared against training baseline; HTML report uploaded to S3
- **CI/CD pipeline** — GitHub Actions runs tests, builds the Docker image, and deploys to EC2 on every push to `main`
- **IaC with Terraform** — all AWS resources (EC2, ECR, S3, Elastic IP, security group) are codified and reproducible

---

## Project structure

```
fod-wpt-mlops/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── predict.py          # POST /predict, GET /health, GET /metrics
│   │   │   └── history.py          # GET /predictions, GET /drift/latest
│   │   ├── core/
│   │   │   └── model_loader.py     # lazy artifact loading, full inference pipeline
│   │   ├── models/
│   │   │   └── prediction.py       # SQLAlchemy Prediction model + SQLite engine
│   │   ├── schemas/
│   │   │   └── prediction.py       # Pydantic request/response schemas
│   │   ├── services/
│   │   │   └── prediction_service.py  # CSV parsing, DB logging, latency tracking
│   │   └── main.py                 # FastAPI app, CORS, Prometheus, lifespan
│   ├── ml/
│   │   ├── pipelines/
│   │   │   ├── feature_extractor.py   # 49-feature extraction from waveforms
│   │   │   └── drift_report.py        # Evidently drift report → S3
│   │   └── registry/
│   │       └── mlflow_registry.py     # log, load, and promote models via MLflow
│   ├── tests/
│   │   ├── unit/                   # unit tests for feature extractor, schemas
│   │   └── integration/            # integration tests for API routes
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── PredictPage.tsx     # drag-drop upload + SHAP chart
│   │   │   ├── HistoryPage.tsx     # prediction history table
│   │   │   └── MonitoringPage.tsx  # Grafana iframe + drift status card
│   │   ├── components/             # HistoryTable, ConfidenceBar, ShapChart, …
│   │   ├── hooks/                  # useHistory, usePrediction
│   │   └── utils/api.ts            # axios client
│   └── package.json
├── infrastructure/
│   └── terraform/
│       ├── main.tf                 # EC2, ECR, S3, Elastic IP, security group
│       ├── variables.tf            # aws_region, instance_type, key_pair_name, bucket_name
│       └── README.md
├── monitoring/
│   ├── prometheus/                 # prometheus.yml scrape config
│   └── grafana/dashboards/         # Grafana dashboard JSON
├── notebooks/
│   ├── feature_extraction.ipynb    # exploratory feature engineering
│   └── ml_classification.ipynb     # model training, comparison, selection
├── .github/workflows/cicd.yml      # test → build → deploy pipeline
├── docker-compose.yml              # api, prometheus, grafana services
└── Dockerfile                      # multi-stage build (~300 MB)
```

---

## Local development

### Python backend

```bash
git clone <repo-url>
cd fod-wpt-mlops

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

uvicorn backend.app.main:app --reload
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### React frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard available at http://localhost:5173
```

### Docker Compose (full stack)

```bash
docker compose up --build
# API:        http://localhost:8000
# Grafana:    http://localhost:3000
# Prometheus: http://localhost:9090
```

---

## Feature extraction

Each waveform is reduced to a 49-dimensional feature vector across three domains:

| Domain | Count | Examples |
|---|---|---|
| Time-domain | 12 | mean, RMS, peak-to-peak, skewness, kurtosis, crest factor, impulse factor |
| Spectral (Welch PSD) | 17 | peak frequency, harmonics 2–6, THD, spectral centroid, entropy, flatness |
| Wavelet (db4, 5 levels) | 20 | energy, entropy, std per band, high-frequency energy ratio |

Feature selection reduces these to **10 features** using Pearson correlation (removes redundancy) followed by Recursive Feature Elimination with cross-validation. See `notebooks/feature_extraction.ipynb` for the full analysis.

---

## CI/CD pipeline

The GitHub Actions workflow (`.github/workflows/cicd.yml`) runs on every push to `main`:

1. **test** — installs dependencies and runs `pytest backend/tests/ -v` on Python 3.11
2. **build** — authenticates to ECR, builds the Docker image, and pushes it tagged with the Git SHA and `latest`
3. **deploy** — SSHes into the EC2 instance, pulls the new image from ECR, and restarts the container

Pull requests only trigger the `test` job; `build` and `deploy` are gated to pushes on `main`.

---

## Drift detection

A nightly script (`backend/ml/pipelines/drift_report.py`) queries today's predictions from the SQLite database and compares the confidence and class distribution against a reference baseline derived from the training set (70% class 0 / 30% class 1, confidence mean ~0.94). It runs an [Evidently AI](https://www.evidentlyai.com/) `DataDriftPreset` report and uploads the HTML output to `s3://fod-wpt-mlops-artifacts/drift-reports/YYYY-MM-DD.html`. The current report status and today's prediction count are surfaced in the dashboard via `GET /drift/latest`.

Run manually for a specific date:

```bash
python backend/ml/pipelines/drift_report.py --date 2026-04-06
```

---

## Research notebooks

The `notebooks/` directory contains the original research used to build this system:

- **`feature_extraction.ipynb`** — waveform visualisation, feature engineering rationale, correlation analysis, and RFE feature selection
- **`ml_classification.ipynb`** — training and evaluation of Random Forest, XGBoost, MLP, and SVM; ROC curves, confusion matrices, SHAP summary plots, and final model selection
