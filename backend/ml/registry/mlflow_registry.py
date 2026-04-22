"""
MLflow Model Registry helpers for FOD-WPT.

Three public functions:
  - log_training_run   — log a sklearn run and register the model
  - load_model_by_stage — load the latest model in a given stage/alias
  - promote_model       — promote a version to Staging or Production

MLflow tracking server defaults to the local `mlruns/` directory unless
MLFLOW_TRACKING_URI is set in the environment.
"""

import os

import mlflow
import mlflow.sklearn
from mlflow import MlflowClient

REGISTRY_NAME = "FOD-RandomForest"

_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
mlflow.set_tracking_uri(_TRACKING_URI)


# ---------------------------------------------------------------------------
# log_training_run
# ---------------------------------------------------------------------------


def log_training_run(
    model,
    scaler,
    feature_names: list[str],
    metrics: dict,
    experiment_name: str = "FOD-WPT",
) -> str:
    """Log a completed training run to MLflow and register the model.

    Logs the sklearn pipeline artifacts (model + scaler), the feature name
    list, and any scalar metrics supplied by the caller. The model is
    registered in the MLflow Model Registry under ``REGISTRY_NAME``.

    Parameters
    ----------
    model:
        Fitted sklearn estimator (e.g. RandomForestClassifier).
    scaler:
        Fitted sklearn scaler (e.g. StandardScaler). Logged as a separate
        artifact under ``artifacts/scaler/``.
    feature_names:
        Ordered list of feature names the model was trained on (the 10
        selected features).
    metrics:
        Dict of scalar metrics to log, e.g.
        ``{"f1": 0.9783, "roc_auc": 0.9966, "kappa": 0.951}``.
    experiment_name:
        MLflow experiment to log under (created if it does not exist).

    Returns
    -------
    str
        The MLflow run ID of the logged run.
    """
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run() as run:
        # Log scalar metrics
        mlflow.log_metrics(metrics)

        # Log feature list as a param (joined string — easy to read in the UI)
        mlflow.log_param("features", ",".join(feature_names))
        mlflow.log_param("n_features", len(feature_names))

        # Log the sklearn model and register it in the Model Registry
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=REGISTRY_NAME,
            input_example=None,
        )

        # Log the scaler as a separate sklearn artifact (not registered)
        mlflow.sklearn.log_model(
            sk_model=scaler,
            artifact_path="scaler",
        )

        run_id = run.info.run_id

    print(f"[mlflow_registry] Run logged: {run_id}")
    return run_id


# ---------------------------------------------------------------------------
# load_model_by_stage
# ---------------------------------------------------------------------------


def load_model_by_stage(stage: str = "Production"):
    """Load the latest model version in the given stage from the registry.

    Uses the MLflow Model Registry alias convention supported by MLflow 3.x.
    The ``stage`` value is used directly as a registered model alias
    (e.g. "Production", "Staging").  If no alias exists with that name the
    function falls back to searching version tags/stages via ``MlflowClient``
    for backwards compatibility with older servers.

    Parameters
    ----------
    stage:
        Registry alias or stage name to load. Defaults to ``"Production"``.

    Returns
    -------
    sklearn estimator
        The deserialized sklearn model object ready for inference.
    """
    model_uri = f"models:/{REGISTRY_NAME}@{stage}"
    try:
        model = mlflow.sklearn.load_model(model_uri)
        print(f"[mlflow_registry] Loaded model via alias: {model_uri}")
        return model
    except mlflow.exceptions.MlflowException:
        pass

    # Fallback: find the latest version whose stage matches (MLflow <2 style)
    client = MlflowClient()
    versions = client.search_model_versions(f"name='{REGISTRY_NAME}'")
    matching = [v for v in versions if (v.current_stage or "").lower() == stage.lower()]
    if not matching:
        raise ValueError(
            f"No model version found for '{REGISTRY_NAME}' with stage/alias '{stage}'."
        )
    latest = max(matching, key=lambda v: int(v.version))
    model_uri = f"models:/{REGISTRY_NAME}/{latest.version}"
    model = mlflow.sklearn.load_model(model_uri)
    print(
        f"[mlflow_registry] Loaded model version {latest.version} (fallback stage lookup)"
    )
    return model


# ---------------------------------------------------------------------------
# promote_model
# ---------------------------------------------------------------------------


def promote_model(version: int, stage: str) -> None:
    """Promote a registered model version to the given stage.

    Sets both the MLflow 3.x alias (recommended) and the legacy
    ``current_stage`` field (for compatibility with older clients / UIs that
    still read the stage column).

    Parameters
    ----------
    version:
        Integer version number of the registered model to promote.
    stage:
        Target stage. Must be one of ``"Staging"`` or ``"Production"``.

    Raises
    ------
    ValueError
        If ``stage`` is not one of the two allowed values.
    """
    allowed = {"Staging", "Production"}
    if stage not in allowed:
        raise ValueError(f"stage must be one of {allowed}, got '{stage}'.")

    client = MlflowClient()

    # MLflow 3.x: set alias so models:/<name>@<stage> URIs resolve correctly
    client.set_registered_model_alias(
        name=REGISTRY_NAME,
        alias=stage,
        version=str(version),
    )

    # Legacy transition for backwards-compatible UIs and older mlflow clients
    try:
        client.transition_model_version_stage(
            name=REGISTRY_NAME,
            version=str(version),
            stage=stage,
            archive_existing_versions=True,
        )
    except mlflow.exceptions.MlflowException:
        # transition_model_version_stage removed in some mlflow 3.x builds
        pass

    print(f"[mlflow_registry] Version {version} promoted to '{stage}'.")


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler

    print("=== MLflow Registry — example run ===")
    print(f"Tracking URI: {mlflow.get_tracking_uri()}")

    # 1. Simulate a trained model + scaler
    rng = np.random.default_rng(0)
    X = rng.standard_normal((100, 10))
    y = rng.integers(0, 2, 100)

    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)
    model = RandomForestClassifier(n_estimators=10, random_state=0).fit(X_scaled, y)

    feature_names = [
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
    metrics = {"f1": 0.9783, "roc_auc": 0.9966, "kappa": 0.951}

    # 2. Log the run and register the model
    run_id = log_training_run(model, scaler, feature_names, metrics)
    print(f"Run ID: {run_id}")

    # 3. Promote version 1 to Staging, then Production
    promote_model(version=1, stage="Staging")
    promote_model(version=1, stage="Production")

    # 4. Load it back
    loaded = load_model_by_stage("Production")
    print(f"Loaded model type: {type(loaded).__name__}")
    sample = scaler.transform(rng.standard_normal((1, 10)))
    print(f"Sample prediction: {loaded.predict(sample)}")
