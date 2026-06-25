"""Gateway configuration — just the URLs of the downstream services."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewaySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FLORA_", env_file=".env", extra="ignore")

    ml_url: str = "http://localhost:8001"
    dl_url: str = "http://localhost:8002"
    agent_url: str = "http://localhost:8003"
    request_timeout: float = 30.0


settings = GatewaySettings()
