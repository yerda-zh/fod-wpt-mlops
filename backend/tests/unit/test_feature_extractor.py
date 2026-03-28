import numpy as np
import pytest

from backend.ml.pipelines.feature_extractor import (
    FEATURE_ORDER,
    compute_feature_vector,
    compute_features,
)

# ---------------------------------------------------------------------------
# Shared fixture — 85 kHz sine wave, 10 000 samples at 1 MHz sample rate
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def sine_wave():
    fs = 1_000_000
    n_samples = 10_000
    freq = 85_000
    t = np.arange(n_samples) / fs
    x = np.sin(2 * np.pi * freq * t)
    return t, x


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_output_has_49_features(sine_wave):
    t, x = sine_wave
    feats = compute_features(t, x)
    assert len(feats) == 49


def test_feature_names_match_feature_order(sine_wave):
    t, x = sine_wave
    feats = compute_features(t, x)
    assert set(feats.keys()) == set(FEATURE_ORDER)
    assert list(feats.keys()) == FEATURE_ORDER


def test_feature_vector_shape(sine_wave):
    t, x = sine_wave
    vec = compute_feature_vector(t, x)
    assert vec.shape == (49,)


def test_no_nan_or_inf(sine_wave):
    t, x = sine_wave
    vec = compute_feature_vector(t, x)
    assert not np.any(np.isnan(vec)), "Feature vector contains NaN"
    assert not np.any(np.isinf(vec)), "Feature vector contains Inf"


def test_time_domain_features_reasonable(sine_wave):
    t, x = sine_wave
    feats = compute_features(t, x)
    assert feats["rms"] > 0
    assert feats["ptp"] > 0
    assert np.isfinite(feats["time_kurtosis"])


def test_spectral_features_reasonable(sine_wave):
    t, x = sine_wave
    feats = compute_features(t, x)
    assert 80_000 <= feats["peak_freq"] <= 90_000
    assert feats["thd"] >= 0


def test_wavelet_features_reasonable(sine_wave):
    t, x = sine_wave
    feats = compute_features(t, x)
    energy_keys = [k for k in FEATURE_ORDER if k.startswith("wav_energy_")]
    for key in energy_keys:
        assert 0.0 <= feats[key] <= 1.0, f"{key} = {feats[key]} is outside [0, 1]"
    assert feats["wav_detail_ratio"] > 0


def test_feature_vector_order_matches_scaler(sine_wave):
    t, x = sine_wave
    vec = compute_feature_vector(t, x)

    expected_time_mean = np.mean(x)
    expected_time_std = np.std(x)
    expected_var = np.var(x)

    assert FEATURE_ORDER[0] == "time_mean"
    assert FEATURE_ORDER[1] == "time_std"
    assert FEATURE_ORDER[2] == "var"

    assert np.isclose(vec[0], expected_time_mean, rtol=1e-9)
    assert np.isclose(vec[1], expected_time_std, rtol=1e-9)
    assert np.isclose(vec[2], expected_var, rtol=1e-9)
