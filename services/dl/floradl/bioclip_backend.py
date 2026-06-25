"""Open-ended species identification with BioCLIP.

WHY THIS IS THE DEFAULT
-----------------------
A 16-class CLIP catalog is *closed-set*: shown a plant outside the list (e.g. a
cannabis leaf) it must still pick one of the 16 and is confidently wrong. The
only real fix for "identify *any* plant" is a model trained across biodiversity.

BioCLIP (Stevens et al., CVPR 2024) is a CLIP pre-trained on TreeOfLife-10M — 10M
images spanning ~450K taxa. Its `TreeOfLifeClassifier` scores an image against the
entire known taxonomy, so it recognises species it was never explicitly asked
about. We keep the top plant-kingdom matches and surface scientific + common
names with calibrated scores.
"""

from __future__ import annotations

import os
import tempfile
from functools import lru_cache

from flora_common.schemas import SpeciesPrediction

from floradl.config import settings


def _pretty(name: str) -> str:
    return name.strip().capitalize() if name else name


class BioCLIPClassifier:
    def __init__(self):
        from bioclip import TreeOfLifeClassifier

        self._clf = TreeOfLifeClassifier()
        self.version = "bioclip-vit-b-16-treeoflife"

    def _predict_path(self, path: str):
        from bioclip import Rank

        # pybioclip returns a list of per-rank prediction dicts, score-sorted.
        return self._clf.predict(path, Rank.SPECIES)

    def predict(self, image_bytes: bytes, top_k: int = 3) -> SpeciesPrediction:
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        try:
            tmp.write(image_bytes)
            tmp.close()
            preds = self._predict_path(tmp.name)
        finally:
            try:
                os.remove(tmp.name)
            except OSError:
                pass

        if not preds:
            return SpeciesPrediction(
                label="Unknown", confidence=0.0, top_k=[],
                model_version=self.version, low_confidence=True,
            )

        # Prefer plant-kingdom matches so an ambiguous photo doesn't surface an animal.
        plants = [p for p in preds if str(p.get("kingdom", "")).lower() == "plantae"]
        ranked = plants or preds

        def display(p: dict) -> str:
            # Scientific name leads (authoritative, never misleading); friendly
            # common name in parentheses when available.
            sci = (p.get("species") or p.get("scientific_name") or "").strip()
            common = (p.get("common_name") or "").strip()
            if sci and common:
                return f"{sci} ({common})"
            return sci or _pretty(common) or "Unknown"

        best = ranked[0]
        best_score = float(best.get("score", 0.0))
        topk = [{display(p): round(float(p.get("score", 0.0)), 4)} for p in ranked[:top_k]]

        return SpeciesPrediction(
            label=display(best),
            confidence=round(best_score, 4),
            top_k=topk,
            model_version=self.version,
            low_confidence=best_score < settings.bioclip_confidence_threshold,
        )


@lru_cache(maxsize=1)
def get_bioclip() -> BioCLIPClassifier:
    return BioCLIPClassifier()
