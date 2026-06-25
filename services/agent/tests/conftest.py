"""Shared fixtures: force the offline hash embedder and build a temp vector store
so the agent tests never touch the network or download a model."""

from __future__ import annotations

import os

import pytest

# Must be set before any floraagent module reads settings.
os.environ["FLORA_EMBED_BACKEND"] = "hash"


@pytest.fixture(scope="session", autouse=True)
def _ingested_store(tmp_path_factory):
    from floraagent import config, ingest, retriever
    from floraagent.vectorstore import VectorStore

    store_dir = tmp_path_factory.mktemp("vectorstore")
    # Point the whole package at the temp store directory.
    config.VECTORSTORE_DIR = store_dir
    ingest.VECTORSTORE_DIR = store_dir
    retriever.VECTORSTORE_DIR = store_dir

    chunks = ingest.build_chunks()
    from floraagent.embeddings import get_embedder

    vectors = get_embedder().embed([c.text for c in chunks])
    VectorStore(vectors, chunks).save(store_dir)
    retriever._resources.cache_clear()
    yield store_dir
