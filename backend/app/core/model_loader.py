"""
Model loader for FOD-WPT inference.

Exposes a single predict() function that runs the full inference pipeline.
Artifacts are loaded lazily on first call to predict().
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import os

from backend.ml.pipelines.feature_extractor import FEATURE_ORDER, compute_feature_vector

# 49 feature names the scaler was fitted on — same order as FEATURE_ORDER
SCALER_FEATURE_NAMES = FEATURE_ORDER

# 10 features selected by Pearson correlation + RFE
SELECTED_FEATURES = [
    "time_mean",
    "ptp",
    "time_skew",
    "time_kurtosis",
    "impulse_factor",
    "harmonic_2_ratio",
    "spec_centroid",
    "wav_entropy_approx",
    "wav_energy_detail_1",
    "wav_high_freq_ratio",
]

_MODELS_DIR = Path(os.getenv("MODELS_DIR", Path(__file__).parents[3] / "models"))

_scaler = None
_model = None

_LABELS = {0: "No object", 1: "FOD detected"}


def _load_artifacts() -> None:
    """Load scaler and model from disk on first call; no-op on subsequent calls."""
    global _scaler, _model
    if _scaler is None:
        _scaler = joblib.load(_MODELS_DIR / "FOD_Scaler_20260202_173744.joblib")
        _model = joblib.load(
            _MODELS_DIR / "Random_Forest_(RF)_FOD_Model_20260202_173744.joblib"
        )


def predict(t: np.ndarray, x: np.ndarray) -> dict:
    """
    Run the full inference pipeline on a single waveform.

    Parameters
    ----------
    t : np.ndarray
        Time axis (seconds).
    x : np.ndarray
        Amplitude samples.

    Returns
    -------
    dict
        prediction   : int   — class index (0 or 1)
        label        : str   — "No object" | "FOD detected"
        confidence   : float — predicted-class probability
        probabilities: dict  — {"no_object": float, "fod_detected": float}
    """
    # 0. Load Artifacts
    _load_artifacts()
    assert _scaler is not None
    assert _model is not None

    # 1. Extract 49 features → shape (49,)
    vec = compute_feature_vector(t, x)

    # 2-3. Wrap in DataFrame before scaling — scaler was fitted on a DataFrame,
    #      so passing one here satisfies sklearn 1.6 feature-name validation.
    df_raw = pd.DataFrame(vec.reshape(1, -1), columns=SCALER_FEATURE_NAMES)
    scaled = _scaler.transform(df_raw)  # shape (1, 49), ndarray
    df_full = pd.DataFrame(scaled, columns=SCALER_FEATURE_NAMES)

    # 4. Slice to the 10 selected features → shape (1, 10)
    df_sel = df_full[SELECTED_FEATURES]

    # 5. Class prediction
    pred_class = int(_model.predict(df_sel)[0])

    # 6. Class probabilities
    proba = _model.predict_proba(df_sel)[0]  # shape (2,)

    # 7. Return structured result
    return {
        "prediction": pred_class,
        "label": _LABELS[pred_class],
        "confidence": float(proba[pred_class]),
        "probabilities": {
            "no_object": float(proba[0]),
            "fod_detected": float(proba[1]),
        },
    }
