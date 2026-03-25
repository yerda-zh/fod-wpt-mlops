"""
Feature extractor for FOD-WPT transmitter coil current waveforms.

Computes time-domain, spectral, and wavelet features from (t, x) arrays.
Used both during dataset construction and at inference time.
"""

import numpy as np
import pywt
from scipy import stats, signal

FEATURE_ORDER = [
    "time_mean",
    "time_std",
    "var",
    "rms",
    "ptp",
    "iqr",
    "time_skew",
    "time_kurtosis",
    "crest_factor",
    "impulse_factor",
    "shape_factor",
    "clearance_factor",
    "peak_freq",
    "peak_power",
    "harmonic_2_ratio",
    "harmonic_3_ratio",
    "harmonic_4_ratio",
    "harmonic_5_ratio",
    "harmonic_6_ratio",
    "thd",
    "snr",
    "spec_centroid",
    "spec_bandwidth",
    "spec_skew",
    "spec_kurtosis",
    "spec_entropy",
    "spec_flatness",
    "spec_rolloff",
    "total_power",
    "wav_energy_approx",
    "wav_entropy_approx",
    "wav_std_approx",
    "wav_energy_detail_5",
    "wav_entropy_detail_5",
    "wav_std_detail_5",
    "wav_energy_detail_4",
    "wav_entropy_detail_4",
    "wav_std_detail_4",
    "wav_energy_detail_3",
    "wav_entropy_detail_3",
    "wav_std_detail_3",
    "wav_energy_detail_2",
    "wav_entropy_detail_2",
    "wav_std_detail_2",
    "wav_energy_detail_1",
    "wav_entropy_detail_1",
    "wav_std_detail_1",
    "wav_detail_ratio",
    "wav_high_freq_ratio",
]


def compute_features(t: np.ndarray, x: np.ndarray, rolloff_pct: float = 0.85) -> dict:
    """
    Extract all features from a single waveform sample.

    Parameters
    ----------
    t : np.ndarray
        Time axis (seconds).
    x : np.ndarray
        Amplitude samples.
    rolloff_pct : float
        Fraction of spectral power for rolloff feature (default 0.85).

    Returns
    -------
    dict
        Feature name → scalar value (49 features total).
    """
    N = len(x)
    feats = {}

    # ------------------------------------------------------------------ #
    # Time-domain statistical features                                     #
    # ------------------------------------------------------------------ #
    feats["time_mean"] = np.mean(x)
    feats["time_std"] = np.std(x)
    feats["var"] = np.var(x)
    rms = np.sqrt(np.mean(x**2))
    feats["rms"] = rms
    feats["ptp"] = np.ptp(x)
    feats["iqr"] = float(np.percentile(x, 75) - np.percentile(x, 25))
    feats["time_skew"] = float(stats.skew(x))
    feats["time_kurtosis"] = float(stats.kurtosis(x, fisher=False))

    mean_abs = np.mean(np.abs(x))
    feats["crest_factor"] = float(np.max(np.abs(x)) / rms) if rms != 0 else 0.0
    feats["impulse_factor"] = (
        float(np.max(np.abs(x)) / mean_abs) if mean_abs != 0 else np.nan
    )
    feats["shape_factor"] = float(rms / mean_abs) if mean_abs != 0 else np.nan
    mean_sqrt = np.mean(np.sqrt(np.abs(x)))
    feats["clearance_factor"] = (
        float(np.max(np.abs(x)) / (mean_sqrt**2)) if mean_sqrt != 0 else np.nan
    )

    # ------------------------------------------------------------------ #
    # Spectral features (Welch PSD)                                        #
    # ------------------------------------------------------------------ #
    fs = 1.0 / float(np.mean(np.diff(t)))
    nperseg = 2 ** int(np.floor(np.log2(N)))
    f, Pxx = signal.welch(x, fs=fs, nperseg=nperseg)
    Pxx = np.maximum(Pxx, 1e-20)

    # Dominant / fundamental frequency
    idx_max = int(np.argmax(Pxx))
    f0 = float(f[idx_max])
    p0 = float(Pxx[idx_max])
    feats["peak_freq"] = f0
    feats["peak_power"] = p0

    # Helper: integrate power in a small window around a target frequency
    def _power_at(target_f: float, window_points: int = 2) -> float:
        idx = int(np.abs(f - target_f).argmin())
        start = max(0, idx - window_points)
        end = min(len(Pxx), idx + window_points + 1)
        return float(np.sum(Pxx[start:end]))

    # Harmonics (2nd … 6th) and THD
    num_harmonics = 5
    fund_energy = _power_at(f0)
    total_harmonic_energy = 0.0

    for h in range(2, num_harmonics + 2):
        h_freq = h * f0
        if h_freq < f[-1]:
            h_pwr = _power_at(h_freq)
            total_harmonic_energy += h_pwr
            feats[f"harmonic_{h}_ratio"] = h_pwr / (fund_energy + 1e-20)
        else:
            feats[f"harmonic_{h}_ratio"] = 0.0

    feats["thd"] = float(
        np.sqrt(total_harmonic_energy) / (np.sqrt(fund_energy) + 1e-20)
    )

    # SNR (approximate)
    total_spec_energy = float(np.sum(Pxx))
    noise_energy = max(total_spec_energy - fund_energy - total_harmonic_energy, 1e-20)
    feats["snr"] = float(10 * np.log10(fund_energy / noise_energy))

    # Spectral shape descriptors
    spec_sum = total_spec_energy + 1e-20
    centroid = float(np.sum(f * Pxx) / spec_sum)
    feats["spec_centroid"] = centroid

    bw = float(np.sqrt(np.sum(((f - centroid) ** 2) * Pxx) / spec_sum))
    feats["spec_bandwidth"] = bw

    spec_std = float(np.sqrt(np.sum(((f - centroid) ** 2) * Pxx) / total_spec_energy))
    feats["spec_skew"] = float(
        np.sum(((f - centroid) ** 3) * Pxx)
        / (total_spec_energy * (spec_std**3) + 1e-20)
    )
    feats["spec_kurtosis"] = float(
        np.sum(((f - centroid) ** 4) * Pxx)
        / (total_spec_energy * (spec_std**4) + 1e-20)
    )

    Pnorm = np.maximum(Pxx / spec_sum, 1e-20)
    feats["spec_entropy"] = float(-np.sum(Pnorm * np.log2(Pnorm)))
    feats["spec_flatness"] = float(
        np.exp(np.mean(np.log(np.maximum(Pxx, 1e-20)))) / (np.mean(Pxx) + 1e-20)
    )

    cumsum = np.cumsum(Pxx)
    roll_idx = int(np.searchsorted(cumsum, rolloff_pct * cumsum[-1]))
    feats["spec_rolloff"] = float(f[roll_idx] if roll_idx < len(f) else f[-1])
    feats["total_power"] = float(np.trapezoid(Pxx, f))

    # ------------------------------------------------------------------ #
    # Wavelet features (db4, 5 levels)                                     #
    # ------------------------------------------------------------------ #
    wavelet_name = "db4"
    decomp_level = 5

    coeffs = pywt.wavedec(x, wavelet_name, level=decomp_level)
    # coeffs = [cA5, cD5, cD4, cD3, cD2, cD1]
    total_wav_energy = float(sum(np.sum(np.array(c) ** 2) for c in coeffs))

    band_names = ["approx"] + [f"detail_{i}" for i in range(decomp_level, 0, -1)]

    for name, c in zip(band_names, coeffs):
        c = np.asarray(c)
        energy = float(np.sum(c**2))

        feats[f"wav_energy_{name}"] = energy / (total_wav_energy + 1e-20)

        p = c**2 / (energy + 1e-20)
        feats[f"wav_entropy_{name}"] = float(-np.sum(p * np.log2(p + 1e-20)))

        feats[f"wav_std_{name}"] = float(np.std(c))

    # FOD-specific wavelet ratios
    sum_detail_energy = sum(
        feats[f"wav_energy_detail_{k}"] for k in range(1, decomp_level + 1)
    )
    feats["wav_detail_ratio"] = sum_detail_energy / (feats["wav_energy_approx"] + 1e-20)

    high_freq_energy = feats["wav_energy_detail_1"] + feats["wav_energy_detail_2"]
    feats["wav_high_freq_ratio"] = high_freq_energy / (total_wav_energy + 1e-20)

    return feats


def compute_feature_vector(t: np.ndarray, x: np.ndarray) -> np.ndarray:
    """
    Returns features as a (49,) numpy array in the exact order
    the scaler was fitted on. Use this at inference time.
    """
    feats = compute_features(t, x)
    return np.array([feats[name] for name in FEATURE_ORDER], dtype=np.float64)
