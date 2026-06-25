"""FastAPI service exposing the trained plant health-risk model.

Endpoints:
  GET  /health   liveness + whether a model is loaded
  GET  /info     model card: version, metrics, global feature importance
  POST /predict  PlantConditions -> HealthPrediction (with local SHAP drivers)

The model is loaded once at startup. If no model artifact exists yet, the
service still starts and reports `model_loaded=false` so orchestration/health
checks behave sensibly — predictions then return HTTP 503 with a clear message.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from flora_common import get_logger
from flora_common.schemas import HealthPrediction, PlantConditions

from floraml.config import CLASS_NAMES, FEATURE_COLUMNS, settings
from floraml.explain import local_drivers
from floraml.train import METRICS_PATH, MODEL_PATH

log = get_logger("floraml.api")

_STATE: dict = {"model": None, "metrics": {}, "version": "untrained"}


def _load_model() -> None:
    if MODEL_PATH.exists():
        _STATE["model"] = joblib.load(MODEL_PATH)
        if METRICS_PATH.exists():
            _STATE["metrics"] = json.loads(METRICS_PATH.read_text())
            _STATE["version"] = _STATE["metrics"].get("model_version", "unknown")
        log.info(f"Loaded model version={_STATE['version']}")
    else:
        log.warning("No model artifact found; run `python -m floraml.train` first.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_model()
    yield


app = FastAPI(
    title="FloraAI · ML Service",
    version="1.0.0",
    description="Classical ML for structured plant health-risk prediction.",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": _STATE["model"] is not None}


@app.get("/info")
def info() -> dict:
    if _STATE["model"] is None:
        raise HTTPException(503, "Model not trained yet.")
    m = _STATE["metrics"]
    return {
        "model_version": _STATE["version"],
        "selected_model": m.get("selected_model"),
        "test_accuracy": m.get("test_accuracy"),
        "test_macro_f1": m.get("test_macro_f1"),
        "top_global_features": dict(list(m.get("global_importance", {}).items())[:6]),
    }


@app.post("/predict", response_model=HealthPrediction)
def predict(conditions: PlantConditions) -> HealthPrediction:
    model = _STATE["model"]
    if model is None:
        raise HTTPException(503, "Model not trained yet. Run `python -m floraml.train`.")

    row = pd.DataFrame([{c: getattr(conditions, c) for c in FEATURE_COLUMNS}])
    proba = model.predict_proba(row)[0]
    classes = list(model.classes_)
    probs = {cls: float(p) for cls, p in zip(classes, proba)}
    # Order probabilities by the canonical class order for stable responses.
    probs = {c: probs.get(c, 0.0) for c in CLASS_NAMES}

    pred_label = max(probs, key=probs.get)
    pred_index = classes.index(pred_label)
    risk_score = 1.0 - probs.get("healthy", 0.0)  # P(not healthy)

    drivers = local_drivers(model, row, class_index=pred_index)

    if max(proba) < settings.confidence_floor:
        log.info(f"Low-confidence prediction (max p={max(proba):.2f})")

    return HealthPrediction(
        risk_label=pred_label,  # type: ignore[arg-type]
        risk_score=round(risk_score, 4),
        class_probabilities={k: round(v, 4) for k, v in probs.items()},
        top_drivers=drivers,
        model_version=_STATE["version"],
    )
