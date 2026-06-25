"""Typed, fault-tolerant HTTP clients for the downstream services.

Every call is wrapped so a downstream failure becomes a `None` result plus a
logged warning rather than a 500 from the gateway. This is what lets the
`/diagnose` flow **degrade gracefully** — partial results beat a hard failure.
"""

from __future__ import annotations

import httpx
from flora_common import get_logger
from flora_common.schemas import (
    AgentRequest,
    AgentResponse,
    HealthPrediction,
    SpeciesPrediction,
)

from floragateway.config import settings

log = get_logger("floragateway.clients")


def _get_json(url: str) -> dict | None:
    try:
        r = httpx.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        log.warning(f"GET {url} failed: {exc}")
        return None


def downstream_health() -> dict:
    """Aggregate health of all three services for the gateway's /health."""
    return {
        "ml": _get_json(f"{settings.ml_url}/health"),
        "dl": _get_json(f"{settings.dl_url}/health"),
        "agent": _get_json(f"{settings.agent_url}/health"),
    }


def identify_species(image_bytes: bytes, filename: str, content_type: str) -> SpeciesPrediction | None:
    try:
        r = httpx.post(
            f"{settings.dl_url}/identify",
            files={"file": (filename, image_bytes, content_type)},
            timeout=settings.request_timeout,
        )
        r.raise_for_status()
        return SpeciesPrediction(**r.json())
    except Exception as exc:
        log.warning(f"DL identify failed: {exc}")
        return None


def predict_health(conditions: dict) -> HealthPrediction | None:
    try:
        r = httpx.post(
            f"{settings.ml_url}/predict", json=conditions, timeout=settings.request_timeout
        )
        r.raise_for_status()
        return HealthPrediction(**r.json())
    except Exception as exc:
        log.warning(f"ML predict failed: {exc}")
        return None


def ask_agent(message: str) -> AgentResponse | None:
    try:
        r = httpx.post(
            f"{settings.agent_url}/chat",
            json=AgentRequest(message=message).model_dump(),
            timeout=settings.request_timeout,
        )
        r.raise_for_status()
        return AgentResponse(**r.json())
    except Exception as exc:
        log.warning(f"Agent chat failed: {exc}")
        return None
