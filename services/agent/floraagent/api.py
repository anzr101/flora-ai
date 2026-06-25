"""FastAPI service for the botanical agent.

  GET  /health   liveness + whether a vector store and LLM key are present
  POST /chat     AgentRequest -> AgentResponse (grounded answer + citations)
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from flora_common import get_logger
from flora_common.schemas import AgentRequest, AgentResponse

from floraagent.agent import run_agent
from floraagent.config import VECTORSTORE_DIR, settings
from floraagent.vectorstore import VectorStore

log = get_logger("floraagent.api")
app = FastAPI(
    title="FloraAI · Agent Service",
    version="1.0.0",
    description="Agentic RAG botanical assistant (Claude + local embeddings).",
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "vectorstore_ready": VectorStore.exists(VECTORSTORE_DIR),
        "llm_enabled": bool(settings.anthropic_api_key),
        "model": settings.flora_agent_model,
    }


@app.post("/chat", response_model=AgentResponse)
def chat(req: AgentRequest) -> AgentResponse:
    if not VectorStore.exists(VECTORSTORE_DIR):
        raise HTTPException(503, "Knowledge base not ingested. Run `python -m floraagent.ingest`.")
    try:
        return run_agent(req)
    except Exception as exc:  # surface a clean error instead of a 500 stack trace
        log.exception("agent failure")
        raise HTTPException(500, f"Agent error: {exc}") from exc
