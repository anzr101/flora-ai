"""Zero-shot plant identification with CLIP (open_clip).

WHY THIS EXISTS
---------------
The supervised CNN (`train.py`) needs labelled training images. Without a large,
real, in-the-wild plant dataset it cannot identify real photos — a model trained
on a few classes of clean/synthetic images collapses on a phone snapshot of a
Monstera (the classic out-of-distribution failure).

CLIP sidesteps that entirely: it was pre-trained on 400M image–text pairs, so it
can match a photo against arbitrary *text* labels with **no task-specific
training**. We describe each species in words, embed the photo and the
descriptions into the same space, and pick the closest. This is:
  • open-vocabulary  — add a species by adding a string, no retraining
  • robust to real photos — trained on web images, not clean studio leaves
  • honest about uncertainty — softmax over similarities + an abstention floor

We ensemble several prompt templates per class (a standard CLIP trick) to make
the text embedding more stable.
"""

from __future__ import annotations

import io
from functools import lru_cache

import torch
import torch.nn.functional as F
from PIL import Image

from flora_common.schemas import SpeciesPrediction

from floradl.config import settings

# (display label, scientific name) for common houseplants. Extend freely — each
# new entry is just text, no retraining required.
SPECIES_CATALOG: list[tuple[str, str]] = [
    ("Monstera deliciosa", "a Monstera deliciosa Swiss cheese plant, with very large glossy heart-shaped green leaves full of natural oval holes and deep slits (fenestrations)"),
    ("Snake plant", "a snake plant (Dracaena trifasciata), with tall stiff upright sword-shaped leaves with yellow edges"),
    ("Golden pothos", "a golden pothos (Epipremnum aureum), a trailing vine with small heart-shaped waxy leaves marbled yellow and green"),
    ("Peace lily", "a peace lily (Spathiphyllum), with dark green leaves and a single white spathe flower"),
    ("Fiddle-leaf fig", "a fiddle-leaf fig (Ficus lyrata), with very large leathery violin-shaped leaves"),
    ("Rubber plant", "a rubber plant (Ficus elastica), with thick glossy oval dark-green or burgundy leaves"),
    ("ZZ plant", "a ZZ plant (Zamioculcas zamiifolia), with upright stems of small glossy oval waxy leaflets"),
    ("Spider plant", "a spider plant (Chlorophytum comosum), with thin arching grass-like leaves striped white and green"),
    ("Aloe vera", "an aloe vera succulent, with a rosette of thick fleshy spiky-edged green leaves"),
    ("Jade plant", "a jade plant (Crassula ovata) succulent, with thick woody stems and small round fleshy oval leaves"),
    ("Boston fern", "a Boston fern (Nephrolepis exaltata), with long arching feathery fronds made of many tiny leaflets"),
    ("Calathea", "a Calathea prayer plant, with broad oval leaves boldly patterned with stripes and purple undersides"),
    ("Heartleaf philodendron", "a heartleaf philodendron, a vine with solid heart-shaped green leaves and no holes"),
    ("English ivy", "English ivy (Hedera helix), a trailing vine with small star-shaped lobed leaves"),
    ("Chinese evergreen", "a Chinese evergreen (Aglaonema), with broad lance-shaped leaves variegated silver, green and pink"),
    ("Phalaenopsis orchid", "a Phalaenopsis moth orchid, with arching sprays of flat round flowers"),
]

PROMPT_TEMPLATES = [
    "a photo of {desc}.",
    "a close-up photo of {desc}.",
    "a potted houseplant: {desc}.",
    "a photo of the leaves of {desc}.",
]


class ZeroShotClassifier:
    def __init__(self):
        import open_clip

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            settings.clip_model, pretrained=settings.clip_pretrained
        )
        self.model.eval().to(self.device)
        self.tokenizer = open_clip.get_tokenizer(settings.clip_model)
        self.labels = [label for label, _ in SPECIES_CATALOG]
        self.version = f"clip-{settings.clip_model}-{settings.clip_pretrained}"
        self._text_features = self._encode_catalog()

    @torch.no_grad()
    def _encode_catalog(self) -> torch.Tensor:
        """Prompt-ensembled, L2-normalised text embedding per species."""
        per_class = []
        for _, desc in SPECIES_CATALOG:
            prompts = [t.format(desc=desc) for t in PROMPT_TEMPLATES]
            tokens = self.tokenizer(prompts).to(self.device)
            feats = self.model.encode_text(tokens)
            feats = F.normalize(feats, dim=-1).mean(dim=0)  # ensemble
            per_class.append(F.normalize(feats, dim=-1))
        return torch.stack(per_class)  # (n_classes, dim)

    @torch.no_grad()
    def predict(self, image_bytes: bytes, top_k: int = 3) -> SpeciesPrediction:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        x = self.preprocess(img).unsqueeze(0).to(self.device)
        img_feat = F.normalize(self.model.encode_image(x), dim=-1)

        logit_scale = self.model.logit_scale.exp()
        logits = (logit_scale * img_feat @ self._text_features.T)[0]
        probs = logits.softmax(dim=-1).cpu()

        k = min(top_k, len(self.labels))
        top_probs, top_idx = torch.topk(probs, k)
        topk = [
            {self.labels[i]: round(float(p), 4)}
            for p, i in zip(top_probs.tolist(), top_idx.tolist())
        ]
        best_p = float(top_probs[0])
        return SpeciesPrediction(
            label=self.labels[int(top_idx[0])],
            confidence=round(best_p, 4),
            top_k=topk,
            model_version=self.version,
            low_confidence=best_p < settings.clip_confidence_threshold,
        )


@lru_cache(maxsize=1)
def get_zero_shot() -> ZeroShotClassifier:
    return ZeroShotClassifier()
