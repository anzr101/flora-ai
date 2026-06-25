"""Retrieval over the persisted vector store.

Lazily loads the store and embedder once, then answers similarity queries and
returns chunks with their source for citation.
"""

from __future__ import annotations

from functools import lru_cache

from flora_common.schemas import Citation

from floraagent.config import VECTORSTORE_DIR, settings
from floraagent.embeddings import get_embedder
from floraagent.vectorstore import VectorStore


@lru_cache(maxsize=1)
def _resources():
    if not VectorStore.exists(VECTORSTORE_DIR):
        raise RuntimeError(
            f"No vector store at {VECTORSTORE_DIR}. Run `python -m floraagent.ingest` first."
        )
    return VectorStore.load(VECTORSTORE_DIR), get_embedder()


def retrieve(query: str, top_k: int | None = None) -> list[tuple[str, str, float]]:
    """Return [(text, source, score)] for the most relevant chunks."""
    store, embedder = _resources()
    qvec = embedder.embed([query])[0]
    hits = store.search(qvec, top_k=top_k or settings.top_k)
    return [(c.text, c.source, score) for c, score in hits]


def retrieve_with_citations(query: str, top_k: int | None = None):
    """Return (context_block, citations) ready for prompt-stuffing + the response."""
    hits = retrieve(query, top_k)
    context = "\n\n".join(f"[{src}]\n{text}" for text, src, _ in hits)
    citations = [
        Citation(source=src, snippet=text[:200].replace("\n", " ").strip())
        for text, src, _ in hits
    ]
    return context, citations
