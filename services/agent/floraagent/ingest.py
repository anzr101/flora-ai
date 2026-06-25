"""Build the RAG vector store from the markdown knowledge base.

Chunking strategy: paragraph-aware, character-bounded windows with overlap, so a
chunk rarely splits a coherent idea and adjacent context isn't lost at the seam.
Each chunk keeps its source filename for citation.

Run:  python -m floraagent.ingest
"""

from __future__ import annotations

import re

from floraagent.config import KNOWLEDGE_DIR, VECTORSTORE_DIR, settings
from floraagent.embeddings import get_embedder
from floraagent.vectorstore import Chunk, VectorStore


def _chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split into ~`size`-char chunks on paragraph boundaries where possible."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}".strip()
        else:
            if current:
                chunks.append(current)
            # Carry a tail of the previous chunk for context continuity.
            tail = current[-overlap:] if overlap and current else ""
            current = f"{tail}\n\n{para}".strip() if tail else para
            # A single very long paragraph gets hard-split.
            while len(current) > size:
                chunks.append(current[:size])
                current = current[size - overlap :]
    if current:
        chunks.append(current)
    return chunks


def build_chunks() -> list[Chunk]:
    chunks: list[Chunk] = []
    cid = 0
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for piece in _chunk_text(text, settings.chunk_chars, settings.chunk_overlap):
            chunks.append(Chunk(text=piece, source=path.name, chunk_id=cid))
            cid += 1
    return chunks


def main() -> None:
    chunks = build_chunks()
    if not chunks:
        raise SystemExit(f"No knowledge documents found in {KNOWLEDGE_DIR}")

    embedder = get_embedder()
    vectors = embedder.embed([c.text for c in chunks])
    store = VectorStore(vectors, chunks)
    store.save(VECTORSTORE_DIR)
    print(f"Ingested {len(chunks)} chunks from {KNOWLEDGE_DIR.name}/ -> {VECTORSTORE_DIR}")


if __name__ == "__main__":
    main()
