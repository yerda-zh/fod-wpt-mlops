"""
Prediction drift report for FOD-WPT.

Compares today's prediction outputs (class distribution + confidence) from the
SQLite DB against a hardcoded reference baseline derived from training results,
then uploads the Evidently HTML report to S3.

Usage:
    python backend/ml/pipelines/drift_report.py
    python backend/ml/pipelines/drift_report.py --date 2026-04-05
"""

import argparse
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import boto3
import numpy as np
import pandas as pd
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

# Resolve project root (this file is backend/ml/pipelines/drift_report.py)
PROJECT_ROOT = Path(__file__).parents[3]
DB_PATH = PROJECT_ROOT / "fod.db"

S3_BUCKET = "fod-wpt-mlops-artifacts"
LOCAL_REPORT_PATH = "/tmp/drift_report.html"

# ---------------------------------------------------------------------------
# Reference dataset — derived from training results:
#   3,680 samples, 70% class 0 / 30% class 1, confidence mean ~0.94
# ---------------------------------------------------------------------------
_RNG_SEED = 42
_REF_SIZE = 1000


def _build_reference_df() -> pd.DataFrame:
    rng = np.random.default_rng(_RNG_SEED)
    predictions = rng.choice([0, 1], size=_REF_SIZE, p=[0.7, 0.3])

    # Beta distributions that yield per-class confidence ~0.94 mean
    confidence = np.where(
        predictions == 0,
        np.clip(rng.beta(20, 1.5, size=_REF_SIZE), 0.0, 1.0),
        np.clip(rng.beta(18, 1.5, size=_REF_SIZE), 0.0, 1.0),
    )

    return pd.DataFrame(
        {"prediction": predictions.astype(float), "confidence": confidence}
    )


# ---------------------------------------------------------------------------
# DB query
# ---------------------------------------------------------------------------


def _query_current_df(target_date: str) -> pd.DataFrame:
    """Return today's prediction rows as a DataFrame with prediction + confidence."""
    # Import here to avoid circular issues if run as a script
    sys.path.insert(0, str(PROJECT_ROOT))
    from backend.app.models.prediction import Prediction  # noqa: PLC0415

    engine = create_engine(
        f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
    )
    Session = sessionmaker(bind=engine)

    day = date.fromisoformat(target_date)
    day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    with Session() as session:
        rows = (
            session.query(Prediction.prediction, Prediction.confidence)
            .filter(
                and_(
                    Prediction.created_at >= day_start,
                    Prediction.created_at < day_end,
                )
            )
            .all()
        )

    if not rows:
        return pd.DataFrame(columns=["prediction", "confidence"])

    return pd.DataFrame(
        [{"prediction": float(r.prediction), "confidence": r.confidence} for r in rows]
    )


# ---------------------------------------------------------------------------
# Report generation + S3 upload
# ---------------------------------------------------------------------------


def _run_report(reference_df: pd.DataFrame, current_df: pd.DataFrame) -> Report:
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_df, current_data=current_df)
    report.save_html(LOCAL_REPORT_PATH)
    return report


def _upload_to_s3(target_date: str) -> str:
    s3_key = f"drift-reports/{target_date}.html"
    s3 = boto3.client("s3")
    s3.upload_file(LOCAL_REPORT_PATH, S3_BUCKET, s3_key)
    return s3_key


def _drift_detected(report: Report) -> bool:
    """Extract dataset_drift flag from the report dict."""
    try:
        result_dict = report.as_dict()
        # DataDriftPreset produces a DatasetDriftMetric as the first metric
        return result_dict["metrics"][0]["result"]["dataset_drift"]
    except (KeyError, IndexError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(target_date: str) -> None:
    print(f"[drift_report] target date: {target_date}")
    print(f"[drift_report] DB path: {DB_PATH}")

    if not DB_PATH.exists():
        print(
            f"[drift_report] WARNING: DB not found at {DB_PATH}; current dataset will be empty."
        )

    reference_df = _build_reference_df()
    current_df = _query_current_df(target_date)

    n_predictions = len(current_df)
    print(f"[drift_report] predictions today: {n_predictions}")

    if n_predictions == 0:
        print(
            "[drift_report] No predictions found for this date — skipping report generation."
        )
        return

    print("[drift_report] Running Evidently DataDriftPreset report...")
    report = _run_report(reference_df, current_df)
    print(f"[drift_report] Report saved to {LOCAL_REPORT_PATH}")

    print(
        f"[drift_report] Uploading to s3://{S3_BUCKET}/drift-reports/{target_date}.html ..."
    )
    s3_key = _upload_to_s3(target_date)
    print(f"[drift_report] Uploaded: s3://{S3_BUCKET}/{s3_key}")

    drift = _drift_detected(report)
    print(f"[drift_report] Drift detected: {'YES' if drift else 'no'}")

    # Summary line for easy log parsing
    print(
        f"\nSummary | date={target_date} | predictions={n_predictions} "
        f"| drift={'YES' if drift else 'no'} "
        f"| report=s3://{S3_BUCKET}/{s3_key}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate and upload a prediction drift report."
    )
    parser.add_argument(
        "--date",
        default=str(date.today()),
        help="Target date in YYYY-MM-DD format (default: today)",
    )
    args = parser.parse_args()
    main(args.date)
