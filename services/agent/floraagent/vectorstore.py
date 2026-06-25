"""A tiny, transparent vector store: cosine similarity over a persisted matrix.

Why not Chroma/FAISS here? For a knowledge base of this size (hundreds of
chunks) a normalised matrix + a single dot product IS the nearest-neighbour
search — adding a vector-DB dependency would be over-engineering. Writing it out
also demonstrates understanding of what a vector DB does under the hood. The
`VectorStore` interface is intentionally swap-compatible with Chroma should the
corpus ever outgrow an in-memory matrix.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Chunk:
    text: str
    source: str
    chunk_id: int


class VectorStore:
    def __init__(self, vectors: np.ndarray, chunks: list[Chunk]):
        self.vectors = vectors.astype(np.float32)
        self.chunks = chunks

    # ── persistence ──────────────────────────────────────────────────────
    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        np.save(directory / "vectors.npy", self.vectors)
        (directory / "chunks.json").write_text(
            json.dumps([c.__dict__ for c in self.chunks], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, directory: Path) -> "VectorStore":
        vectors = np.load(directory / "vectors.npy")
        raw = json.loads((directory / "chunks.json").read_text(encoding="utf-8"))
        chunks = [Chunk(**c) for c in raw]
        return cls(vectors, chunks)

    @classmethod
    def exists(cls, directory: Path) -> bool:
        return (directory / "vectors.npy").exists() and (directory / "chunks.json").exists()

    # ── search ───────────────────────────────────────────────────────────
    def search(self, query_vec: np.ndarray, top_k: int = 4) -> list[tuple[Chunk, float]]:
        """Return the top_k (chunk, cosine_similarity) pairs.

        Vectors are L2-normalised at ingest, so a dot product == cosine sim.
        """
        q = query_vec.reshape(-1).astype(np.float32)
        sims = self.vectors @ q
        idx = np.argsort(sims)[::-1][:top_k]
        return [(self.chunks[i], float(sims[i])) for i in idx]

    def __len__(self) -> int:
        return len(self.chunks)
