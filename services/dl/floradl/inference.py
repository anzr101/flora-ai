"""Inference: load a trained checkpoint and classify a single image.

Includes **abstention** — if the top softmax probability is below the configured
threshold, the prediction is flagged `low_confidence`. This is the honest
response to an out-of-distribution photo (e.g. a real field image when the model
was trained on clean studio images), rather than confidently mislabelling it.
"""

from __future__ import annotations

import io
from functools import lru_cache

import torch
import torch.nn.functional as F
from PIL import Image

from flora_common.schemas import SpeciesPrediction

from floradl.config import CHECKPOINT, settings
from floradl.model import build_model, device
from floradl.transforms import build_transforms


class Classifier:
    def __init__(self, checkpoint_path=CHECKPOINT):
        ckpt = torch.load(checkpoint_path, map_location="cpu")
        self.classes: list[str] = ckpt["classes"]
        self.version: str = ckpt.get("version", "unknown")
        self.image_size = ckpt.get("image_size", settings.image_size)
        self.device = device()
        self.model = build_model(num_classes=len(self.classes), arch=ckpt["arch"], pretrained=False)
        self.model.load_state_dict(ckpt["state_dict"])
        self.model.to(self.device).eval()
        self.transform = build_transforms(train=False)

    @torch.no_grad()
    def predict(self, image_bytes: bytes, top_k: int = 3) -> SpeciesPrediction:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        x = self.transform(img).unsqueeze(0).to(self.device)
        probs = F.softmax(self.model(x), dim=1)[0].cpu()

        k = min(top_k, len(self.classes))
        top_probs, top_idx = torch.topk(probs, k)
        topk = [
            {self.classes[i]: round(float(p), 4)}
            for p, i in zip(top_probs.tolist(), top_idx.tolist())
        ]
        best_p = float(top_probs[0])
        best_label = self.classes[int(top_idx[0])]

        return SpeciesPrediction(
            label=best_label,
            confidence=round(best_p, 4),
            top_k=topk,
            model_version=self.version,
            low_confidence=best_p < settings.confidence_threshold,
        )


@lru_cache(maxsize=1)
def get_classifier() -> Classifier:
    if not CHECKPOINT.exists():
        raise RuntimeError(
            f"No checkpoint at {CHECKPOINT}. Train first: `python -m floradl.train`."
        )
    return Classifier()
