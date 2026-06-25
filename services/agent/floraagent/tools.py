"""Tools the agent can call.

The agent is not just a chatbot over documents — it can take ACTIONS:
- `search_botanical_knowledge` → RAG retrieval over the knowledge base.
- `predict_plant_health` → calls the ML service (Module 1) for a structured
  health-risk prediction from sensor/care values.

Each tool exposes an Anthropic tool schema and a Python implementation. The agent
loop (agent.py) dispatches `tool_use` blocks here and feeds results back.
"""

from __future__ import annotations

import json

import httpx

from floraagent.config import settings
from floraagent.retriever import retrieve

# Citations accumulated during a single turn's tool calls (read by the agent).
LAST_CITATIONS: list[dict] = []


TOOL_SCHEMAS = [
    {
        "name": "search_botanical_knowledge",
        "description": (
            "Search the curated botanical knowledge base for care, watering, "
            "light, soil/pH, disease, pest, seasonal, or species information. "
            "Use this for any factual horticultural question before answering."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A focused search query, e.g. 'monstera yellow leaves overwatering'.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "predict_plant_health",
        "description": (
            "Predict a plant's health-risk class (healthy/at_risk/diseased) from "
            "structured environmental and care conditions using the ML model. "
            "Use when the user provides sensor readings or specific care values."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "temperature_c": {"type": "number"},
                "humidity_pct": {"type": "number"},
                "soil_moisture_pct": {"type": "number"},
                "light_hours": {"type": "number"},
                "soil_ph": {"type": "number"},
                "watering_freq_per_week": {"type": "number"},
                "fertilizer_freq_per_month": {"type": "number"},
                "plant_age_months": {"type": "number"},
            },
            "required": [
                "temperature_c",
                "humidity_pct",
                "soil_moisture_pct",
                "light_hours",
                "soil_ph",
                "watering_freq_per_week",
                "fertilizer_freq_per_month",
                "plant_age_months",
            ],
        },
    },
]


def _tool_search(query: str) -> str:
    hits = retrieve(query)
    for text, src, score in hits:
        LAST_CITATIONS.append(
            {"source": src, "snippet": text[:200].replace("\n", " ").strip()}
        )
    return "\n\n".join(f"[source: {src} | score={score:.2f}]\n{text}" for text, src, score in hits)


def _tool_predict_health(**conditions) -> str:
    try:
        resp = httpx.post(f"{settings.flora_ml_url}/predict", json=conditions, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return json.dumps(
            {
                "risk_label": data["risk_label"],
                "risk_score": data["risk_score"],
                "class_probabilities": data["class_probabilities"],
                "top_drivers": data.get("top_drivers", []),
            }
        )
    except Exception as exc:
        return f"ERROR: could not reach ML service ({exc}). Answer from general knowledge instead."


def execute_tool(name: str, tool_input: dict) -> str:
    """Dispatch a tool call by name; always returns a string for the model."""
    if name == "search_botanical_knowledge":
        return _tool_search(tool_input["query"])
    if name == "predict_plant_health":
        return _tool_predict_health(**tool_input)
    return f"ERROR: unknown tool '{name}'."
