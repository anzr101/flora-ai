"""Embedding backends.

Design decision: Claude has **no embeddings endpoint**, and paying per token to
embed a static knowledge base would be wasteful. So embeddings run locally.

We use `fastembed` (ONNX runtime) rather than `sentence-transformers` so the RAG
container stays small and **torch-free** — a deliberate footprint/cost choice.

A deterministic `hash` backend is provided for tests/CI so the suite never
touches the network or downloads a model.
"""

from __future__ import annotations

import hashlib

import numpy as np

from floraagent.config import settings


class HashEmbedder:
    """Deterministic, offline embedder: hashes tokens into a fixed vector.

    Not semantically strong, but it exercises the full retrieval plumbing with
    zero downloads — ideal for unit tests and CI.
    """

    dim = 384

    def embed(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for token in text.lower().split():
                h = int(hashlib.md5(token.encode()).hexdigest(), 16)
                out[i, h % self.dim] += 1.0
        return _l2_normalize(out)


class FastEmbedEmbedder:
    """Real semantic embeddings via fastembed (ONNX)."""

    def __init__(self, model_name: str):
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model_name)
        self.dim = 384  # bge-small / MiniLM family

    def embed(self, texts: list[str]) -> np.ndarray:
        vecs = np.array(list(self._model.embed(texts)), dtype=np.float32)
        return _l2_normalize(vecs)


def _l2_normalize(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return x / norms


def get_embedder():
    """Factory honouring FLORA_EMBED_BACKEND."""
    if settings.flora_embed_backend == "hash":
        return HashEmbedder()
    try:
        return FastEmbedEmbedder(settings.flora_embedding_model)
    except Exception as exc:  # pragma: no cover - environment dependent
        # Fail loud in production, but don't crash if fastembed isn't present.
        raise RuntimeError(
            "fastembed unavailable; set FLORA_EMBED_BACKEND=hash for offline use."
        ) from exc
