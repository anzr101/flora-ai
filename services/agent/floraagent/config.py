"""Configuration for the agent service."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_ROOT = Path(__file__).resolve().parent.parent  # services/agent/
KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"
VECTORSTORE_DIR = SERVICE_ROOT / "vectorstore"


class AgentSettings(BaseSettings):
    # Reads ANTHROPIC_API_KEY, FLORA_AGENT_MODEL, FLORA_EMBEDDING_MODEL, etc.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    flora_agent_model: str = "claude-haiku-4-5"
    flora_embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Embedding backend: "fastembed" (real, ONNX) or "hash" (deterministic,
    # offline — used in tests/CI so we never hit the network).
    flora_embed_backend: str = "fastembed"

    # URLs of the sibling services the agent can call as tools.
    flora_ml_url: str = "http://localhost:8001"
    flora_dl_url: str = "http://localhost:8002"

    # Retrieval
    top_k: int = 4
    chunk_chars: int = 700
    chunk_overlap: int = 120
    max_tool_iterations: int = 4


settings = AgentSettings()
