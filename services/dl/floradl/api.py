"""FastAPI service for plant/leaf image classification.

  GET  /health    liveness + which identifier backend is active
  GET  /info       model card (backend, classes/catalog, accuracy if supervised)
  POST /identify   multipart image upload -> SpeciesPrediction (with abstention)

Two interchangeable backends (set FLORA_DL_IDENTIFIER_BACKEND):
  • "bioclip" (default) — open-ended identification across ~450K species.
  • "cnn"               — the supervised transfer-learning checkpoint (baseline).
"""

from __future__ import annotations

import json

from fastapi import FastAPI, File, HTTPException, UploadFile
from flora_common import get_logger
from flora_common.schemas import SpeciesPrediction

from floradl.config import CHECKPOINT, MODELS_DIR, settings

log = get_logger("floradl.api")
app = FastAPI(
    title="FloraAI · DL Service",
    version="1.1.0",
    description="Computer vision for plant identification (BioCLIP + PyTorch transfer learning).",
)

_BACKEND = settings.identifier_backend


def _predict(image_bytes: bytes) -> SpeciesPrediction:
    if _BACKEND == "bioclip":
        from floradl.bioclip_backend import get_bioclip

        return get_bioclip().predict(image_bytes)
    from floradl.inference import get_classifier

    return get_classifier().predict(image_bytes)


def _ready() -> bool:
    # BioCLIP needs no local checkpoint; the CNN backend does.
    return CHECKPOINT.exists() if _BACKEND == "cnn" else True


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "backend": _BACKEND, "model_loaded": _ready()}


@app.get("/info")
def info() -> dict:
    if not _ready():
        raise HTTPException(503, "Model not available. Train the CNN or use BioCLIP.")
    if _BACKEND == "bioclip":
        from floradl.bioclip_backend import get_bioclip

        return {
            "backend": "bioclip-tree-of-life",
            "model_version": get_bioclip().version,
            "open_vocabulary": True,
            "coverage": "~450,000 taxa across the biological tree of life",
        }
    from floradl.inference import get_classifier

    metrics_path = MODELS_DIR / "metrics.json"
    metrics = json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
    clf = get_classifier()
    return {
        "backend": "cnn-transfer-learning",
        "model_version": clf.version,
        "arch": clf.model.__class__.__name__,
        "classes": clf.classes,
        "test_accuracy": metrics.get("test_acc"),
    }


@app.post("/identify", response_model=SpeciesPrediction)
async def identify(file: UploadFile = File(...)) -> SpeciesPrediction:
    if not _ready():
        raise HTTPException(503, "Model not available.")
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(400, "Uploaded file must be an image.")
    image_bytes = await file.read()
    try:
        return _predict(image_bytes)
    except Exception as exc:
        log.exception("inference failed")
        raise HTTPException(400, f"Could not process image: {exc}") from exc
