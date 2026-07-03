"""Gateway configuration — just the URLs of the downstream services."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewaySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FLORA_", env_file=".env", extra="ignore")

    ml_url: str = "http://localhost:8001"
    dl_url: str = "http://localhost:8002"
    agent_url: str = "http://localhost:8003"
    request_timeout: float = 30.0

    # Diagnosis history persistence. SQLite for zero-setup dev; in production
    # set FLORA_DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/flora
    database_url: str = "sqlite+aiosqlite:///./flora_gateway.db"


settings = GatewaySettings()
