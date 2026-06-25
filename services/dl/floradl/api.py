"""FastAPI service for plant/leaf image classification.

  GET  /health    liveness + whether a checkpoint is loaded
  GET  /info       model card (arch, classes, test accuracy)
  POST /identify   multipart image upload -> SpeciesPrediction (with abstention)
"""

from __future__ import annotations

import json

from fastapi import FastAPI, File, HTTPException, UploadFile
from flora_common import get_logger
from flora_common.schemas import SpeciesPrediction

from floradl.config import CHECKPOINT, MODELS_DIR
from floradl.inference import get_classifier

log = get_logger("floradl.api")
app = FastAPI(
    title="FloraAI · DL Service",
    version="1.0.0",
    description="Computer vision for plant/leaf classification (PyTorch transfer learning).",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": CHECKPOINT.exists()}


@app.get("/info")
def info() -> dict:
    if not CHECKPOINT.exists():
        raise HTTPException(503, "Model not trained yet. Run `python -m floradl.train`.")
    metrics_path = MODELS_DIR / "metrics.json"
    metrics = json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
    clf = get_classifier()
    return {
        "model_version": clf.version,
        "arch": clf.model.__class__.__name__,
        "classes": clf.classes,
        "test_accuracy": metrics.get("test_acc"),
    }


@app.post("/identify", response_model=SpeciesPrediction)
async def identify(file: UploadFile = File(...)) -> SpeciesPrediction:
    if not CHECKPOINT.exists():
        raise HTTPException(503, "Model not trained yet. Run `python -m floradl.train`.")
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(400, "Uploaded file must be an image.")
    image_bytes = await file.read()
    try:
        return get_classifier().predict(image_bytes)
    except Exception as exc:
        log.exception("inference failed")
        raise HTTPException(400, f"Could not process image: {exc}") from exc
