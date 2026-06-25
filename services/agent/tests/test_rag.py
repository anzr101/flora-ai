"""Retrieval, tooling, and offline-agent tests (all offline via the hash backend)."""

from __future__ import annotations

from flora_common.schemas import AgentRequest

from floraagent import tools as tools_mod
from floraagent.agent import run_agent
from floraagent.eval import evaluate
from floraagent.retriever import retrieve


def test_chunks_were_ingested(_ingested_store):
    from floraagent.vectorstore import VectorStore

    store = VectorStore.load(_ingested_store)
    assert len(store) > 5  # several chunks across the KB


def test_retrieve_returns_sources_and_scores():
    hits = retrieve("how often to water a succulent", top_k=3)
    assert len(hits) == 3
    for text, source, score in hits:
        assert source.endswith(".md")
        assert isinstance(text, str) and text
        assert -1.0001 <= score <= 1.0001


def test_search_tool_populates_citations():
    tools_mod.LAST_CITATIONS.clear()
    out = tools_mod.execute_tool("search_botanical_knowledge", {"query": "spider mites"})
    assert isinstance(out, str) and out
    assert len(tools_mod.LAST_CITATIONS) > 0


def test_unknown_tool_is_handled():
    assert tools_mod.execute_tool("nope", {}).startswith("ERROR")


def test_offline_agent_fallback_grounds_in_retrieval(monkeypatch):
    # Force the no-LLM path and confirm we still return citations.
    monkeypatch.setattr("floraagent.agent.settings.anthropic_api_key", "", raising=False)
    resp = run_agent(AgentRequest(message="Why are my plant's leaves yellow?"))
    assert resp.citations
    assert "search_botanical_knowledge" in resp.tools_used


def test_eval_harness_runs_and_returns_metrics():
    results = evaluate(top_k=4)
    assert 0.0 <= results["hit_at_k"] <= 1.0
    assert 0.0 <= results["mrr"] <= 1.0
    assert results["n_questions"] == 11
