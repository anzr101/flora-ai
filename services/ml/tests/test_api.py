"""API tests. A tiny model is trained on the fly so the suite is self-contained
and does not depend on a previously-saved artifact."""

from __future__ import annotations

import joblib
import pytest
from fastapi.testclient import TestClient
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline

from floraml.config import FEATURE_COLUMNS, TARGET_COLUMN
from floraml.features import build_preprocessor
from floraml.generate_data import generate


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    # Train a small fast model and point the API state at it.
    df = generate(n=1500, seed=11)
    model = Pipeline(
        [
            ("pre", build_preprocessor(scale=False)),
            ("model", HistGradientBoostingClassifier(max_iter=80, random_state=0)),
        ]
    )
    model.fit(df[FEATURE_COLUMNS], df[TARGET_COLUMN].astype(str))

    from floraml import api

    api._STATE["model"] = model
    api._STATE["version"] = "test-v1"
    api._STATE["metrics"] = {"selected_model": "hist_gbm", "test_accuracy": 0.8}
    return TestClient(api.app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["model_loaded"] is True


def test_predict_contract(client):
    payload = {
        "temperature_c": 38,
        "humidity_pct": 20,
        "soil_moisture_pct": 8,
        "light_hours": 14,
        "soil_ph": 8.5,
        "watering_freq_per_week": 0,
        "fertilizer_freq_per_month": 0,
        "plant_age_months": 5,
    }
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["risk_label"] in {"healthy", "at_risk", "diseased"}
    assert 0.0 <= body["risk_score"] <= 1.0
    # Probabilities are present for all three classes and roughly sum to 1.
    probs = body["class_probabilities"]
    assert set(probs) == {"healthy", "at_risk", "diseased"}
    assert abs(sum(probs.values()) - 1.0) < 1e-3


def test_predict_validation_rejects_bad_input(client):
    bad = {"temperature_c": 999}  # missing fields + out of range
    r = client.post("/predict", json=bad)
    assert r.status_code == 422
